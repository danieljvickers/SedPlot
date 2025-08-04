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

# set the environment and path veriables to where FFMPEG was found
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

def get_box_number(tkValue):
    try:
        return int(tkValue.get())
    except:
        print("Could not get value. Returning default.")
        return 0


def publish_gui_error(gui_msg):
    print(gui_msg)
    # TODO :: set a text field to this



def submit_dsa():
    # create the DSA display and fetch values
    if not renderer.eegData:
        raise 'No Input Data Selected'  # TODO :: have this publish to the GUI
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
    renderer.create_animation_from_data(outputFileName=out_file.get(), channel_number=0, tk_progress_bar=progress_object)
    
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
        file_entry.delete(0, tk.END)
        out_entry.insert(tk.END, file_path)
    else:
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

# common DSA file input and output
# Input
input_file = tk.StringVar(value='')
file_label = tk.Label(root, text='EDF File', font=('calibre', 10, 'bold'))
file_button = tk.Button(root, text="Search", font=10, command=get_input_file)
file_entry = tk.Entry(root, textvariable=input_file, state="readonly", font=10, width=TK_WIDTH)
file_label.grid(row=0, column=1)
file_entry.grid(row=0, column=2)
file_button.grid(row=0, column=3)
# output
out_file = tk.StringVar(value='')
out_label = tk.Label(root, text='Output File', font=('calibre', 10, 'bold'))
out_button = tk.Button(root, text="Select", font=10, command=get_output_file)
out_entry = tk.Entry(root, textvariable=out_file, state="readonly", font=10, width=TK_WIDTH)
out_label.grid(row=1, column=1)
out_entry.grid(row=1, column=2)
out_button.grid(row=1, column=3)

# resolution selection
# output resolution selection
resolutions = ["360p (640x360)", "480p (640x480)", "720p (1280x720)", "1080p (1920x1080)", "2560x1440", "4K (3840x2160)"]
resolution = tk.StringVar(root)
resolution.set(resolutions[3])
dropdown = tk.OptionMenu(root, resolution, *resolutions)
dropdown_label = tk.Label(root, text='Output Resolution', font=('calibre', 10, 'bold'))
dropdown_label.grid(row=2, column=1)
dropdown.grid(row=2, column=2)


# create tabs
tabControl = ttk.Notebook(root)
dsa_tab = ttk.Frame(tabControl)
spectrogram_tab = ttk.Frame(tabControl)
tabControl.add(dsa_tab, text ='DSA')
tabControl.add(spectrogram_tab, text ='Spectrogram')
tabControl.grid(row=3, column=0, columnspan=3, sticky="ew")


# min and max dB inputs
min_db_variable = tk.StringVar(value='20')
max_db_variable = tk.StringVar(value='65')
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
spectrogram_button = tk.Button(dsa_tab, text="Generate 3D Spectrogram", command=submit_spectrogram)
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
progress_bar = ttk.Progressbar(dsa_tab, orient='horizontal', mode='determinate', length=TK_WIDTH*1.5, style="Custom.Horizontal.TProgressbar")
progress_object = TkProgress(dsa_tab, progress_bar)
progress_bar.grid(row=row_counter, column=1, columnspan=3, pady=10, sticky="ew")
row_counter += 1


dsa_tab.columnconfigure(2, minsize=TK_WIDTH)
dsa_tab.columnconfigure(2, weight=1)

# create multiple tabls (notebooks)



root.mainloop()
