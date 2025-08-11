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
                renderer.create_spectrogram_image(start_time_var.get(), (30, 45)) 

        pass

    row_counter = 0


    start_angle_var = tk.DoubleVar(root)
    start_angle_label = tk.Label(root, text='Starting Angle (degrees)', font=('calibre', 10, 'bold'))
    start_angle_entry = tk.Entry(root, textvariable=start_angle_var)
    end_angle_var = tk.DoubleVar(root)
    end_angle_label = tk.Label(root, text='Ending Angle (degrees)', font=('calibre', 10, 'bold'))
    end_angle_entry = tk.Entry(root, textvariable=end_angle_var)
    start_angle_label.grid(row=row_counter, column=0)
    start_angle_entry.grid(row=row_counter, column=1)
    end_angle_label.grid(row=row_counter, column=2)
    end_angle_entry.grid(row=row_counter, column=3)
    row_counter += 1


    spectrogram_button = tk.Button(root, text="Generate 3D Spectrogram", command=submit_spectrogram)
    spectrogram_button.grid(row=row_counter, column=0,
                   columnspan=4, pady=10, sticky="ew")

