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

# Look for ffmpeg next to the executable or in system path and store in ffmpeg_location
def find_ffmpeg():
    ffmpeg_location = None
    if hasattr(sys, '_MEIPASS'):  # This is true if you installed as a binary
        # do a platform specific search for the ffmpeg executable
        if platform.system() == "Windows":
            ffmpeg_location = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg-7.1.1-essentials_build', 'bin', 'ffmpeg.exe')
        elif platform.system() == "Darwin": # MacOS
            ffmpeg_location = os.path.join(sys._MEIPASS, 'ffmpeg', 'ffmpeg')
        else:
            ffmpeg_location = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', 'ffmpeg')

        # set various environment variables to ensure that the executable finds ffmpeg
        if not os.path.isfile(ffmpeg_location):  # if we find the file, use it
            print(f"WARN :: FFMPEG was not installed in this binary. Searching for other FFMPEG installations...")
            ffmpeg_location = None  # reset the location

    if (not ffmpeg_location) and os.path.isdir('ffmpeg'):  # if this is not a binary, and there is a local ffmpeg directory
        if platform.system() == "Windows":
            ffmpeg_location = os.path.join('ffmpeg', 'ffmpeg-7.1.1-essentials_build', 'bin', 'ffmpeg.exe')
        elif platform.system() == "Darwin": # MacOS
            ffmpeg_location = os.path.join('ffmpeg', 'ffmpeg')
        else:
            ffmpeg_location = os.path.join('ffmpeg', 'bin', 'ffmpeg')

        # cofnirm this ffmpeg is valid
        if os.path.isfile(ffmpeg_location):
            print(f"INFO :: Found FFMPEG locally. Using FFMPEG at {ffmpeg_location}")
        else:
            print(f"WARN :: Searched for FFMPEG at {ffmpeg_location} but found nothing. Searching globally...")
            ffmpeg_location = None  # reset the location

    if not ffmpeg_location:  # if ffmpeg is not local, fall back to the global ffmpeg installation
        assert shutil.which("ffmpeg") is not None, "ERROR :: FFMPEG not found locally and is not installed. Install FFMPEG to resolve."  # if it wasn't found, rase an exception
        ffmpeg_location = shutil.which("ffmpeg")  # sets the lcoation to the global installation
        print(f"INFO :: Found FFMPEG globally. Using FFMPEG at {ffmpeg_location}")
    
    return ffmpeg_location

# set the environment and path veriables to where FFMPEG was found
ffmpeg_location = find_ffmpeg()
os.environ["FFMPEG_BINARY"] = ffmpeg_location
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_location
animation.FFMpegWriter.exec_path = ffmpeg_location
plt.rcParams['animation.ffmpeg_path'] = ffmpeg_location


# library imports after ffmpeg is found
from src.DSADisplay import DSADisplay
renderer = DSADisplay()

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


def publish_gui_error(gui_msg):
    print(gui_msg)
    # TODO :: set a text field to this


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
        file_entry.config(state='normal')
        for filepath in filename:
            file_entry.insert(tk.END, filepath + ";") # Insert each file path, separated by a semicolo
        file_entry.config(state='readonly')
        renderer.load_eeg_data(filename)


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
        out_entry.config(state='normal')
        out_entry.delete(0, tk.END)
        out_entry.insert(tk.END, file_path)
        out_entry.config(state='readonly')
        renderer.outputFileName = file_path
    else:
        print("File selection canceled.")


def set_resolution(tk_variable, _, action):
    resolution = resolution_var.get()
    renderer.graphicsSettings.renderSettings.figure_size = (16, 9)
    if resolution == "1080p (1920x1080)":
        renderer.graphicsSettings.renderSettings.dpi = 120
    elif resolution == "2560x1440":
        renderer.graphicsSettings.renderSettings.dpi = 160
    elif resolution == "4K (3840x2160)":
        renderer.graphicsSettings.renderSettings.dpi = 140
    elif resolution == "720p (1280x720)":
        renderer.graphicsSettings.renderSettings.dpi = 80
    elif resolution == "360p (640x360)":
        renderer.graphicsSettings.renderSettings.dpi = 40
    elif resolution == "480p (640x480)":
        renderer.graphicsSettings.renderSettings.dpi = 40
        renderer.graphicsSettings.renderSettings.figure_size == (16, 12)


#create root and the upper file loading
row_counter = 1
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit_me)  # cleanup protocol for when the window is closed
root.title("EEGView")

# common DSA file input and output
# Input
input_file = tk.StringVar(value='')
file_label = tk.Label(root, text='EDF File', font=('calibre', 10, 'bold'))
file_button = tk.Button(root, text="Select Input", font=10, command=get_input_file)
file_entry = tk.Entry(root, textvariable=input_file, state="readonly", font=10, width=TK_WIDTH)
file_label.grid(row=0, column=0)
file_entry.grid(row=0, column=1)
file_button.grid(row=0, column=2)
# output
out_file = tk.StringVar(value='')
out_label = tk.Label(root, text='Output File', font=('calibre', 10, 'bold'))
out_button = tk.Button(root, text="Select Output", font=10, command=get_output_file)
out_entry = tk.Entry(root, textvariable=out_file, state="readonly", font=10, width=TK_WIDTH)
out_label.grid(row=1, column=0)
out_entry.grid(row=1, column=1)
out_button.grid(row=1, column=2)

# resolution selection
# output resolution selection
resolutions = ["360p (640x360)", "480p (640x480)", "720p (1280x720)", "1080p (1920x1080)", "2560x1440", "4K (3840x2160)"]
resolution_var = tk.StringVar(root)
resolution_var.set(resolutions[3])
resolution_var.trace_add('write', set_resolution)
dropdown = tk.OptionMenu(root, resolution_var, *resolutions)
dropdown_label = tk.Label(root, text='Output Resolution', font=('calibre', 10, 'bold'))
dropdown_label.grid(row=2, column=0)
dropdown.grid(row=2, column=1)


# create tabs
tabControl = ttk.Notebook(root)
dsa_tab = ttk.Frame(tabControl)
spectrogram_tab = ttk.Frame(tabControl)
tabControl.add(dsa_tab, text ='DSA')
tabControl.add(spectrogram_tab, text ='Spectrogram')
tabControl.grid(row=3, column=0, columnspan=3, sticky="ew")


# Progress bar
ttk.Style().configure("Custom.Horizontal.TProgressbar",
                    background="light green",  # Color of the filled part
                    troughcolor="lightgray",  # Color of the empty part
                    bordercolor="darkgray", # Outline border
                    lightcolor="white", # Inner border highlight
                    darkcolor="gray") # Inner border shadow
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=TK_WIDTH*1.5, style="Custom.Horizontal.TProgressbar")
progress_object = TkProgress(root, progress_bar)
progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew")


dsa_tab.columnconfigure(2, minsize=TK_WIDTH)
dsa_tab.columnconfigure(2, weight=1)

## TABS
from create_dsa_tab import create_dsa_tab
create_dsa_tab(renderer, progress_object, dsa_tab)
from create_spectrogram_tab import create_spectrogram_tab
create_spectrogram_tab(renderer, progress_object, spectrogram_tab)

root.mainloop()
