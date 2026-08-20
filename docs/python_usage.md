# Python Usage

## Contents

1. [EEGArray.py](#EEGArray.py)
2. [DSADisplay.py](#DSADisplay.py)
3. [Examples](#Examples)

The source code in this repository is broken up into two diffent directories. There are tools that are beneficial for the compiled binary application, which includes the `EEGView.py` file and all files in the `gui` directory. None of the that code is intended to be helpful when working with this repository. All relevant code is in the other directory, `src`. Inside of `src`, there are two primary files of interest. Here we will describe the contents of each and how to manipulate the code

## EEGArray.py

The `EEGArray.py` file is generally the most-useful file for anyone trying to directly manipulate EEG/DSA data without desiring any of the graphical rendering output. The `EEGArray.py` file contains code for a single `EEGArray` object, with some useful methods for returning processed EEG data. The object must be instantiated with either a string to a valid EDF file or an array of strings for multiple files. If many files are provided, they are concatenated together into a single python. The code can be called and stored to a variable like so: `foo = EEGArray('/path/to/edf/file')` or `foo = EEGArray(['/first/edf/file', '/second/edf/file', ...])`. Upon completion, public member variable are created. The list of member variables is below:

| Member Variable Name | Meaning |
| -                    | - | 
| totalNumSamples      | The number of discrete data values in the array of processed EEG data |
| sampleRate           | The sampling rate in samples per second |
| totalTime            | The total amount of time that the file lasts for, which is equal to `totalNumSamples / sampleRate` |
| inputFiles           | The string or array of strings that was used to generate this particular EEGArray object |
| data                 | A list of numpy arrays that contain the EEG time-series data. Each index in the list is the data for a different EEG channel (usually `len(data) = 4` for commercial EEG montitors) |
| data_is_safe         | `False` if anything about the load was suspect, such as a file that had to be recovered by a fallback reader, a file that could not be read at all, or files whose sample rates or channel counts disagree |
| load_warnings        | A list of human readable strings explaining every problem found while loading. Empty when `data_is_safe` is `True` |

Files are read with `pyedflib.highlevel` first. If that refuses a file, which it does for damaged headers, unreadable annotation channels and recordings that were cut short mid-record, the loader falls back to reading channel by channel with `pyedflib.EdfReader` and then to parsing the EDF/BDF layout directly off disk. Data recovered by a fallback is still returned, but `data_is_safe` is set to `False` so a caller can warn about it. If every reader fails on every file, an `EEGLoadError` is raised.

Raw data can simple be extracted directly from the array with python array slicing (`foo = EEGArray('/edf/file')` then `bar = foo.data[channel_number][start_index:end_index]`). If one desires to recieve a processed frame of EEG data in DSA form, then that can be accessed with the `get_dsa_frame` class method:

Usage: `get_dsa_frame(T_fast, T_slow, max_plot_frequency, start_time_seconds, channel_number=0)`

| Variable Name      | Meaning |
| -                  | - |
| T_fast             | The "fast time", or length of time of a single DFT, in seconds. For the Masimo SedLine display, this value is 2.5 s. |
| T_slow             | The "slow time" or total length of time the DSA plots, in seconds. For the Masimo SedLine display, this value is usually 20 min (1200 s) to 30 min (1800 s) |
| max_plot_frequency | The maximum frequency that points are included up to in Hz. For most interperative EEG monitors, this value is 40 Hz. |
| start_time_seconds | The amount of time into the case that one desires the DSA frame. This will be the time that the right-most value of the DSA frame is at. |
| channel_number     | The channel number to plot. For the Masimo SedLine display, the list of (channel_number, brain_hemisphere) pairs is (0, L1), (1, L2), (2, R1), (3, R2). This is another way to say that indices 0 and 1 are the left brain hemisphere (measured at two different points) and indices 2 and 3 are the right brain hemispheres. | 

## DSADisplay.py

The `DSADisplay.py` file contains all of the code for converting EEG data into a graphic or animation. The display does not require any intiial vairables, and can be created as `foo = DSADisplay()`. Note that much of the display object was made to integrate with the GUI, and as such there are many functions and variables that are intended to not be used when using the obejct programatically. A lit of member variables is listed below:

| Variable Name                        | Default              | Meaning |
| -                                    | -                    | - |
| do_save_animation                    | False                | determines if the animation is saved or just played to the screen |
| do_add_audio_to_animation            | False                | determines if the EEG video output will be sonicated | 
| do_spectrogram_plot                  | True                 | Determines if a spectrogram plot will be rendered | 
| do_spectral_edge_frequency           | False                | # determines if the SEF will be rendered as a standalone plot | 
| do_plot_spectral_edge_on_spectrogram | False                | determins if the SEF will be rendered on top of the spectrogram | 
| graphicsSettings                     | GraphicsSettings()   | A default `GraphicsSettings` object, decribed below | 
| processingSettings                   | ProcessingSettings() | A default `ProcessingSettings` object, decribed below | 
| sefPercent                           | 80                   | The percentage of power that defines the spectral edge frequency. A value of 80 indicates processing with SEF80 |
| eegData                              | None                 | The `EEGArray` object as described above | 
| outputFileName                       | ''                   | The file name that the plot will be saved to | 
| broadcaster                          | None                 | A broadcaster object, used to publish print statements to the GUI. This set to `None` will result in printing to the terminal |

Two private variables hold internal references to graphical settings in objects, defined in `src/GraphicsSettings.py`. You can refer to that file for a detailed breakdown of the structure of these objects. They are also repeated here.

`GraphicsSettings`

| Variable Name                                                    | Default  | Meaning |
| -                                                                | -        | - |
| timeDomainParameters.time_amplitude                              | 40       | Determines the maximum amplitude of the time-domain plot |
| timeDomainParameters.do_time_domain_plot                         | False    | Determines if a time-domain plot will be rendered in a DSA video |
| frequencyDomainParameters.min_db_power                           | -40      | Sets the lowest db power in the color bar | 
| frequencyDomainParameters.max_db_power                           | 5        | Sets the highest db power in the color bar | 
| frequencyDomainParameters.outside_db_to_plot                     | 10       | Sets the height/lowest above/below min_db_power/max_db_power that the DFT plot will render | 
| frequencyDomainParameters.max_plot_frequency                     | 40       | Sets the maximum frequency shown on the DSA | 
| frequencyDomainParameters.do_frequency_domain_plot               | False    | Determines if a frequency-domain plot will be rendered in a DSA video | 
| frequencyDomainParameters.do_frequency_domain_as_colored_scatter | False    | Requires `do_frequency_domain_plot` to be `true`. Sets the scatter points in the DFT plot to be colored the same as the DSA | 
| renderSettings.figure_size                                       | (10, 10) | Sets the (width, height) of the output figure, in inches | 
| renderSettings.font_size                                         | 18       | Sets the font size of the axis labels | 
| renderSettings.tick_size                                         | 14       | Sets the font size of the tick labels | 
| renderSettings.dpi                                               | 100      | Sets the pixels per inch of the figure | 
| renderSettings.do_render_plot_axis                               | True     | Determines if the ticks will be shown on the figure | 
| renderSettings.fps                                               | 30       | Frames per second of all video outputs | 

`ProcessingSettings`

| Variable Name  | Default | Meaning |
| -              | -       | - |
| T_slow         | 1200    | Slow time of the STFT used to generate the DSA, in seconds |
| T_fast         | 2.5     | Fast time of the STFT used to generate the DSA, in seconds |
| channel_number | 0       | Index of the channel number used when opening the `EEGArray.data` object. See above. |

The `DSADisplay` object also has several class methods, with their usage documented below:

`load_eeg_data(inputFileName)` returns nothing, but loads eeg data to the object

- `inputFileName` is a string of a single file **OR** a list of strings that contain multiple EDF files. This will load the data as an `EEGArray` (see above) and stored internall as `eegData` (see below)

`calc_SEF_value(f, linear_data, num_frequency_points)` returns a single frequency value that is the SEF

- `f` is an array of frequency values
- `linear_data` is an array of DFT values, which matches `f`
- `num_frequency_points` is the number of points that are considered in the plot when calculating SEF

`external_broadcast(msg, log_level='info')` returns none but is an internal print value that can either print to the terminal or to a GUI

- `msg` is the message being sent
- `log_level` is the info level, and determines the color of the print statement. Acceptable log_level values are `info`, `success`, `warn`, `error`, and `except`.

`get_ouput_file_ending()` returns a string that is the ending of the output file name (see below)

`create_dsa_animation(start_time_min=0,tk_progress_bar=None)` renders the configured animated DSA output for the currently set input data and a type defined by the file ending of the output file. Acceptable output endings are .GIF and .MP4

- `start_time_min` is the start time (in minutes) into the currently configured eegData that the animation will begin
- `tk_progress_bar` is a reference to a progress bar that will be updated with animation progress. If set to None, it will print progress to the terminal.

`create_dsa_image(start_time_min)` plots a still image DSA of the type specified by the current output file. Acceptable outputs include PNG, JPG, PDF, and SVG.

- `start_time_min` is the time (in minutes) that the image will be rendered at

`create_spectrogram_animation(time_min, script, height_floor=-10, tk_progress_bar=None, filter_size=0, do_triangle_mesh=True)`

- `time_min` is the time in the case file that the spectrogram will plot
- `script` is an array of dictionary objects that control the various look angles of the render. These dictionaries contain: `function` (which can be either "rotate" or "pause"), `begin` which is an integer representing the starting frame of this script element, `end` which is an integer representing the ending frame of this script element, `start` which is a 2-element array containing angles to begin this script element, and `stop` which is a 2-element array containing angles to end this script element.
- `angle` is a 2-element array that contains the view elevation and azimuth look angles in degrees.
- `height_floor` is the height below the currently configured minimum dB value (see `FrequencyDomainParameters`) which will be made flat for the render
- `tk_progress_bar` is a reference to a progress bar that will be updated with animation progress. If set to None, it will print progress to the terminal.
- `filter_size` is the size of a smoothing median filter, mostly useful for generating STL files.
- `do_trignale_mesh` is a boolean that controls if the mesh will be a default surface mesh or a triangle mesh. The triangle mesh usually looks nicer, but takes longer to render. It is recommended to set this to false as you experiment with view angles and data times, then set this to true for the final image render.

`create_spectrogram_image(time_min, angle=(30, 45), height_floor=-10, filter_size=0, do_triangle_mesh=True)`

- `time_min` is the time in the case file that the spectrogram will plot
- `angle` is a 2-element array that contains the view elevation and azimuth look angles in degrees.
- `height_floor` is the height below the currently configured minimum dB value (see `FrequencyDomainParameters`) which will be made flat for the render
- `filter_size` is the size of a smoothing median filter, mostly useful for generating STL files.
- `do_trignale_mesh` is a boolean that controls if the mesh will be a default surface mesh or a triangle mesh. The triangle mesh usually looks nicer, but takes longer to render. It is recommended to set this to false as you experiment with view angles and data times, then set this to true for the final image render.

`create_dsa_csv_file(start_time_min)` writes an output CSV file containing the calculated DSA power, time, and frequency values written to the currently configured output file.

- `start_time_min` is the time in the eegData at which this DSA represents.

`create_time_csv_file(start_time_min)` writes the raw time-series EEG data directly to CSV with the time from the start of the case.

- `start_time_min` is the time in the eegData at which this data represents.

`create_stl_file(time_min, height_floor=-10, filter_size=0)` generates an STL file that contains the triangle vertices of the 3D spectrogram

- `time_min` is the time in minutes that the STL file represents
- `height_floor` is the height below the currently configured minimum dB value (see `FrequencyDomainParameters`) which will be made flat for the render
- `filter_size` is the size of a smoothing median filter, mostly useful for generating STL files.

The DSADisplay object also has a list of member variables used for plotting:

| Variable Name              | Default              | Meaning |
| -                          | -                    | -       |
| do_save_animation          | False                | Determines if the animation/plot will be saved (True) or only displayed to the screen (False) |
| do_add_audio_to_animation  | False                | Determines if any output DSA video MP4s will be sonicated (True) or not (False) |
| do_spectrogram_plot        | True                 | Determines if the MP4 videos will plot the DSA (True) or not (False) |
| do_spectral_edge_frequency | False                | Determines if the MP4 videos will plot the SEF on the DSA (True) or not (False) |
| graphicsSettings           | GraphicsSettings()   | Initialized as a default GraphicsSettings object (see above) |
| processingSettings         | ProcessingSettings() | Initialized as a default ProcessingSettings object (see above) |
| sefPercent                 | 80                   | sets the SEF percentage considered when plotting the SEF |
| eegData                    | None                 | determins if the SEF will be rendered on top of the spectrogram |
| outputFileName             | ''                   | A string that holds the name of the output file |
| broadcaster                | None                 | A value that will only be used with the GUI for publishing messages up to the user. Setting this to None tells the obejct to print to the terminal instead. |
