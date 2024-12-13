# spectrogram-visualization

Repository for the visualization of data by the use of spectrograms. This code was designed specifically for the generation of spectrogram animations from EDF data and music data to aid in the understanding of visualizations of the SEDLine display.

## Usage

In order to use this library, import the module from the SignalDisplay directory and create a signal display module. You can then give it an input file name and run the display.

```commandline
from SignalDisplay import SignalDisplay

sig_display = SignalDisplay()
sig_display.load_data_from_file('/path/to/input/file')
sig_display.create_plot_from_data()
```

The default setting is to show the animation in real-time and not save off the file. To generate a file with the audio attached, you will want to set an ouput file of `.mp4` type and tell the signal display object to attach the audio.

```commandline
from SignalDisplay import SignalDisplay

sig_display = SignalDisplay()
sig_display.load_data_from_file('/path/to/input/file')
sig_display.output_file_name = '/path/to/output/file'
sig_display.do_save_animation = True
sig_display.do_add_audio_to_animation = True
sig_display.create_plot_from_data()
```

Note that in order to attach the audio, the signal display object needs to create an intermediate file named `temp.mp4`. It will create this file in the execution directory, and will remove it after generation. If you have a file named `temp.mp4` in your directory, it will be overwritten and then deleted during execution of the plot generation when the `do_add_audio_to_animation` flag is set to `True`.

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