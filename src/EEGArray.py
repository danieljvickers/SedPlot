import pyedflib
import os
import numpy as np
import math


class EEGLoadError(Exception):
    """Raised when none of the available readers can extract data from a file."""
    pass


class EEGArray:

    def __init__(self, inputFiles):
        self.data = []
        self.sampleRate = -1.
        self.data_is_safe = True
        self.load_warnings = []  # human readable notes about anything odd during the load
        self.load_array_of_data(inputFiles)
        self.totalNumSamples = len(self.data[0])
        self.totalTime = math.floor(self.totalNumSamples / self.sampleRate)
        self.inputFiles = inputFiles


    def load_array_of_data(self, file_array):
        self.data = []

        if type(file_array) is str:
            file_array = file_array.split(';')
        elif type(file_array) == tuple:
            file_array = list(file_array)
        elif type(file_array) is not list:
            raise TypeError("Object passed into `load_array_of_data` is not a string or array. Exiting.")
        file_array = [file for file in file_array if file != '']

        file_array.sort()  # required for linux compatability. TODO :: find a better way to handle this in case someone wants to order this on their own
        for file in file_array:
            assert os.path.exists(file), f"ERROR :: The file {file} does not exists."
            try:
                channels, sample_rate = self.read_edf_with_fallbacks(file)
            except EEGLoadError as error:
                print(f"Unable to load file: {file} ({error})")
                self.warn(f"Unable to load {os.path.basename(file)}.")
                continue

            if self.sampleRate > 0 and sample_rate != self.sampleRate:
                self.warn(f"{os.path.basename(file)} samples at {sample_rate} Hz, "
                          f"but earlier data samples at {self.sampleRate} Hz.")
            self.sampleRate = sample_rate

            if not self.data:
                self.data = [np.array([]) for _ in channels]
            elif len(channels) != len(self.data):
                self.warn(f"{os.path.basename(file)} holds {len(channels)} channels, "
                          f"but earlier data holds {len(self.data)}.")
                # only the channels present in every file can be concatenated safely
                while len(self.data) < len(channels):
                    self.data.append(np.array([]))

            for channel_number in range(min(len(channels), len(self.data))):
                self.data[channel_number] = np.concatenate((self.data[channel_number], channels[channel_number]))

        if not self.data or len(self.data[0]) == 0:
            raise EEGLoadError("No usable data could be read from the requested file(s).")

        # channels of unequal length break the frame arithmetic, so trim them back to the shortest
        shortest_channel = min(len(channel) for channel in self.data)
        if any(len(channel) != shortest_channel for channel in self.data):
            self.warn("Channels hold differing numbers of samples. Trimming to the shortest channel.")
            self.data = [channel[:shortest_channel] for channel in self.data]

        # renormalize
        for i in range(len(self.data)):
            self.data[i] = self.data[i] * 1e-3


    def warn(self, message):
        """Record a problem found while loading and mark the data set as suspect."""
        self.data_is_safe = False
        if message not in self.load_warnings:
            self.load_warnings.append(message)


    def read_edf_with_fallbacks(self, file):
        """Read a single EDF/BDF file into a list of channels plus its sample rate.

        Readers are tried from the most to the least strict. `pyedflib.highlevel` refuses
        files with a damaged header, an unreadable annotation channel or a truncated final
        data record, all of which are common in recordings that were cut short, so the
        lower level readers below salvage what data such a file still holds.
        """
        readers = [
            ("pyedflib.highlevel", self.read_edf_highlevel),
            ("pyedflib.EdfReader", self.read_edf_channelwise),
            ("raw EDF parser", self.read_edf_raw),
        ]

        failures = []
        for reader_name, reader in readers:
            try:
                channels, sample_rate = reader(file)
            except Exception as error:  # any reader may fail in its own way
                failures.append(f"{reader_name}: {error}")
                continue

            if not channels or not len(channels[0]) or not sample_rate or sample_rate <= 0:
                failures.append(f"{reader_name}: no usable signals found")
                continue

            if failures:
                self.warn(f"{os.path.basename(file)} could not be read normally. "
                          f"Recovered with the {reader_name} fallback.")
                print(f"Fell back to the {reader_name} reader for {file}. "
                      f"Earlier attempts failed with -- " + "; ".join(failures))
            return [np.asarray(channel, dtype=float) for channel in channels], float(sample_rate)

        raise EEGLoadError("; ".join(failures))


    @staticmethod
    def read_edf_highlevel(file):
        """Primary reader. Validates the whole file and reads every channel at once."""
        signals, signal_headers, _ = pyedflib.highlevel.read_edf(file)
        sample_rate = pyedflib.highlevel._get_sample_frequency(signal_headers[0])
        return [np.asarray(signal, dtype=float) for signal in signals], sample_rate


    @staticmethod
    def read_edf_channelwise(file):
        """First fallback. Skips annotations and reads one channel at a time.

        Annotation channels are a common reason for an otherwise healthy recording to be
        rejected, and reading channel by channel means a single unreadable channel costs
        only that channel instead of the whole recording.

        Note that pyedflib's REPAIR_FILE_SIZE_IF_WRONG mode is deliberately not used here.
        It writes to the file being opened, and on a file that is not really an EDF it
        truncates that file to zero bytes, which would destroy the user's recording.
        """
        # a header that overstates its length makes pyedflib pad the tail of every channel
        # with fabricated samples, so cap each read at what the file on disk can hold
        try:
            layout = EEGArray.parse_edf_layout(file)
            sample_caps = [layout['records_on_disk'] * samples for samples in layout['samples_per_record']]
        except Exception:
            sample_caps = None

        reader = None
        open_errors = []
        for file_size_mode in (pyedflib.CHECK_FILE_SIZE, pyedflib.DO_NOT_CHECK_FILE_SIZE):
            if file_size_mode == pyedflib.DO_NOT_CHECK_FILE_SIZE and sample_caps is None:
                # without a cap of our own there is nothing left to stop a bad header from
                # inventing samples, so leave this file to the raw parser instead
                open_errors.append("file size check cannot be skipped without a readable header")
                continue
            try:
                reader = pyedflib.EdfReader(file, pyedflib.DO_NOT_READ_ANNOTATIONS, file_size_mode)
                break
            except Exception as error:
                open_errors.append(str(error))
        if reader is None:
            raise EEGLoadError("; ".join(open_errors))

        try:
            signal_headers = reader.getSignalHeaders()
            sample_rate = pyedflib.highlevel._get_sample_frequency(signal_headers[0])
            channels = []
            for channel_number in range(reader.signals_in_file):
                available = reader.getNSamples()[channel_number]
                if sample_caps is not None and channel_number < len(sample_caps):
                    available = min(available, sample_caps[channel_number])
                try:
                    signal = reader.readSignal(channel_number, 0, available)
                except Exception:
                    signal = EEGArray.read_signal_in_chunks(reader, channel_number, available)
                channels.append(np.asarray(signal, dtype=float))
        finally:
            reader.close()

        # a channel that fell short of the others would desynchronise the time axis
        channels = [channel for channel in channels if len(channel)]
        if not channels:
            raise EEGLoadError("every channel failed to read")
        shortest_channel = min(len(channel) for channel in channels)
        return [channel[:shortest_channel] for channel in channels], sample_rate


    @staticmethod
    def read_signal_in_chunks(reader, channel_number, total_samples, chunk_size=4096):
        """Read as much of a channel as the file will give up before the first failure."""
        collected = []
        start = 0
        while start < total_samples:
            n = min(chunk_size, total_samples - start)
            try:
                collected.append(reader.readSignal(channel_number, start, n))
            except Exception:
                break
            start += n
        if not collected:
            return np.array([])
        return np.concatenate(collected)


    @staticmethod
    def parse_edf_layout(file):
        """Read the EDF/BDF header by hand and describe where the samples sit on disk.

        This trusts nothing beyond the header fields it needs, so it also works for the
        files pyedflib rejects outright. `records_on_disk` is derived from the real file
        size rather than the declared record count, which is what makes it a useful sanity
        check on a header that overstates how much data the file contains.
        """
        file_size = os.path.getsize(file)
        with open(file, 'rb') as handle:
            fixed_header = handle.read(256)
            if len(fixed_header) < 256:
                raise EEGLoadError("file is shorter than a single EDF header")

            is_bdf = fixed_header[0:1] == b'\xff'
            sample_width = 3 if is_bdf else 2

            # the header size and record count are both recoverable from the file size, so a
            # damaged value there is not worth refusing the file over
            header_bytes = EEGArray.parse_header_number(fixed_header[184:192], int, "header size", default=0)
            declared_records = EEGArray.parse_header_number(fixed_header[236:244], int, "record count", default=-1)
            record_duration = EEGArray.parse_header_number(fixed_header[244:252], float, "record duration")
            num_signals = EEGArray.parse_header_number(fixed_header[252:256], int, "signal count")

            if num_signals <= 0:
                raise EEGLoadError("header declares no signals")
            if record_duration <= 0:
                raise EEGLoadError("header declares a non-positive record duration")

            signal_header_bytes = handle.read(256 * num_signals)
            if len(signal_header_bytes) < 256 * num_signals:
                raise EEGLoadError("file ends inside the signal headers")

            # each field of the signal header is written for every signal in turn, so the
            # block starts with all the labels, then all the transducers, and so on
            def header_field(bytes_per_signal_before, field_width):
                """Pull one per-signal field out of the block written field-major."""
                start = bytes_per_signal_before * num_signals
                return [signal_header_bytes[start + i * field_width:start + (i + 1) * field_width]
                        for i in range(num_signals)]

            # 16 label + 80 transducer + 8 dimension = 104 bytes per signal ahead of the ranges
            physical_min = [EEGArray.parse_header_number(field, float, "physical minimum")
                            for field in header_field(104, 8)]
            physical_max = [EEGArray.parse_header_number(field, float, "physical maximum")
                            for field in header_field(112, 8)]
            digital_min = [EEGArray.parse_header_number(field, float, "digital minimum")
                           for field in header_field(120, 8)]
            digital_max = [EEGArray.parse_header_number(field, float, "digital maximum")
                           for field in header_field(128, 8)]
            # the sample count sits after the 80 byte prefilter block
            samples_per_record = [EEGArray.parse_header_number(field, int, "samples per record")
                                  for field in header_field(216, 8)]

            if min(samples_per_record) < 0 or max(samples_per_record) == 0:
                raise EEGLoadError("header declares no samples per data record")

        if header_bytes <= 0 or header_bytes > file_size:
            header_bytes = 256 * (num_signals + 1)
        record_bytes = sum(samples_per_record) * sample_width
        records_on_disk = (file_size - header_bytes) // record_bytes
        if records_on_disk <= 0:
            raise EEGLoadError("file holds no complete data records")

        return {
            'header_bytes': header_bytes,
            'record_bytes': record_bytes,
            'record_duration': record_duration,
            'sample_width': sample_width,
            'samples_per_record': samples_per_record,
            'num_signals': num_signals,
            'declared_records': declared_records,
            'records_on_disk': records_on_disk,
            'physical_min': physical_min,
            'physical_max': physical_max,
            'digital_min': digital_min,
            'digital_max': digital_max,
        }


    @staticmethod
    def read_edf_raw(file):
        """Last resort. Reads the sample blocks straight off disk using the parsed layout.

        This ignores every consistency field pyedflib validates, so it still returns data
        from a file whose header claims the wrong record count or that was truncated
        partway through a data record.
        """
        layout = EEGArray.parse_edf_layout(file)
        samples_per_record = layout['samples_per_record']
        declared_records = layout['declared_records']
        num_records = layout['records_on_disk']
        if declared_records > 0:
            num_records = min(declared_records, num_records)

        with open(file, 'rb') as handle:
            handle.seek(layout['header_bytes'])
            raw_samples = handle.read(num_records * layout['record_bytes'])

        digital = EEGArray.decode_samples(raw_samples, layout['sample_width'])
        digital = digital.reshape(num_records, sum(samples_per_record))

        channels = []
        offset = 0
        for channel_number in range(layout['num_signals']):
            width = samples_per_record[channel_number]
            channel = digital[:, offset:offset + width].reshape(-1).astype(float)
            offset += width

            digital_span = layout['digital_max'][channel_number] - layout['digital_min'][channel_number]
            if digital_span != 0:
                gain = (layout['physical_max'][channel_number] - layout['physical_min'][channel_number]) / digital_span
                channel = (channel - layout['digital_min'][channel_number]) * gain + layout['physical_min'][channel_number]
            channels.append(channel)

        sample_rate = max(samples_per_record) / layout['record_duration']
        return channels, sample_rate


    @staticmethod
    def decode_samples(raw_samples, sample_width):
        """Turn the packed little endian sample block into signed integers."""
        if sample_width == 2:
            return np.frombuffer(raw_samples, dtype='<i2')
        # BDF stores 24 bit samples, which numpy has no dtype for, so sign extend by hand
        as_bytes = np.frombuffer(raw_samples, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        values = as_bytes[:, 0] | (as_bytes[:, 1] << 8) | (as_bytes[:, 2] << 16)
        return np.where(values >= 1 << 23, values - (1 << 24), values)


    @staticmethod
    def parse_header_number(field, cast, field_name, default=None):
        """EDF header numbers are ASCII, space padded, and occasionally blank or damaged.

        A `default` marks a field the caller can do without. Without one an unreadable
        field aborts the parse, since guessing at it would silently distort the signal.
        """
        text = field.decode('ascii', errors='ignore').strip()
        try:
            if text == '':
                raise ValueError("blank")
            return cast(float(text)) if cast is int else cast(text)
        except ValueError:
            if default is not None:
                return default
            raise EEGLoadError(f"header field for {field_name} is unreadable: {text!r}")


    def get_end_frame_number(self, num_samples):
        return math.floor(len(self.data[0]) / num_samples) - 1


    def get_dsa_frame(self, T_fast, T_slow, max_plot_frequency, start_time_seconds, channel_number=0):
        assert start_time_seconds >= 0,  "Requested start time predates the start of the file."
        num_samples = int(math.floor(self.sampleRate * T_fast))  # samples added in a single frame
        num_image_frames = int(T_slow / T_fast)
        f = np.fft.fftshift(np.fft.fftfreq(num_samples, d=1 / self.sampleRate))

        num_frequency_points = 0
        for f_sample in f:
            if 0. <= f_sample <= max_plot_frequency:
                num_frequency_points += 1 # manually count the number of points. # TODO :: There is a nice math way to compute this in a single line based upon the num_samples

        empty_sed_array = np.array([np.zeros(num_frequency_points) - 100. for i in range(num_image_frames)])
        processing_data = np.concatenate((np.ones(num_image_frames * num_samples) * 1e-10, self.data[channel_number]))  # concatenate zeros to allow for begining generatino as well

        start_frame = math.floor(start_time_seconds * self.sampleRate / num_samples)
        max_frame = math.floor(self.totalNumSamples / num_samples) + num_image_frames
        assert max_frame >= num_image_frames, "Not enough data loaded in to create the requested image. Consider reducing the input slow time."
        start_frame = min(start_frame, max_frame - num_image_frames)

        for i in range(start_frame, start_frame+num_image_frames):
            y = np.array(processing_data[num_samples * i:num_samples * (i + 1)])
            y_f_linear = abs(np.fft.fftshift(np.fft.fft(y)))

            # convert the frequency-domain data to dB and replace 0s with small numbers that will not conver to NaNs
            for i in range(len(y_f_linear)):
                if y_f_linear[i] == 0.:
                    y_f_linear[i] = 1e-100            
            y_f = 20 * np.log10(y_f_linear)

            empty_sed_array = np.roll(empty_sed_array, -1, axis=0)
            empty_sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(empty_sed_array[0])])

        return empty_sed_array.transpose()