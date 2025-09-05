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


## Examples

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