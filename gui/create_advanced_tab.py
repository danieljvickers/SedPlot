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
def create_advanced_tab(renderer, root):
    row_counter = 0

    def update_advanced_settings():
        renderer.processingSettings.T_slow = slow_time_variable.get() * 60.
        renderer.processingSettings.T_fast = fast_time_variable.get()
        renderer.graphicsSettings.timeDomainParameters.time_amplitude = time_amplitude_variable.get()
        renderer.external_broadcast("Updated Advanced Settings", "info")

    # sets the slow and fast time inputs
    slow_time_variable = tk.DoubleVar(value=renderer.processingSettings.T_slow / 60.)
    fast_time_variable = tk.DoubleVar(value=renderer.processingSettings.T_fast)
    slow_time_entry = tk.Entry(root, textvariable=slow_time_variable, width=TK_WIDTH)
    fast_time_entry = tk.Entry(root, textvariable=fast_time_variable, width=TK_WIDTH)
    slow_time_label = tk.Label(root, text='Slow Time (min)', font=('calibre', 10, 'bold'))
    fast_time_label = tk.Label(root, text='Fast Time (s)', font=('calibre', 10, 'bold'))
    slow_time_label.grid(row=row_counter, column=1)
    slow_time_entry.grid(row=row_counter, column=2)
    fast_time_label.grid(row=row_counter+1, column=1)
    fast_time_entry.grid(row=row_counter+1, column=2)
    row_counter += 2

    # set the amplitude in the time domain of the data for plotting
    time_amplitude_variable = tk.DoubleVar(value=renderer.graphicsSettings.timeDomainParameters.time_amplitude)
    time_amplitude_entry = tk.Entry(root, textvariable=time_amplitude_variable, width=TK_WIDTH)
    time_amplitude_label = tk.Label(root, text='Time Amplitude (uV)', font=('calibre', 10, 'bold'))
    time_amplitude_label.grid(row=row_counter, column=1)
    time_amplitude_entry.grid(row=row_counter, column=2)
    row_counter += 1

    update_button = tk.Button(root, text="Update Settings", command=update_advanced_settings)
    update_button.grid(row=row_counter, column=1,
                    columnspan=3, pady=10, sticky="ew")
    row_counter += 1