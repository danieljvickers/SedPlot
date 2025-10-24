# Spectral EEG View

Repository for the visualization of data by the use of spectrograms. This code was designed specifically for the generation of spectrogram animations from EDF data to aid in the understanding of visualizations of the interoperative EEG displays. The development was initially focused on supporting the Masimo SedLine display.

## Contents
1. [Features](#features)
1. [Citing this Software](#citing-this-software)
1. [Downloading SefPlot](#downloading-sedplot)
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

If you use this software in your academic publications please consider citing us. Citing this works helps to support our open-source development and improve visability of this academic tool. The information for the release publication can be found below:

```
Paper Submitted. Come back later for citation.
```

```
Paper Submitted. Come back later for citation.
```

If you cite us in your research, please consider sending an email to our lead developer at `dnlvickers5@gmail.com`. We would love to add you to the [Citing Works](#citing-works) section of this documentation.

## Downloading SedPlot

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
    py -m venv env  # creates the python virtual environment
    .\env\Scripts\activate. # this activates your virtual environment
    python -m pip install --upgrade pip
    python -m pip install pyinstaller  # use if you plan on installing this code as a binary
    python -m pip install -r requirements.txt  # install all of the python libraries

    curl -L -o ffmpeg.zip https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip  # get the windows ffmpeg binaries
    unzip ffmpeg.zip -d ffmpeg  # unzip ffmpeg and store in a local directory
```

The code can be run directly from the terminal with `python SedPlot.py` or installed as a binary into the `dist` directory with `pyinstaller SedPlot.py --noconfirm --onefile --add-data "ffmpeg:ffmpeg"`.

#### MacOS

Install python and ensure that it is accessible via the command line with `python3 --version`. We recommend building with a python virtual environment, which is shown below. FFMPEG is also required to run this code. We show how to download this code below. Navigate to the top directory of this repository before running and commands. First you must build the python virtual environment and install all of the dependencies:
 
```bash
    brew install python-tk  # install the python tkinter backend BEFORE installing
    python3 -m venv env  # create the python virtual environment
    source /env/bin/activate  # activates the virtual environment
    python -m pip install --upgrade pip
    python -m pip install pyinstaller  # get the py installer to generate binaries
    python -m pip install -r requirements.txt  # install all python modules
```

You will then have two options. If you want to run locally via python it is easiest to install FFMPEG with `brew` and then run the GUI. You can do that by:

```bash
    brew install ffmpeg  # install ffmpeg globally
    python SedPlot.py  # run the GUI from the command line
```

To build the binary yourself, you will need to get a local ffmpeg and build the binary in the `dist` directory like so:

```bash
    curl -L -o ffmpeg.zip https://evermeet.cx/ffmpeg/getrelease/zip  # get the zipped ffmpeg binaries
    unzip ffmpeg.zip -d ffmpeg  # unzip ffmpeg and store in the ffmpeg directory
    pyinstaller SedPlot.py --noconfirm --onefile --add-data "ffmpeg:ffmpeg"  # build the binary
```

#### Linux (Ubuntu)

These commands a specificly developed for Ubuntu, and may require modification for other Linux distributions. Pay perticular attention to the FFMPEG source on other distributions. Install python and ensure that it is accessible via the command line with `python3 --version`. We recommend building with a python virtual environment, which is shown below. FFMPEG is also required to run this code. We show how to download this code below. Navigate to the top directory of this repository before running and commands. The commands required to build are:
 
```bash
    python3 -m venv env. # build the virtual environment
    source /env/bin/activate  # activate your virtual environment
    python -m pip install --upgrade pip
    python -m pip install pyinstaller  # use if you plan on installing this code as a binary
    python -m pip install -r requirements.txt  # install all of the python modules
```

From here, you can either run it from the command line with python or install the binaries into the `dist` directory. To run directly from python it is esiest to install ffmpeg with `apt`. Do so via:

```bash
    sudo apt install ffmpeg  # install ffmpeg globally
    python SedPlot.py  # run the code
```

To build the binary yourself, you will need to get a local ffmpeg and build the binary in the `dist` directory like so:

```bash
    curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz  # fetch the zipped ffmpeg binaries
    tar -xf ffmpeg.tar.xz --strip-components=1 -C ffmpeg  # unzip and store in the ffmpeg directory

    pyinstaller SedPlot.py --noconfirm --onefile --add-data "ffmpeg;ffmpeg"  # build the binary and store in dist
```

## User Instructions

### Downloading EDF Case Files

This software was intended to be run via the GUI. For information on how to obtain EDF files from the Masimo SedLine, refer either to the [Masimo SedLine Documentation](https://techdocs.masimo.com/contentassets/c19b67c39baa430daf34fb73907d8578/lab-7373e-master.pdf) or watch the video below.

```
Video Coming Soon
```

### Using the GUI

Once SedPlot has been downloaded, it can be operated via the graphical user interface. For documentation on the features of the GUI, please refere to the [gui usage reame file](docs/gui_usage.md).

### Using from Python

To view the python usage documentation, checkout the [python usage readme file](docs/python_usage.md).

## Citing Works

Below are a list of papers that used SedPlot to render their graphics and animations. If you use this software in one of your papers, please cite us and send an email to the lead developer at `dnlvickers5@gmail.com` to be added to this section.

- Barkley R, Vickers DJ, Binda DD, Ortega R. An Auditory Analogy for Electroencephalography Understanding: Video in Clinical Anesthesia. A A Pract. 2024 Dec 11;18(12):e01871. doi: 10.1213/XAA.0000000000001871. PMID: 39660749.

- Barkley R, Vickers DJ, Xuan H, Brook K, Lambert D. Brief Instruction Improves Resident Understanding of EEG Spectrograms: A Two-Institution Pilot Study. JEPM. 2025 Oct. Paper Accepted. Full citation coming soon.
