import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import os

from src.DSADisplay import DSADisplay

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"
input_file = "./bin/EEG_240505_084705.edf"
# renderer = DSADisplay(input_file)
# renderer.do_save_animation = True
# renderer.create_plot_from_data(outputFileName="local.mp4", channel_number=0)

def submit():
    renderer = DSADisplay(input_file.get())
    renderer.do_save_animation = True
    renderer.create_plot_from_data(outputFileName="local.mp4", channel_number=0)
    root.destroy()


def browsefunc():
    filename = askopenfilename(filetypes=(("edf file", "*.edf"), ("All files", "*.*"),))
    file_entry.insert(tk.END, filename) # add this


#create root
root = tk.Tk()
root.title("Generate Video")

# input for the input file
input_file = tk.StringVar()
file_label = tk.Label(root, text='EDF File', font=('calibre', 10, 'bold'))
file_button = tk.Button(root, text="Search", font=10, command=browsefunc)
file_entry = tk.Entry(root, textvariable=input_file, font=10)
file_label.grid(row=1, column=1)
file_entry.grid(row=1, column=2)
file_button.grid(row=1, column=3)

submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.grid(row=2, column=0,
                   columnspan=2, pady=10)

root.mainloop()
