import pyedflib
import os
import numpy as np
import math

class EEGArray:
    data = [np.array([]) for i in range(4)]

    def __init__(self, inputFiles):
        self.load_array_of_data(inputFiles)
        self.totalNumSamples = len(self.data[0])
        self.totalTime = math.floor(self.totalNumSamples / self.sampleRate)
        self.inputFiles = inputFiles

    
    def load_array_of_data(self, file_array):
        self.data.clear()

        if type(file_array) is str:
            file_array = file_array.split(';')
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
