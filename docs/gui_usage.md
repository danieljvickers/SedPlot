# SedPlot GUI User Manual

This file contains documentation for all GUI input fields and buttons available in SedPlot. The GUI has a main tab, which hold values that are common to all EEG processing in SedPlot. There are also four tabs for specialized processing. The main tab and each specialized tab has a section below.

Special notes for usage or specific operating systems will appear in **bold**.

## Main Tab

### EDF File

This field is the input EDF file. You must use the button to the right, labeled "Selct Input" to select the data files. This will open a separate window to select files on your system. In order to combine case files, select all of the EDF files that you wish to include. Once loaded, all files will be joined together into a larger data set automatically.

**MacOS**: In order to get around the Apple firewall, the MacOS entitlements requires EDF files to be placed in the computer Desktop, Downloads, or Documents. Reading files from other locations will result in an error.

### Output File

This field is the output that will be saved when running SedPlot. When selecting the button to the right, labeled "select Output" will open a new window to select where the file will be saved, the file name, and the file type. The file ending that is selected in this window decides the type of output that will be generated. The default is MP4, which will render a video of all of the case data loaded. Change this to one of the other options made available in the window to change this behavior.

**MacOS**: In order to get around the Apple firewall, the MacOS entitlements requires output files to be written to the computer Desktop, Downloads, or Documents. Saving files to other locations will result in an error.


### Output Resolution

This drop down selects the number of pixels used to generate the output file. Higher resolution will take longer to save. We recommend generating outputs at lower resolutions to adjust settings and select the correct output time. Once all settings have been adjusted, we recommend rendering the image/video again at a higher resolution.

### EEG Channel

This drop down selects the channel that the EEG data is pulled from when plotted. The Masimo SedLine display saves data in 4 channels, two for the left brain hemisphere (L) and two for the right brain hemisphere (R).

### Start Time

This box accepts a number that is the start time, in minutes. The start time is the time at which a video begins or the time at which a photo is generated. The default time plotted on SedPlot is 20 min. Because of this, the default start time is also set to 20 min. Selecting a start time of 20 min means that SedPlot renders the first frame of data that is "full" (has EEG data for the entire time of the plot).

If a start time greater than the length of the case is provided, the start time will be overwritten to the very end of the case file during processing.

## DSA

This is the DSA tab, which generates all DSA images, made to mimic the look of the Masimo SedLine display.

### Min dB

The power value set for the deepest blue color in SedPlot.

### Max dB

The power value set for the deepest red color in SedPlot.

### Axis Font Size

The font size of the axis labels.

### Tick Font Size

The font size of the numbers used to mark plot ticks.

### Plot SEF

A switch that enables/disables plotting the SEF over the DSA

### Sonicate

A switch that determins if DSA videos will be sonicated. Sonication is the process of converting the EEG signal into pure sound and playing that over the DSA video.

### Plot Freq. Domain

This switch, when enabled, will also render a separate plot in videos which show the instantaneous Fourier Transform of the EEG signal.

### Plot Time Domain

This switch, when enabled, will also render a separate plot that shows the raw/unprocessed EEG signal.

## Spectrogram

This tab contains information for generating 3D renderings of EEG spectrograms. This tab is used to make 3D graphics and STL files.

### Start Angle Azimuth 

This is the azimuth (left-to-right) view angle of the 3D spectrogram and the start angle for animations.

### Start Agnle Elevation

This is the elevation (up/down) view angle of the 3D spectrogram and the start angle for animations.

### End Angle Azimuth 

This is the final azimuth (left-to-right) view angle of the 3D spectrogram for animations.

### End Angle Elevation

This is the elevation (up/down) view angle of the 3D spectrogram for animations.

### Floor Height

The height below the mininum dB (see the DSA tab) that will be plot in the 3D representation before all values being made constant.

### Smoothing Radius

This is the radius, in number of EEG data points, that will be smoothed when generating the 3D spectrogram. It is recommended to set this value to 0 for animations. It is useful to set the smoothing radius to non-zero when exporting STL files to avoid sharp points in the output. This smoothing is applied via a median filter.

### No Angle Reset

This switch is used when generating rotating animations of the 3D spectrogram. Keeping this switch off will make the spectrogram rotate back to its starting view angle at the end of the animation. This is useful for creating smooth looping GIF animations. Turning this switch value on will mean that the view angles will not reset.

### Use Triangle Mesh

When plotting 3D spectrograms, two types of meshes can be used. A rectangular mesh is much faster to calculate on the computer because it is slightly less detailed than a triangular mesh. Using a triangular mesh will result in longer render times, but slightly higher levels of detail.

We recommend testing animations with this switch disabled, and then enabling it for a final high-fidelity render.

## CSV

This tab contains information for exporting data to CSV, which can be opened in spreadsheet software like Excel.

### Generate DSA CSV

This will generate post-processed EEG data in the DSA format. This means that it will output a 2D spreadsheet of dB values in time and frequency to match the current DSA settings.

### Generate Time CSV

This will output the raw/unprocessed EEG data directly to a spreadsheet. This is useful for simply converting the EDF file into a human-readable spreadsheet.

## Advanced

This tab contains other visual tools for adjusting plot output that did not fit into the other tabs.

### Slow Time

This adjusts the slow time used to process the short-time Fourier Transform. This controls the amount of time shown on a single frame of the DSA.

### Fast Time

This adjusts the fast time used to process the short-time Fourier Transform. The Masimo SedLine defaults to a value of 2.5 seconds for this, and changing the value will result in processing that is different than the SedLine. Increasing this value will increase the amount of time between Dsicrete Fourier Transforms. It will have the result of increasing the frequency resolution but decreasing the time resolutions (data points will become shorter and wider).

### Time Amplitude

This value is the height that is plotted when creating videos of the time-series EEG signals in the DSA tab.