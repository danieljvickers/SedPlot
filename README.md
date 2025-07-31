# Spectral EEG View

Repository for the visualization of data by the use of spectrograms. This code was designed specifically for the generation of spectrogram animations from EDF data to aid in the understanding of visualizations of the interoperative EEG displays. The development was initially focused on supporting the Masimo SedLine display.

## Contents
1. [Features](#features)
1. [Citing this Software](#citing-this-software)
1. [Downloading EEGView](#downloading-eegview)
1. [User Instructions](#user-instructions)
1. [Citing Works](#citing-works)

Also consider looking at our [Gallery](#gallery).  TODO :: Create a gallery page in the docs

## Featrues

This application is capable of parsing EDF files, which is the native format from most interoperative EEG monitors. If multiple EDF files are provided, it will automatically sort these files and generate longer case files before rendering. It can use that data to generate several different graphics and animation. The outputs include:

- Still images of the EEG DSA (2D spectrogram), selected at particular times of a case. Outputs include PNG, JPG, PDF, and SVG.
- Animations of the DSA for full cases. Outputs include MP4 and GIF. The MP4 outputs can be sonicated.
- Still images of the 3D spectrogram, selected at particular times of a case. Outputs include PNG, JPG, PDF, and SVG.
- Rotating animations of the 3D spectrogram, selected at particlar times of a case. Outputs include MP4 and GIF.
- CAD models of the 3D spectrogram, exported to STL format. This file is capable of being opened in any 3D rendering software.


## Citing this Software

If you use this software in your academic publications please consider citing us. The information for the release publication can be found below:

TODO :: PUT IN A HYPERLINK

```
TODO :: MLM FORMAT
```

```
TODO :: BIBTEX FORMAT
```

If you cite us in your research, please consider sending an email to our lead developer at `dnlvickers5@gmail.com`. We would love to add you to the [Citing Works](#citing-works) section of this documentation.

## Downloading EEGView

### Recommended For Physicians

We provide a direct download of this library for Window, MacOS, and Linux (Ubuntu). If you only desire to have access to the plot generation via the GUI, we recommend that you download the binaries directly. You can find those binaries here:

- Windows
- MacOS
- Linux (Ubuntu)

Once the Windows and MacOS binaries are downloaded, they can immediately be run as a process. The Linux binaries are delivered as a `.zip` file and will first need to be unzipped. The library should work immediately. If this does not work for you or if you are on a non-supported operating system, you can install directly from the command line using the [Recommended for Developers](#recommended-for-developers) section below. Otherwise, you can contact the lead develpoper at `dnlvickers5@gmail.com` for software support.

### Recommended for Developers

All build systems require python to build and install this code. This application requires a version of python 3.12 or newer. Ensure that python can be found via the command line with `py --version` on Windows, or `python3 --version` on MacOS and Linux. Easy building and installing of this code can follow the instructions in the `.github/workflows/build.yaml` file, or are repeated below for easy use:

#### Windows

Install python and ensure that it is accessible via the command line with `py --version`. We recommend building with a python virtual environment, which is shown below. FFMPEG is also required to run this code. We show how to download this code below. Navigate to the top directory of this repository before running and commands. The commands required to build are:
 
```bash
    py -m venv env
    .\env\Scripts\activate. # this activates your virtual environment
    python -m pip install --upgrade pip
    python -m pip install pyinstaller  # use if you plan on installing this code as a binary
    python -m pip install -r requirements.txt

    curl -L -o ffmpeg.zip https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    unzip ffmpeg.zip -d ffmpeg
```

The code can be run directly from the terminal with `python EEGView.py` or installed as a binary into the `dist` directory with `pyinstaller EEGView.py --noconfirm --onefile --add-data "ffmpeg:ffmpeg"`.

#### MacOS

Install python and ensure that it is accessible via the command line with `python3 --version`. We recommend building with a python virtual environment, which is shown below. FFMPEG is also required to run this code. We show how to download this code below. Navigate to the top directory of this repository before running and commands. First you must build the python virtual environment and install all of the dependencies:
 
```bash
    brew install python-tk
    python3 -m venv env
    source /env/bin/activate 
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
    python -m pip install -r requirements.txt
```

You will then have two options. If you want to run locally via python it is easiest to install FFMPEG with `brew` and then run the GUI. You can do that by:

```bash
    brew install ffmpeg
    python EEGView.py
```

To build the binary yourself, you will need to get a local ffmpeg and build the binary in the `dist` directory like so:

```bash
    curl -L -o ffmpeg.zip https://evermeet.cx/ffmpeg/getrelease/zip
    unzip ffmpeg.zip -d ffmpeg
    pyinstaller EEGView.py --noconfirm --onefile --add-data "ffmpeg:ffmpeg"
```

#### Linux (Ubuntu)

These commands a specificly developed for Ubuntu, and may require modification for other Linux distributions. Pay perticular attention to the FFMPEG source on other distributions. Install python and ensure that it is accessible via the command line with `python3`. We recommend building with a python virtual environment, which is shown below. FFMPEG is also required to run this code. We show how to download this code below. Navigate to the top directory of this repository before running and commands. The commands required to build are:
 
```bash
    # set up the python virtual environment
    python3 -m venv env
    source /env/bin/activate  # this activates your virtual environment
    python -m pip install --upgrade pip
    python -m pip install pyinstaller  # use if you plan on installing this code as a binary
    python -m pip install -r requirements.txt
```

From here, you can either run it from the command line with python or install the binaries into the `dist` directory. To run directly from python it is esiest to install ffmpeg with `apt`. Do so via:

```bash
    sudo apt install ffmpeg
    python EEGView.py
```

To build the binary yourself, you will need to get a local ffmpeg and build the binary in the `dist` directory like so:

```bash
    curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xf ffmpeg.tar.xz --strip-components=1 -C ffmpeg

    pyinstaller EEGView.py --noconfirm --onefile --add-data "ffmpeg;ffmpeg"
```

## User Instructions

### Using the GUI

TODO :: Put in a bunch of graphics and a discription of what all of the buttons do


### Using from Python

TODO :: Add instructions on how to use the code when everything is done

```python
from SignalDisplay import SignalDisplay

sig_display = SignalDisplay()
sig_display.load_data_from_file('/path/to/input/file')
sig_display.create_plot_from_data()
```

The default setting is to show the animation in real-time and not save off the file. To generate a file with the audio attached, you will want to set an ouput file of `.mp4` type and tell the signal display object to attach the audio.

```python
from SignalDisplay import SignalDisplay

sig_display = SignalDisplay()
sig_display.load_data_from_file('/path/to/input/file')
sig_display.output_file_name = '/path/to/output/file'
sig_display.do_save_animation = True
sig_display.do_add_audio_to_animation = True
sig_display.create_plot_from_data()
```

Note that in order to attach the audio, the signal display object needs to create an intermediate file named `temp.mp4`. It will create this file in the execution directory, and will remove it after generation. If you have a file named `temp.mp4` in your directory, it will be overwritten and then deleted during execution of the plot generation when the `do_add_audio_to_animation` flag is set to `True`.

## Citing Works

Below are a list of papers that used EEG view to render their graphics and animations. If you use this software in one of your papers, please cite us and send an email to the lead developer at `dnlvickers5@gmail.com` to be added to this section.

- Barkley R, Vickers DJ, Binda DD, Ortega R. An Auditory Analogy for Electroencephalography Understanding: Video in Clinical Anesthesia. A A Pract. 2024 Dec 11;18(12):e01871. doi: 10.1213/XAA.0000000000001871. PMID: 39660749.

- Lambert Paper


## Customization

There are multiple customization options for generating the plots. There are 3 subcategories of flags, grouped by the plot that they apply to. First, there is a `SignalDisplay.time_domain_parameters` where:

| name | default value | description |
| - | - | - |
| time_amplitude | 40 | The amplitude range plotted in the time domain plot |
| do_time_domain_plot | True | Determines if the time-domain data will be plotted in the animation |

There are also values in `SignalDisplay.frequency_domain_parameters`:

| name | default value | description |
| - | - | - |
| min_db_power | 100 | Sets the power amplitude such that the color will be dark blue |
| max_db_power | 130 | Sets the power amplitude such that the color will be dark red |
| outside_db_to_plot | 10 | Determines how far past the minimum and maximum power that will be plotted |
| max_plot_frequency | 1200 | Sets the maximum frequency that will be plot on the frequency-domain data and the spectrogram |
| do_frequency_domain_plot | True | Determines if the frequency-domain data will be plotted in the animation |
| do_frequency_domain_as_colored_scatter | True | If `True`, the frequency domain will be plotted as a colored scatter plot and as a line plot if set to `False` |

The final subcategory is `SignalDisplay.graphics_settings`:

| name | default value | description |
| - | - | - |
| figure_size | (10, 10) | Determines the plot dimensions in inches as (height, width) |
| font_size | 18 | The font size of the axis labels |
| dpi | 100 | The density of pixels in units of pixels per inch |

Finally, there are uncategorized parameters:

| name | default value | description |
| - | - | - |
| do_save_animation | False | When `True`, save the animation as the `output_file_name` parameter |
| do_add_audio_to_animation | False | When `True`, save the audio file data as the audio of the clip |
| do_spectrogram_plot | True | When `True`, include the spectrogram in the final animation |
| do_spectral_edge_frequency | False | When `True`, include the spectral edge frequency in the spectrogram |
| output_file_name | '' | Sets the output file name with accepted types of `.mp4` and `.gif` |
| fps | 40 | Sets the frames per second of the animation, and determines the fast time of the plot |
| T_slow | 40 | Sets the slow-time duration of the spectrogram |
| total_frames | -1 | Sets the total number of frames to plot for. When -1, default to plotting the entire file content |

## Installation

This library requires some video and edf dependencies in order to run. We document those here.

| Dependency | Required for |
| - | - |
| ffmpeg | Video rendering of mp4s and opening of mp3s |
| pydub | Editing of .mp3 files |
| moviepy | Video rendering wrapper around ffmpeg |
| pyedf | Reading and editing EDF files | 