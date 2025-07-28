import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib import cm
import moviepy as mp

import os
import pyedflib
import math


'''
AN EARLY VERSION OF THE FUNCTION THAT I USED TO GET DATA
AND GENERATE A SPECTRAL ARRAY FOR PLOTTING.
'''


def get_data_from_array(file_names, start_frame):
    data = np.array([])
    sample_rate = 0.
    for file_name in file_names:
        signals, signal_headers, header = pyedflib.highlevel.read_edf(file_name)
        sample_rate = signal_headers[0]['sample_rate']
        data = np.concatenate((data, signals[0]))  # indexed by channel number

    T_fast = 2.5  # fast time period in seconds
    T_slow = 20 * 60
    num_samples = int(math.floor(sample_rate * T_fast))
    t = np.array([i / sample_rate for i in range(num_samples)])
    f = np.fft.fftshift(np.fft.fftfreq(len(t), d=1 / sample_rate))

    max_plot_frequency = 40.
    num_frequency_points = 0
    for f_sample in f:
        if 0. <= f_sample <= max_plot_frequency:
            num_frequency_points += 1

    empty_sed_array = np.array([np.zeros(num_frequency_points) - 100 for i in range(int(T_slow / T_fast))])


    start_sample = num_samples * start_frame
    for i in range(int(T_slow / T_fast)):
        y = np.array(data[start_sample + (num_samples * i):start_sample + (num_samples * (i + 1))])
        y_f_linear = abs(np.fft.fftshift(np.fft.fft(y)))
        y_f = 20 * np.log10(y_f_linear)

        empty_sed_array = np.roll(empty_sed_array, -1, axis=0)
        empty_sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(empty_sed_array[0])])

    return empty_sed_array.transpose()


def get_data(file_name, start_frame):
    # file_name = 'data/EEG_240505_084705.edf'
    signals, signal_headers, header = pyedflib.highlevel.read_edf(file_name)
    sample_rate = signal_headers[0]['sample_rate']
    data = signals[0]  # indexed by channel number

    T_fast = 2.5  # fast time period in seconds
    T_slow = 20 * 60
    num_samples = int(math.floor(sample_rate * T_fast))
    t = np.array([i / sample_rate for i in range(num_samples)])
    f = np.fft.fftshift(np.fft.fftfreq(len(t), d=1 / sample_rate))

    max_plot_frequency = 40.
    num_frequency_points = 0
    for f_sample in f:
        if 0. <= f_sample <= max_plot_frequency:
            num_frequency_points += 1

    empty_sed_array = np.array([np.zeros(num_frequency_points) - 100 for i in range(int(T_slow / T_fast))])


    start_sample = num_samples * start_frame
    for i in range(int(T_slow / T_fast)):
        y = np.array(data[start_sample + (num_samples * i):start_sample + (num_samples * (i + 1))])
        y_f_linear = abs(np.fft.fftshift(np.fft.fft(y)))
        y_f = 20 * np.log10(y_f_linear)

        empty_sed_array = np.roll(empty_sed_array, -1, axis=0)
        empty_sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(empty_sed_array[0])])

    return empty_sed_array.transpose()


def main():
    file_name = '/home/dan/Documents/data/lambert_eeg_data/Root_2000026958_20250125_155127/EEG_250125_172109.edf'
    file_names = ['/home/dan/Documents/data/lambert_eeg_data/Root_2000026958_20250125_155127/EEG_250125_172109.edf', '/home/dan/Documents/data/lambert_eeg_data/Root_2000026958_20250125_155127/EEG_250125_175103.edf']
    signals, signal_headers, header = pyedflib.highlevel.read_edf(file_name)
    sample_rate = signal_headers[0]['sample_rate']

    T_fast = 2.5  # fast time period in seconds
    T_slow = 20 * 60
    num_samples = int(math.floor(sample_rate * T_fast))
    t = np.array([i / sample_rate for i in range(num_samples)])
    f = np.fft.fftshift(np.fft.fftfreq(len(t), d=1 / sample_rate))

    max_plot_frequency = 40.
    num_frequency_points = 0
    for f_sample in f:
        if 0. <= f_sample <= max_plot_frequency:
            num_frequency_points += 1
    min_db_power = 30
    max_db_power = 60
    font_size = 18

    plt.figure(figsize=(16, 9), dpi=250)
    ax = plt.subplot(1, 1, 1)

    # empty_sed_array = np.array([np.zeros(num_frequency_points) - 100 for i in range(int(T_slow / T_fast))])
    frame_num = 300
    empty_sed_array = get_data_from_array(file_names, frame_num)
    # empty_sed_array = get_data(file_name, frame_num)
    sed_plot = plt.imshow(empty_sed_array, cmap='jet',
                            vmin=min_db_power,
                            vmax=max_db_power,
                            aspect='auto', interpolation='bilinear',
                            extent=[-int(T_slow / 60), 0, max_plot_frequency, 0])
    cbar = plt.colorbar()
    cbar.set_label('Power (dB)', fontsize=font_size)
    ax.set_yticks(np.array([-0. + i*max_plot_frequency/4 for i in range(5)]))
    ax.set_yticklabels(np.arange(max_plot_frequency, -0.5,
                                    -int(max_plot_frequency / 4)))
    plt.xlabel('Time (min)', fontsize=font_size)
    plt.ylabel('Frequency (Hz)', fontsize=font_size)
    plt.tight_layout()

    plt.savefig('figures/N20_spectrogram.png')
    plt.show()


if  __name__ == '__main__':
    main()
