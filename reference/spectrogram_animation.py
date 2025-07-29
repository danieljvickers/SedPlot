import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib import cm
import moviepy as mp

import os
import pyedflib
import math
from scipy import ndimage

from get_data import get_data

'''
GENERATES A SPECTROGRAM ANIMATION. RENDERES A 3D ARRAY OF
THE DATA, COLORS IT, AND CRTEATES A GIF WATCHING FROM MANY
DIFFERENT ANGLES
'''

script = [
    {
        "function":"rotate",
        "begin": 0,
        "end": 120,
        "start": np.array([30., 45.]),
        "stop": np.array([89.9, -89.9])
    },
    {
        "function":"rotate",
        "begin": 180,
        "end": 300,
        "start": np.array([89.9, -89.9]),
        "stop": np.array([30., 45.])
    },
    {
        "function": "pause",
        "begin": 301,
        "end": 360
    }
]


def rotate_to_angle(ax, i, window, start_angle, end_angle):
    i_frac = i / window
    current_angle = start_angle * (1. - i_frac) + i_frac * end_angle
    ax.view_init(elev=current_angle[0], azim=current_angle[1])


def main():
    def run_animation(i):
        for scene in script:
            if scene["begin"] <= i <= scene['end']:
                if scene['function'] == 'rotate':
                    window = scene['end'] - scene['begin']
                    rotate_to_angle(ax, i - scene['begin'], window, scene['start'], scene['stop'])
                break

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
    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_subplot(projection='3d')
    # ax.set_box_aspect((9, 16, 5))
    '''ax.plot_surface(T, F, data, 
                    cmap='jet',
                    vmin=min_db_power,
                    vmax=max_db_power,
                    cstride=100,
                    rstride=1,
                    lw=0)'''
    ax.plot_trisurf(T.ravel(), F.ravel(), data.ravel(), 
                    cmap='jet',
                    vmin=min_db_power,
                    vmax=max_db_power,
                    lw=0)
    plt.xlabel('time (min)')
    plt.ylabel('frequency (Hz)')
    ax.set_zlabel('power (dB)')

    ax.view_init(elev=30, azim=45)
    ani = animation.FuncAnimation(fig, run_animation, repeat=True, frames=script[-1]["end"]+1, interval=30)
    writer = animation.PillowWriter(fps=30, metadata=dict(artist='Daniel J. Vickers'), bitrate=1800)
    ani.save('figures/height_map_lowrez_nofilter.gif', writer=writer)
    # plt.show()


if __name__ == '__main__':
    main()
