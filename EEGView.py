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
            for root, dirs, files in os.walk(os.path.join(sys._MEIPASS, 'ffmpeg')):  # searches the ffmpeg temp folder
                if "ffmpeg.exe" in files:
                    ffmpeg_location = os.path.join(root, "ffmpeg.exe")
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
            for root, dirs, files in os.walk('ffmpeg'):  # searches the ffmpeg temp folder
                if "ffmpeg.exe" in files:
                    ffmpeg_location = os.path.join(root, "ffmpeg.exe")
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

    if not os.path.isfile(ffmpeg_location):  # if ffmpeg is not local, fall back to the global ffmpeg installation
        ffmpeg_location = shutil.which("ffmpeg")  # sets the lcoation to the global installation
        if not ffmpeg_location:
            print("ERROR :: FFMPEG not found locally and is not installed. Video (MP4) file generation will be disables. Install FFMPEG to resolve.")  # if it wasn't found, rase an exception
        else:
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
SUCC_COLOR = '\033[32m'
INFO_COLOR = '\033[36m'
WARN_COLOR = '\033[33m'
ERROR_COLOR = '\033[31m'
RESET = '\033[0m'


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


# progress bar class for Tkinter which can be given to matplotlib and be updated
class TkStatus:
    def __init__(self, master, tk_label):
        self.broadcast_label = tk_label
        self.master = master
    
    def broadcast(self, msg, log_level='info'):
        if log_level == 'info':
            print(f"{INFO_COLOR}{msg}{RESET}")
            self.broadcast_label.config(text=msg, fg='black')
        elif log_level == 'success':
            print(f"{SUCC_COLOR}{msg}{RESET}")
            self.broadcast_label.config(text=msg, fg='green')
        elif log_level == 'warn':
            print(f"{WARN_COLOR}{msg}{RESET}")
            self.broadcast_label.config(text=msg, fg='orange')
        elif log_level == 'error':
            print(f"{ERROR_COLOR}{msg}{RESET}")
            self.broadcast_label.config(text=msg, fg='red')
        elif log_level == 'except':  # complete failure
            self.broadcast_label.config(text=msg, fg='red')
            raise msg


def publish_gui_error(gui_msg):
    print(gui_msg)
    # TODO :: set a text field to this


def quit_me():
    print("Closing App...")
    root.quit()
    root.destroy()


def get_input_file():
    filename = askopenfilenames(title="Select EDF Case File(s)",
                                filetypes=(("edf file", "*.edf"), ("All files", "*.*")),
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
        defaultextension=default_output_filetype,  # Default extension if none is provided by the user
        filetypes=supported_output_filetypes
    )
    if file_path:  # Check if a file path was selected (not canceled)
        out_entry.config(state='normal')
        out_entry.delete(0, tk.END)
        out_entry.insert(tk.END, file_path)
        out_entry.config(state='readonly')
        renderer.outputFileName = file_path
    else:
        print("File selection canceled.")


def set_resolution(tk_variable=None, _=None, action=None):
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


def set_channel_num(tk_variable=None, _=None, action=None):
    renderer.processingSettings.channel_number = channel_map[channel_var.get()]
    

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
supported_output_filetypes = [
    ("GIF files", "*.gif"),
    ("PNG files", "*.png"),
    ("JPG files", "*.jpg"),
    ("PDF files", "*.pdf"),
    ("SVG files", "*.svg"),
    ("CSV files", "*.csv"),
    ("STL files", "*.stl"),
    ("All files", "*.*")
]  # sets the list of supported files
default_output_filetype = ".png" # sets the default file to PNG images
if ffmpeg_location is not None:
    # if FFMPEG was found, add MP4 video as a supported file type and set it to default
    supported_output_filetypes = [("Video files", "*.mp4")] + supported_output_filetypes
    default_output_filetype = ".mp4"
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
resolution_dropdown = tk.OptionMenu(root, resolution_var, *resolutions)
resolution_label = tk.Label(root, text='Output Resolution', font=('calibre', 10, 'bold'))
resolution_label.grid(row=2, column=0)
resolution_dropdown.grid(row=2, column=1)
set_resolution()

# channel number select
channel_map = {
    'L1': 0,
    'L2': 1,
    'R1': 2,
    'R2': 3,  # TODO :: verify all of these labels
}
channel_var = tk.StringVar(root)
channel_var.set(list(channel_map.keys())[0])
channel_var.trace_add('write', set_channel_num)
channel_dropdown = tk.OptionMenu(root, channel_var, *channel_map.keys())
channel_label = tk.Label(root, text='EEG Channel', font=('calibre', 10, 'bold'))
channel_label.grid(row=3, column=0)
channel_dropdown.grid(row=3, column=1)
set_resolution()

# time select
start_time_var = tk.DoubleVar(root)
start_time_var.set(renderer.processingSettings.T_slow / 60.)
start_time_entry = tk.Entry(root, textvariable=start_time_var, font=10, width=TK_WIDTH)
start_time_label = tk.Label(root, text="Start Time (min)", font=('calibre', 10, 'bold'))
start_time_label.grid(row=4, column=0)
start_time_entry.grid(row=4, column=1)


# create tabs
tabControl = ttk.Notebook(root)
dsa_tab = ttk.Frame(tabControl)
spectrogram_tab = ttk.Frame(tabControl)
csv_tab = ttk.Frame(tabControl)
advanced_tab = ttk.Frame(tabControl)
tabControl.add(dsa_tab, text ='DSA')
tabControl.add(spectrogram_tab, text ='Spectrogram')
tabControl.add(csv_tab, text='CSV')
tabControl.add(advanced_tab, text ='Advanced')
tabControl.grid(row=5, column=0, columnspan=3, sticky="ew")


# broadcaster
broadcast_label = tk.Label(root)
broadcast_label.grid(row=6, column=1)
broadcaster = TkStatus(root, broadcast_label)
renderer.broadcaster = broadcaster


# Progress bar
ttk.Style().configure("Custom.Horizontal.TProgressbar",
                    background="light green",  # Color of the filled part
                    troughcolor="lightgray",  # Color of the empty part
                    bordercolor="darkgray", # Outline border
                    lightcolor="white", # Inner border highlight
                    darkcolor="gray") # Inner border shadow
progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=TK_WIDTH*1.5, style="Custom.Horizontal.TProgressbar")
progress_object = TkProgress(root, progress_bar)
progress_bar.grid(row=7, column=0, columnspan=3, sticky="ew")


dsa_tab.columnconfigure(2, minsize=TK_WIDTH)
dsa_tab.columnconfigure(2, weight=1)

## Create all of the tabs
from gui.create_dsa_tab import create_dsa_tab
create_dsa_tab(renderer, progress_object, dsa_tab, start_time_var)
from gui.create_spectrogram_tab import create_spectrogram_tab
create_spectrogram_tab(renderer, progress_object, spectrogram_tab, start_time_var)
from gui.create_csv_tab import create_csv_tab
create_csv_tab(renderer, csv_tab, start_time_var)

root.mainloop()
