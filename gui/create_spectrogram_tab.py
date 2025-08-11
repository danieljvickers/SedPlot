# GUI Imports
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilenames, asksaveasfilename

# system importes
import os
import platform
import sys
import shutil
import subprocess

TK_WIDTH = 75

def create_spectrogram_tab(renderer, progress_object, root, start_time_var):
    def submit_spectrogram():
        do_manual_angles = False
        renderer.graphicsSettings.frequencyDomainParameters.min_db_power = 20
        renderer.graphicsSettings.frequencyDomainParameters.max_db_power = 65
        
        file_ending = renderer.get_ouput_file_ending()
        if file_ending in ('mp4', 'gif'):
            if do_manual_angles:
                pass
            else:
                pass # renderer.create_spectrogram_animation()
        elif file_ending in ('png', 'jpg', 'pdf', 'svg'):
            if do_manual_angles:
                pass
            else:
                angle = (start_az_var.get(), start_el_var.get())
                renderer.create_spectrogram_image(start_time_var.get(), angle) 

        pass

    row_counter = 0

    # variables for the starting view angle
    start_az_var = tk.DoubleVar(root, value=30)
    start_az_label = tk.Label(root, text='Start Angle Azimuth (degrees)', font=('calibre', 10, 'bold'))
    start_az_entry = tk.Entry(root, textvariable=start_az_var)
    start_el_var = tk.DoubleVar(root, value=45)
    start_el_label = tk.Label(root, text='Start Angle Elevation (degrees)', font=('calibre', 10, 'bold'))
    start_el_entry = tk.Entry(root, textvariable=start_el_var)
    start_az_label.grid(row=row_counter, column=0)
    start_az_entry.grid(row=row_counter, column=1)
    start_el_label.grid(row=row_counter, column=2)
    start_el_entry.grid(row=row_counter, column=3)
    row_counter += 1

    end_az_var = tk.DoubleVar(root, value=0)
    end_az_label = tk.Label(root, text='End Angle Azimuth (degrees)', font=('calibre', 10, 'bold'))
    end_az_entry = tk.Entry(root, textvariable=end_az_var)
    end_el_var = tk.DoubleVar(root, value=0)
    end_el_label = tk.Label(root, text='End Angle Elevation (degrees)', font=('calibre', 10, 'bold'))
    end_el_entry = tk.Entry(root, textvariable=end_el_var)
    end_az_label.grid(row=row_counter, column=0)
    end_az_entry.grid(row=row_counter, column=1)
    end_el_label.grid(row=row_counter, column=2)
    end_el_entry.grid(row=row_counter, column=3)
    row_counter += 1


    spectrogram_button = tk.Button(root, text="Generate 3D Spectrogram", command=submit_spectrogram)
    spectrogram_button.grid(row=row_counter, column=0,
                   columnspan=4, pady=10, sticky="ew")

