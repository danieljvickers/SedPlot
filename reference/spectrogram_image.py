import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib import cm
import moviepy as mp

import os
import pyedflib
import math
from scipy import ndimage
from stl import mesh

from get_data import get_data

'''
CREATES A 3D ARRAY OF THE DATA AS A SPECTROGRAM AND
GENERATES AN IMAGE FROM A SPECIFIC VIEW ANGLE.
'''


def main():
    file_name = 'data/EEG_240505_084705.edf'
    start_frame = 101
    signals, signal_headers, header = pyedflib.highlevel.read_edf(file_name)
    sample_rate = signal_headers[0]['sample_rate']
    data = get_data(file_name, start_frame)

    offset = 30
    data = data - 30
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] < 0:
                data[i][j] = 0.
    
    data = np.flip(data, 0)
    # data = np.flip(data, 1)

    # filter_size = 5
    # data = ndimage.median_filter(data, size=(filter_size, 5*filter_size))

    T_fast = 2.5  # fast time period in seconds
    T_slow = 20 * 60
    t = np.linspace(0, T_slow, int(T_slow / T_fast)) / 60.

    f_max = 40
    f = np.linspace(0, f_max, int(f_max * T_fast))
    T, F = np.meshgrid(t, f)

    min_db_power = 0
    max_db_power = 30
    

    # Create vertices
    vertices = np.zeros((len(t) * len(f), 3))
    vertices[:, 0] = T.ravel()
    vertices[:, 1] = F.ravel()
    vertices[:, 2] = data.ravel()

    ax = plt.figure(figsize=(10, 10), dpi=250).add_subplot(projection='3d')
    # ax.set_box_aspect((9, 16, 5))
    ax.plot_trisurf(T.ravel(), F.ravel(), data.ravel(), 
                    cmap='jet',
                    vmin=min_db_power,
                    vmax=max_db_power,
                    lw=0)
    plt.xlabel('time (min)', fontsize=18)
    plt.ylabel('frequency (Hz)', fontsize=18)
    ax.set_zlabel('power (dB)', fontsize=18)

    ax.view_init(elev=30, azim=45)
    plt.savefig('figures/height_map_nofilter.png')
    plt.show()


if __name__ == '__main__':
    main()