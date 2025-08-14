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

# math
import numpy as np

TK_WIDTH = 75

def create_spectrogram_tab(renderer, progress_object, root, start_time_var):    
    def submit_spectrogram():
        do_manual_angles = False
        renderer.graphicsSettings.frequencyDomainParameters.min_db_power = 20
        renderer.graphicsSettings.frequencyDomainParameters.max_db_power = 65
        
        file_ending = renderer.get_ouput_file_ending()
        start_angle = (start_el_var.get(), start_az_var.get())
        if file_ending in ('mp4', 'gif'):
            end_angle = (end_el_var.get(), end_az_var.get())
            script = get_spectrogram_animation_script(start_angle, end_angle, reset=(not dont_angle_reset_var.get()))
            renderer.create_spectrogram_animation(start_time_var.get(), script,
                tk_progress_bar=progress_object, height_floor=height_var.get())
        elif file_ending in ('png', 'jpg', 'pdf', 'svg'):
            renderer.create_spectrogram_image(start_time_var.get(), start_angle, height_floor=height_var.get()) 

        pass


    def get_spectrogram_animation_script(start_angle, stop_angle, reset=True):
        script = [
            {
                "function":"rotate",
                "begin": 0,
                "end": 120,
                "start": np.array(start_angle),
                "stop": np.array(stop_angle)
            }
        ]
        if reset:
            script = script + [
                {
                    "function":"rotate",
                    "begin": 180,
                    "end": 300,
                    "start": np.array(stop_angle),
                    "stop": np.array(start_angle)
                },
                {
                    "function": "pause",
                    "begin": 301,
                    "end": 360
                }
            ]
        return script

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

    end_az_var = tk.DoubleVar(root, value=-89.9)
    end_az_label = tk.Label(root, text='End Angle Azimuth (degrees)', font=('calibre', 10, 'bold'))
    end_az_entry = tk.Entry(root, textvariable=end_az_var)
    end_el_var = tk.DoubleVar(root, value=89.9)
    end_el_label = tk.Label(root, text='End Angle Elevation (degrees)', font=('calibre', 10, 'bold'))
    end_el_entry = tk.Entry(root, textvariable=end_el_var)
    end_az_label.grid(row=row_counter, column=0)
    end_az_entry.grid(row=row_counter, column=1)
    end_el_label.grid(row=row_counter, column=2)
    end_el_entry.grid(row=row_counter, column=3)
    row_counter += 1

    # Variable that controls the plot heioght
    height_var = tk.DoubleVar(root, value=10)
    height_label = tk.Label(root, text="Floor Height", font=('calibre', 10, 'bold'))
    height_entry = tk.Entry(root, textvariable=height_var)
    height_label.grid(row=row_counter, column=0)
    height_entry.grid(row=row_counter, column=1)
    row_counter += 1

    # Variable that dtermines if we loop the animation or not
    # TODO :: For some reason this does not want to default to selected on MAC. See how to resolve this.
    dont_angle_reset_var = tk.BooleanVar(root)
    dont_angle_reset_checkbox = tk.Checkbutton(root, text="No Angle Reset", variable=dont_angle_reset_var, onvalue=True, offvalue=False)
    dont_angle_reset_checkbox.grid(row=row_counter, column=1)
    # do_angle_reset_checkbox.select()
    row_counter += 1

    spectrogram_button = tk.Button(root, text="Generate 3D Spectrogram", command=submit_spectrogram)
    spectrogram_button.grid(row=row_counter, column=0,
                   columnspan=4, pady=10, sticky="ew")

