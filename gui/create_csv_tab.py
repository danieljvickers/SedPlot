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

def create_csv_tab(renderer, root, start_time_var):
    row_counter = 0

    def submit_csv():
        # create the DSA display and fetch values
        if not renderer.eegData:
            renderer.external_broadcast('No Input Data Selected', 'error')

        file_ending = renderer.get_ouput_file_ending().lower()
        if file_ending in ('csv'):
            renderer.create_csv_file(start_time_var.get())
        else:
            renderer.external_broadcast(f"File ending '.{file_ending}' is not supported for this button. Try '.csv' instead.", 'error')

    # The submission buttons
    csv_button = tk.Button(root, text="Generate DSA", command=submit_csv)
    csv_button.grid(row=row_counter, column=1,
                    columnspan=3, pady=10, sticky="ew")
    row_counter += 1