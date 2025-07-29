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

from matplotlib import animation
import matplotlib.pyplot as plt

# library imports
from src.DSADisplay import DSADisplay


# Find FFMPEG on the system or in the binaries
ffmpeg_filename = 'ffmpeg'
if platform.system() == 'Windows':
    ffmpeg_filename = ffmpeg_filename + '.exe'
local_ffmpeg = None
# Look for ffmpeg next to the executable or in system path
if hasattr(sys, '_MEIPASS'):  # This is true if you installed the binaries
    # do a platform specific search for the ffmpeg executable
    if platform.system() == "Windows":
        local_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg-7.1.1-essentials_build', 'bin', ffmpeg_filename)
    else:
        local_ffmpeg = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', ffmpeg_filename)

    # set various environment variables to ensure that the executable finds ffmpeg
    os.environ["FFMPEG_BINARY"] = local_ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = local_ffmpeg
    animation.FFMpegWriter.exec_path = local_ffmpeg
    plt.rcParams['animation.ffmpeg_path'] = local_ffmpeg
elif shutil.which("ffmpeg") is not None:  # this is true if it is installed on your host machine
    print("Unable to find FFmpeg in local repository. Defauling to installed ffmpeg")
    os.environ["IMAGEIO_FFMPEG_EXE"] = shutil.which("ffmpeg")
else:
    raise RuntimeError("FFmpeg not found with executable or on system. Please install it and/or add it your path.")

TK_WIDTH = 75

# progress bar class for Tkinter which can be given to matplotlib and be updated
class TkProgress:
    def __init__(self, master, tk_progress_bar):
        self.progress_bar = tk_progress_bar
        self.master = master
    
    def set_bar_max(self, new_max):
        self.progress_bar['maximum'] = new_max

    def update_bar(self, i, n):
        self.progress_bar['value'] = i
        self.master.update_idletasks() # Force update of the GUI

def get_box_number(tkValue):
    try:
        return int(tkValue.get())
    except:
        print("Could not get value. Returning default.")
        return 0


def submit_dsa():
    # create the DSA display and fetch values
    renderer = DSADisplay(input_file.get())
    renderer.do_save_animation = True
    renderer.graphicsSettings.frequencyDomainParameters.min_db_power = get_box_number(min_db_variable)
    renderer.graphicsSettings.frequencyDomainParameters.max_db_power = get_box_number(max_db_variable)
    renderer.graphicsSettings.renderSettings.font_size = axis_font_var.get()
    renderer.graphicsSettings.renderSettings.tick_size = tick_font_var.get()
    # TODO :: Fetch a particular slow_time starting/ending value

    # graphs graphical resolutoin settings
    set_resolution(renderer, resolution.get())
    if do_sef_var.get():
        renderer.do_plot_spectral_edge_on_spectrogram = True
    if do_audio_var.get():
        renderer.do_add_audio_to_animation = True
    if do_frequency_spectrum_var.get():
        renderer.graphicsSettings.frequencyDomainParameters.do_frequency_domain_plot = True
    if do_time_domain_var.get():
        renderer.graphicsSettings.timeDomainParameters.do_time_domain_plot = True

    # TODO :: Check the output file type and decide if you will render a video or image.
    renderer.create_animation_from_data(outputFileName=out_file.get(), channel_number=0, tk_progress_bar=progress_object, ffmpeg_path=local_ffmpeg)
    
    # destroy the box when done
    del renderer


def submit_spectrogram():
    # Empty for now, but I want it to generate 3D spectrogram videos
    # Look at references/spectrogram_animation.py for what should be done
    # TODO :: Fill all of this in with a new spectrogram object 
    pass



def quit_me():
    print("Closing App...")
    root.quit()
    root.destroy()


def get_input_file():
    filename = askopenfilenames(title="Select EDF Case File(s)",
                                filetypes=(("edf file", "*.edf"),("All files", "*.*")),
                                multiple=True)
    file_entry.delete(0, tk.END)
    if filename:
        for filepath in filename:
            file_entry.insert(tk.END, filepath + ";") # Insert each file path, separated by a semicolo


def get_output_file():
    file_path = asksaveasfilename(
        defaultextension=".mp4",  # Default extension if none is provided by the user
        filetypes=[
            ("Video files", "*.mp4"),
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
    )
    if file_path:  # Check if a file path was selected (not canceled)
        out_label.config(text=file_path)
    else:
        out_label.config(text="File selection canceled.")
        print("File selection canceled.")


def set_resolution(render_object, resolution):
    render_object.graphicsSettings.renderSettings.figure_size = (16, 9)
    if resolution == "1080p (1920x1080)":
        render_object.graphicsSettings.renderSettings.dpi = 120
    elif resolution == "2560x1440":
        render_object.graphicsSettings.renderSettings.dpi = 160
    elif resolution == "4K (3840x2160)":
        render_object.graphicsSettings.renderSettings.dpi = 140
    elif resolution == "720p (1280x720)":
        render_object.graphicsSettings.renderSettings.dpi = 80
    elif resolution == "360p (640x360)":
        render_object.graphicsSettings.renderSettings.dpi = 40
    elif resolution == "480p (640x480)":
        render_object.graphicsSettings.renderSettings.dpi = 40
        render_object.graphicsSettings.renderSettings.figure_size == (16, 12)


#create root
row_counter = 1
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit_me)  # cleanup protocol for when the window is closed
root.title("EEGView")

