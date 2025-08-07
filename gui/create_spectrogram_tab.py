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

def create_spectrogram_tab(renderer, progress_object, spectrogram_tab, start_time_var):
    def submit_spectrogram():
        # Empty for now, but I want it to generate 3D spectrogram videos
        # Look at references/spectrogram_animation.py for what should be done
        # TODO :: Fill all of this in with a new spectrogram object 
        pass

    row_counter = 0
    spectrogram_button = tk.Button(spectrogram_tab, text="Generate 3D Spectrogram", command=submit_spectrogram)
    spectrogram_button.grid(row=row_counter+1, column=1,
                   columnspan=3, pady=10, sticky="ew")
