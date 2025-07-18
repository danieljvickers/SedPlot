import pyedflib
import os
import numpy as np
import math

class EEGArray:
    data = []

    def __init__(self, inputFiles):
        self.load_array_of_data(inputFiles)
        self.totalNumSamples = len(self.data[0])
        self.totalTime = math.floor(self.totalNumSamples / self.sampleRate)
        self.inputFiles = inputFiles

    
    def load_array_of_data(self, file_array):
        self.data.clear()

        if type(file_array) is str:
            assert os.path.exists(file_array), f"ERROR :: The file '{file_array} does not exists.'"  # check that the file exists before we open it
            try:
                signals, signal_headers, header = pyedflib.highlevel.read_edf(file_array)  # read in the data with the pyedf library
                self.sampleRate = signal_headers[0]['sample_rate']  # fetch the sample rate
                for channel_number in range(len(signals)):
                    self.data.insert(signals[channel_number])  # get out the data from each channel and store it into the array
            except:
                print(f"Unable to load file: {file}")

        elif type(file_array) is list:
            file_array = file_array.sort()  # required for linux compatability. TODO :: find a better way to handle this in case someone wants to order this on their own
            for file in file_array:
                assert os.path.exists(file), f"ERROR :: The file '{file} does not exists.'"
                try:
                    signals, signal_headers, header = pyedflib.highlevel.read_edf(file)
                    self.sampleRate = signal_headers[0]['sample_rate']
                    if len(self.data) < len(signals):
                        for i in range(len(signals)):
                            self.data.append(np.array([]))
                    for channel_number in range(len(signals)):
                        self.data[channel_number] = np.concatenate((self.data, signals[channel_number]))
                except:
                    print(f"Unable to load file: {file}")

        else:
            raise "Object passed into `load_array_of_data` is not a string or array. Exiting."