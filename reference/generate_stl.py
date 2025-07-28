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
    data = np.flip(data, 1)

    filter_size = 5
    data = ndimage.median_filter(data, size=(filter_size, 5*filter_size))
    rows, cols = data.shape

    T_fast = 2.5  # fast time period in seconds
    T_slow = 20 * 60
    t = np.linspace(0, T_slow, int(T_slow / T_fast)) / 60.

    f_max = 40
    f = np.linspace(0, f_max, int(f_max * T_fast))
    T, F = np.meshgrid(t, f)

    # Define desired physical dimensions (in mm)
    desired_width = 500.0  # Width in mm (x-axis)
    desired_depth = 50.0  # Depth in mm (y-axis)
    desired_height = 10.0  # Height in mm (z-axis)

    scale = 7
    desired_width *= scale
    desired_depth *= scale
    desired_height *= scale

    # Scale the coordinates to match the desired dimensions
    x_scaled = T * (desired_width / (cols - 1))
    y_scaled = F * (desired_depth / (rows - 1))
    z_scaled = data * (desired_height / data.max())
    

    # Create vertices
    vertices = np.zeros((len(t) * len(f), 3))
    vertices[:, 0] = x_scaled.ravel()
    vertices[:, 1] = y_scaled.ravel()
    vertices[:, 2] = z_scaled.ravel()

    # Create faces (triangular mesh)
    faces = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            # Define corners of the rectangle
            p1 = i * cols + j
            p2 = p1 + 1
            p3 = p1 + cols
            p4 = p3 + 1
            # Create two triangles
            faces.append([p1, p2, p3])
            faces.append([p2, p4, p3])
    faces = np.array(faces)

    # Create the mesh
    terrain_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            terrain_mesh.vectors[i][j] = vertices[f[j], :]

    # Calculate face colors based on average height
    for i, f in enumerate(faces):
        # Get the average height of the face
        avg_height = vertices[f, 2].mean()  # Z-coordinates of the face vertices
        # Normalize height to [0, 1]
        norm_height = avg_height / desired_height
        # Map to a 15-bit RGB color (5 bits per channel)
        r = 0 # int(norm_height * 31)  # Red channel (5 bits)
        g = 0 # int((1 - norm_height) * 31)  # Green channel (5 bits)
        b = 31 # int((norm_height * 0.5) * 31)  # Blue channel (5 bits)
        # Combine into a single 16-bit attribute
        color = (r << 10) | (g << 5) | b
        # Assign the color to the face
        terrain_mesh.attr[i] = color

    # Save to STL
    terrain_mesh.save('figures/eeg.stl')


if __name__ == '__main__':
    main()