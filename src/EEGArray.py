import pyedflib
import os
import numpy as np
import math

class EEGArray:
    data = [np.array([]) for i in range(4)]
    sampleRate = -1.

    def __init__(self, inputFiles):
        self.load_array_of_data(inputFiles)
        self.totalNumSamples = len(self.data[0])
        self.totalTime = math.floor(self.totalNumSamples / self.sampleRate)
        self.inputFiles = inputFiles

    
    def load_array_of_data(self, file_array):
        self.data.clear()

        if type(file_array) is str:
            file_array = file_array.split(';')
        elif type(file_array) == tuple:
            file_array = list(file_array)
        elif type(file_array) is not list:
            raise "Object passed into `load_array_of_data` is not a string or array. Exiting."
        if file_array[-1] == '':
            file_array.pop(-1)

        file_array.sort()  # required for linux compatability. TODO :: find a better way to handle this in case someone wants to order this on their own
        for file in file_array:
            assert os.path.exists(file), f"ERROR :: The file {file} does not exists."
            try:
                signals, signal_headers, header = pyedflib.highlevel.read_edf(file)
                self.sampleRate = signal_headers[0]['sample_rate']
                if len(self.data) < len(signals):
                    for i in range(len(signals)):
                        self.data.append(np.array([]))
                for channel_number in range(len(signals)):
                    self.data[channel_number] = np.concatenate((self.data[channel_number], signals[channel_number]))
            except:
                print(f"Unable to load file: {file}")
    
    
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
            y_f = 20 * np.log10(y_f_linear)

            empty_sed_array = np.roll(empty_sed_array, -1, axis=0)
            empty_sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(empty_sed_array[0])])

        return empty_sed_array.transpose()