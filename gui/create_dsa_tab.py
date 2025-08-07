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

def create_dsa_tab(renderer, progress_object, dsa_tab, start_time_var):
    row_counter = 0

    def submit_dsa():
        # create the DSA display and fetch values
        if not renderer.eegData:
            raise 'No Input Data Selected'  # TODO :: have this publish to the GUI
        renderer.do_save_animation = True
        renderer.graphicsSettings.frequencyDomainParameters.min_db_power = int(min_db_variable.get())
        renderer.graphicsSettings.frequencyDomainParameters.max_db_power = int(max_db_variable.get())
        renderer.graphicsSettings.renderSettings.font_size = axis_font_var.get()
        renderer.graphicsSettings.renderSettings.tick_size = tick_font_var.get()
        # TODO :: Fetch a particular slow_time starting/ending value

        # graphs graphical resolutoin settings
        if do_sef_var.get():
            renderer.do_plot_spectral_edge_on_spectrogram = True
        if do_audio_var.get():
            renderer.do_add_audio_to_animation = True
        if do_frequency_spectrum_var.get():
            renderer.graphicsSettings.frequencyDomainParameters.do_frequency_domain_plot = True
        if do_time_domain_var.get():
            renderer.graphicsSettings.timeDomainParameters.do_time_domain_plot = True

        file_ending = renderer.get_ouput_file_ending().lower()
        if file_ending in ('mp4', 'gif'):
            renderer.create_dsa_animation(tk_progress_bar=progress_object, start_time_min=start_time_var.get())
        elif file_ending in ('png', 'jpg', 'svg', 'pdf'):
            renderer.create_dsa_image(start_time_var.get())
        else:
            renderer.external_broadcast(f"File ending '.{file_ending}' is not supported.", 'error')

    # min and max dB inputs
    min_db_variable = tk.DoubleVar(value=renderer.graphicsSettings.frequencyDomainParameters.min_db_power)
    max_db_variable = tk.DoubleVar(value=renderer.graphicsSettings.frequencyDomainParameters.max_db_power)
    min_db_entry = tk.Entry(dsa_tab, textvariable=min_db_variable, width=TK_WIDTH)
    max_db_entry = tk.Entry(dsa_tab, textvariable=max_db_variable, width=TK_WIDTH)
    min_db_label = tk.Label(dsa_tab, text='Min dB', font=('calibre', 10, 'bold'))
    max_db_label = tk.Label(dsa_tab, text='Max dB', font=('calibre', 10, 'bold'))
    min_db_label.grid(row=row_counter, column=1)
    min_db_entry.grid(row=row_counter, column=2)
    max_db_label.grid(row=row_counter+1, column=1)
    max_db_entry.grid(row=row_counter+1, column=2)
    row_counter += 2

    # font sizes
    axis_font_var = tk.IntVar(dsa_tab, value=18)
    tick_font_var = tk.IntVar(dsa_tab, value=14)
    axis_font_label = tk.Label(dsa_tab, text='Axis Font Size', font=('calibre', 10, 'bold'))
    tick_font_label = tk.Label(dsa_tab, text='Tick Font Size', font=('calibre', 10, 'bold'))
    axis_font_entry = tk.Entry(dsa_tab, textvariable=axis_font_var, width=TK_WIDTH)
    tick_font_entry = tk.Entry(dsa_tab, textvariable=tick_font_var, width=TK_WIDTH)
    axis_font_label.grid(row=row_counter, column=1)
    axis_font_entry.grid(row=row_counter, column=2)
    tick_font_label.grid(row=row_counter+1, column=1)
    tick_font_entry.grid(row=row_counter+1, column=2)
    row_counter += 2

    # check boxes
    do_sef_var = tk.BooleanVar(dsa_tab)  # check if you want to do the SEF on the plot
    do_audio_var = tk.BooleanVar(dsa_tab)  # check if you want to add audio to the video
    do_frequency_spectrum_var = tk.BooleanVar(dsa_tab)
    do_time_domain_var = tk.BooleanVar(dsa_tab)
    do_sef_checkbox = tk.Checkbutton(dsa_tab, text="Plot SEF", variable=do_sef_var, onvalue=True, offvalue=False)
    do_aidio_checkbox = tk.Checkbutton(dsa_tab, text="Sonicate", variable=do_audio_var, onvalue=True, offvalue=False)
    do_frequency_domain_checkbox = tk.Checkbutton(dsa_tab, text="Plot Freq. Domain", variable=do_frequency_spectrum_var, onvalue=True, offvalue=False)
    do_time_domain_checkbox = tk.Checkbutton(dsa_tab, text="Plot Time Domain", variable=do_time_domain_var, onvalue=True, offvalue=False)
    do_sef_checkbox.grid(row=row_counter, column=1)
    do_aidio_checkbox.grid(row=row_counter, column=2)
    do_frequency_domain_checkbox.grid(row=row_counter, column=3)
    do_time_domain_checkbox.grid(row=row_counter + 1, column=1)
    row_counter += 2

    # The submission buttons
    dsa_button = tk.Button(dsa_tab, text="Generate DSA", command=submit_dsa)
    dsa_button.grid(row=row_counter, column=1,
                    columnspan=3, pady=10, sticky="ew")
    row_counter += 1