# input for the input file
# TODO :: Add help message boxes for every single input field that can be opened at run time
input_file = tk.StringVar(value='/home/dan/Documents/repos/spectrogram_generation/bin/EEG_240505_084705.edf')
file_label = tk.Label(root, text='EDF File', font=('calibre', 10, 'bold'))
file_button = tk.Button(root, text="Search", font=10, command=get_input_file)
file_entry = tk.Entry(root, textvariable=input_file, font=10, width=TK_WIDTH)
file_label.grid(row=row_counter, column=1)
file_entry.grid(row=row_counter, column=2)
file_button.grid(row=row_counter, column=3)
row_counter += 1

# min and max dB inputs
min_db_variable = tk.StringVar(value='20')
max_db_variable = tk.StringVar(value='65')
min_db_entry = tk.Entry(root, textvariable=min_db_variable, width=TK_WIDTH)
max_db_entry = tk.Entry(root, textvariable=max_db_variable, width=TK_WIDTH)
min_db_label = tk.Label(root, text='Min dB', font=('calibre', 10, 'bold'))
max_db_label = tk.Label(root, text='Max dB', font=('calibre', 10, 'bold'))
min_db_label.grid(row=row_counter, column=1)
min_db_entry.grid(row=row_counter, column=2)
max_db_label.grid(row=row_counter+1, column=1)
max_db_entry.grid(row=row_counter+1, column=2)
row_counter += 2

# font sizes
axis_font_var = tk.IntVar(root, value=18)
tick_font_var = tk.IntVar(root, value=14)
axis_font_label = tk.Label(root, text='Axis Font Size', font=('calibre', 10, 'bold'))
tick_font_label = tk.Label(root, text='Tick Font Size', font=('calibre', 10, 'bold'))
axis_font_entry = tk.Entry(root, textvariable=axis_font_var, width=TK_WIDTH)
tick_font_entry = tk.Entry(root, textvariable=tick_font_var, width=TK_WIDTH)
axis_font_label.grid(row=row_counter, column=1)
axis_font_entry.grid(row=row_counter, column=2)
tick_font_label.grid(row=row_counter+1, column=1)
tick_font_entry.grid(row=row_counter+1, column=2)
row_counter += 2

# input for the output file
out_file = tk.StringVar(value='test.mp4')
out_label = tk.Label(root, text='Output File', font=('calibre', 10, 'bold'))
out_button = tk.Button(root, text="Select", font=10, command=get_output_file)
out_entry = tk.Entry(root, textvariable=out_file, font=10, width=TK_WIDTH)
out_label.grid(row=row_counter, column=1)
out_entry.grid(row=row_counter, column=2)
out_button.grid(row=row_counter, column=3)
row_counter += 1

# output resolution selection
resolutions = ["360p (640x360)", "480p (640x480)", "720p (1280x720)", "1080p (1920x1080)", "2560x1440", "4K (3840x2160)"]
resolution = tk.StringVar(root)
resolution.set(resolutions[3])
dropdown = tk.OptionMenu(root, resolution, *resolutions)
dropdown_label = tk.Label(root, text='Output Resolution', font=('calibre', 10, 'bold'))
dropdown_label.grid(row=row_counter, column=1)
dropdown.grid(row=row_counter, column=2)
row_counter += 1

# check boxes
do_sef_var = tk.BooleanVar(root)  # check if you want to do the SEF on the plot
do_audio_var = tk.BooleanVar(root)  # check if you want to add audio to the video
do_frequency_spectrum_var = tk.BooleanVar(root)
do_time_domain_var = tk.BooleanVar(root)
do_sef_checkbox = tk.Checkbutton(root, text="Plot SEF", variable=do_sef_var, onvalue=True, offvalue=False)
do_aidio_checkbox = tk.Checkbutton(root, text="Sonicate", variable=do_audio_var, onvalue=True, offvalue=False)
do_frequency_domain_checkbox = tk.Checkbutton(root, text="Plot Freq. Domain", variable=do_frequency_spectrum_var, onvalue=True, offvalue=False)
do_time_domain_checkbox = tk.Checkbutton(root, text="Plot Time Domain", variable=do_time_domain_var, onvalue=True, offvalue=False)
do_sef_checkbox.grid(row=row_counter, column=1)
do_aidio_checkbox.grid(row=row_counter, column=2)
do_frequency_domain_checkbox.grid(row=row_counter, column=3)
do_time_domain_checkbox.grid(row=row_counter + 1, column=1)
row_counter += 2

# The submission buttons
dsa_button = tk.Button(root, text="Generate DSA", command=submit_dsa)
dsa_button.grid(row=row_counter, column=1,
                   columnspan=3, pady=10, sticky="ew")
spectrogram_button = tk.Button(root, text="Generate 3D Spectrogram", command=submit_spectrogram)
spectrogram_button.grid(row=row_counter+1, column=1,
                   columnspan=3, pady=10, sticky="ew")
row_counter += 2

# Progress bar
ttk.Style().configure("Custom.Horizontal.TProgressbar",
                    background="light green",  # Color of the filled part
                    troughcolor="lightgray",  # Color of the empty part
                    bordercolor="darkgray", # Outline border
                    lightcolor="white", # Inner border highlight
                    darkcolor="gray") # Inner border shadow
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=TK_WIDTH*1.5, style="Custom.Horizontal.TProgressbar")
progress_object = TkProgress(root, progress_bar)
progress_bar.grid(row=row_counter, column=1, columnspan=3, pady=10, sticky="ew")
row_counter += 1


root.columnconfigure(2, minsize=TK_WIDTH)
root.columnconfigure(2, weight=1)

root.mainloop()
