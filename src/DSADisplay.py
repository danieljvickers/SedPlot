# graphical rendering libraries
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import moviepy as mp

# math and scientific libraries
import numpy as np
from scipy.io import wavfile
import math

# basic os and gui management libraries
import os
# from tqdm.gui import tqdm
from tqdm import tqdm

# internal data structures
from .EEGArray import EEGArray
from .GraphicsSettings import GraphicsSettings, ProcessingSettings


class DSADisplay:
    do_save_animation = False  # determines if the animation is saved or just played to the screen
    do_add_audio_to_animation = False  # determines if the EEG video output will be sonicated
    do_spectrogram_plot = True  # Determines if a spectrogram plot will be rendered
    do_spectral_edge_frequency = False  # determines if the SEF will be rendered as a standalone plot
    do_plot_spectral_edge_on_spectrogram = False  # determins if the SEF will be rendered on top of the spectrogram
    graphicsSettings = GraphicsSettings()
    processingSettings = ProcessingSettings()
    sefPercent = 80
    eegData = None
    outputFileName = ''
    broadcaster = None


    def __init__(self, inputFileName=''):
        if inputFileName !=  '':
            self.eegData = EEGArray(inputFileName)


    def load_eeg_data(self, inputFileName):
        if self.eegData:
            del self.eegData  # TODO :: Determine if this kind of memory management is actually required. Also try ot determine if this must be thread safe.
        try:
            self.eegData = EEGArray(inputFileName)
            self.external_broadcast("File Loaded")
        except:
            self.external_broadcast(f"Error Opening file(s). No such files or invalid data format.", 'error')


    # takes in frequency-domain data to compute the SEF80
    def calc_SEF_value(self, f, linear_data, num_frequency_points):
        y_in_sum = np.fft.ifftshift(linear_data)[:num_frequency_points]  # gets the section of the array that we will be summing
        total_power = sum(y_in_sum)  # computes the total power in the array
        for i in range(len(y_in_sum)):
            if sum(y_in_sum[:i]) > total_power * (self.sefPercent / 100.):  # check if we are over the SEF80
                return np.fft.ifftshift(f)[i-1]  # return the SEF value at this point

    def rotate_to_angle(self, ax, i, window, start_angle, end_angle):
        i_frac = i / window
        current_angle = start_angle * (1. - i_frac) + i_frac * end_angle
        ax.view_init(elev=current_angle[0], azim=current_angle[1])

    
    def external_broadcast(self, msg, log_level='info'):
        if self.broadcaster:
            self.broadcaster.broadcast(msg, log_level)
        else:
            print(msg)

    def get_ouput_file_ending(self):
        return self.outputFileName.split('.')[-1].lower()


    # main loop which renders the plots
    def create_dsa_animation(self, start_time_min=0,tk_progress_bar=None):
        
        if self.do_save_animation and self.outputFileName == '':
            self.external_broadcast('Requested to save, but no output filename set.', 'error')
            return
        self.external_broadcast("Setting Up Plots")

        # define the animation function which is called every frame
        global_index = 0
        def run_animation(frame_number):
            nonlocal global_index
            y = np.array(self.eegData.data[self.processingSettings.channel_number][num_samples * global_index:num_samples * (global_index + 1)])

            # handle the time-domain plotting case
            if self.graphicsSettings.timeDomainParameters.do_time_domain_plot:
                fast_time_line.set_data(t, np.real(y))

            # handels the case of plotting the SEF graph
            y_f_linear = abs(np.fft.fftshift(np.fft.fft(y)))
            if self.do_spectral_edge_frequency or self.do_plot_spectral_edge_on_spectrogram:
                spectral_edge_frequency = self.calc_SEF_value(f, y_f_linear, num_frequency_points)
                if self.do_spectral_edge_frequency:
                    spectral_edge_data = np.roll(sef_line.get_ydata(), -1, axis=0)
                    spectral_edge_data[-1] = spectral_edge_frequency
                    sef_line.set_ydata(spectral_edge_data)

            # convert the frequency-domain data to dB and replace 0s with small numbers that will not conver to NaNs
            for i in range(1, len(y_f_linear)):
                if y_f_linear[i] == 0.:
                    y_f_linear[i] = 1e-100
            y_f = 20 * np.log10(y_f_linear)

            # handle plotting in the frequency domain.
            if self.graphicsSettings.frequencyDomainParameters.do_frequency_domain_plot:
                if self.graphicsSettings.frequencyDomainParameters.do_frequency_domain_as_colored_scatter:
                    scatter_data = np.column_stack((f, y_f))
                    frequency_line.set_offsets(scatter_data)
                    normalized_data = plt.Normalize(self.graphicsSettings.frequencyDomainParameters.min_db_power,
                                                    self.graphicsSettings.frequencyDomainParameters.max_db_power)(y_f)
                    colors = cm.jet(normalized_data)
                    frequency_line.set_color(colors)
                else:
                    frequency_line.set_data(f, np.real(y_f))

            if self.do_spectrogram_plot:
                sed_array = sed_plot.get_array().transpose()
                sed_array = np.roll(sed_array, -1, axis=0)
                if self.do_plot_spectral_edge_on_spectrogram:
                    spectral_edge_data = np.roll(sef_on_spec.get_ydata(), -1, axis=0)
                    spectral_edge_data[-1] = self.graphicsSettings.frequencyDomainParameters.max_plot_frequency - spectral_edge_frequency
                    sef_on_spec.set_ydata(spectral_edge_data)
                sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(sed_array[0])])
                sed_plot.set_array(sed_array.transpose())
            global_index += 1


        # initialize some variables used in the plot generation
        num_samples = int(math.floor(self.eegData.sampleRate * self.processingSettings.T_fast))
        t = np.array([i / self.eegData.sampleRate for i in range(num_samples)])
        f = np.fft.fftshift(np.fft.fftfreq(len(t), d=1 / self.eegData.sampleRate))
        num_frequency_points = 0
        for f_sample in f:
            if 0. <= f_sample <= self.graphicsSettings.frequencyDomainParameters.max_plot_frequency:
                num_frequency_points += 1

        # start the outline of the basic plots
        fig = plt.figure(figsize=self.graphicsSettings.renderSettings.figure_size)
        total_number_plot = 0
        t_index, f_index, s_index, sef_index = -1, -1, -1, -1
        if self.graphicsSettings.timeDomainParameters.do_time_domain_plot:
            t_index = total_number_plot
            total_number_plot += 1
        if self.graphicsSettings.frequencyDomainParameters.do_frequency_domain_plot:
            f_index = total_number_plot
            total_number_plot += 1
        if self.do_spectrogram_plot:
            s_index = total_number_plot
            total_number_plot += 1
        if self.do_spectral_edge_frequency:
            sef_index = total_number_plot
            total_number_plot += 1
        assert total_number_plot > 0 , "No plots configured to display."

        fast_time_line = 0
        frequency_line = 0
        sed_plot = 0
        sef_line = 0
        sef_on_spec = 0
        # create a subplot for each type of plot specified
        for i in range(total_number_plot):
            ax3 = plt.subplot(total_number_plot, 1, int(i+1))
            if i == t_index:
                if self.graphicsSettings.timeDomainParameters.do_time_domain_plot:
                    fast_time_line = plt.plot([])[0]
                    plt.xlabel('Time (s)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.ylabel('Energy ($\\mu$V)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.xlim([0, self.processingSettings.T_fast])
                    plt.ylim([-self.graphicsSettings.timeDomainParameters.time_amplitude, self.graphicsSettings.timeDomainParameters.time_amplitude])
                    plt.xticks(fontsize=GraphicsSettings.renderSettings.tick_size)
                    plt.yticks(fontsize=GraphicsSettings.renderSettings.tick_size)
            elif i == f_index:
                if self.graphicsSettings.frequencyDomainParameters.do_frequency_domain_plot:
                    if self.graphicsSettings.frequencyDomainParameters.do_frequency_domain_as_colored_scatter:
                        frequency_line = plt.scatter(np.zeros(int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency * self.processingSettings.T_fast)),
                                                     np.zeros(int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency * self.processingSettings.T_fast)),
                                                     cmap='jet', vmin=self.graphicsSettings.frequencyDomainParameters.min_db_power,
                                                     vmax=self.graphicsSettings.frequencyDomainParameters.max_db_power)
                    else:
                        frequency_line = plt.plot([])[0]
                    plt.xlim([0, self.graphicsSettings.frequencyDomainParameters.max_plot_frequency])
                    plt.ylim([self.graphicsSettings.frequencyDomainParameters.min_db_power - self.graphicsSettings.frequencyDomainParameters.outside_db_to_plot,
                              self.graphicsSettings.frequencyDomainParameters.max_db_power + self.graphicsSettings.frequencyDomainParameters.outside_db_to_plot])
                    plt.xlabel('Frequency (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.ylabel('Power (dB)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.xticks(fontsize=GraphicsSettings.renderSettings.tick_size)
                    plt.yticks(fontsize=GraphicsSettings.renderSettings.tick_size)
            elif i == s_index:
                if self.do_spectrogram_plot:
                    empty_sed_array = np.array([np.zeros(num_frequency_points) - 100 for i in range(int(self.processingSettings.T_slow / self.processingSettings.T_fast))])
                    sed_plot = plt.imshow(empty_sed_array.transpose(), cmap='jet',
                                          vmin=self.graphicsSettings.frequencyDomainParameters.min_db_power,
                                          vmax=self.graphicsSettings.frequencyDomainParameters.max_db_power,
                                          aspect='auto', interpolation='bilinear',
                                          extent=[-int(self.processingSettings.T_slow / 60), 0, self.graphicsSettings.frequencyDomainParameters.max_plot_frequency, 0])
                    cbar = plt.colorbar()
                    cbar.set_label('Power (dB)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    ax3.set_yticks(np.array([-0. + i*self.graphicsSettings.frequencyDomainParameters.max_plot_frequency/4 for i in range(5)]))
                    ax3.set_yticklabels(np.arange(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency, -0.5,
                                                  -int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency / 4)))
                    if self.do_plot_spectral_edge_on_spectrogram:
                        negative_times = [(-self.processingSettings.T_slow + i * self.processingSettings.T_fast) / 60 for i in range(int(self.processingSettings.T_slow / self.processingSettings.T_fast))]
                        sef_on_spec = ax3.plot(negative_times, [self.graphicsSettings.frequencyDomainParameters.max_plot_frequency
                                                                for i in range(int(self.processingSettings.T_slow / self.processingSettings.T_fast))],
                                               color='white', linewidth=3)[0]
                    plt.xlabel('Time (min)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.ylabel('Frequency (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.xticks(fontsize=GraphicsSettings.renderSettings.tick_size)
                    plt.yticks(fontsize=GraphicsSettings.renderSettings.tick_size)
            elif i == sef_index:
                if self.do_spectral_edge_frequency:
                    negative_times = [-self.processingSettings.T_slow + i * self.processingSettings.T_fast for i in range(int(self.processingSettings.T_slow / self.processingSettings.T_fast))]
                    sef_line = plt.plot(negative_times, [0 for i in range(int(self.processingSettings.T_slow / self.processingSettings.T_fast))])[0]
                    plt.xlabel('Time (s)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.ylabel('SEF (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
                    plt.ylim([0, self.graphicsSettings.frequencyDomainParameters.max_plot_frequency])
                    plt.xlim([-self.processingSettings.T_slow, 0])
                    plt.xticks(fontsize=GraphicsSettings.renderSettings.tick_size)
                    plt.yticks(fontsize=GraphicsSettings.renderSettings.tick_size)
        plt.tight_layout()

        # skip frames until we get to the start time
        frames_to_skip = math.floor(start_time_min * 60. / self.processingSettings.T_fast)
        for i in range(frames_to_skip):
            run_animation(i)
        total_frames = self.eegData.get_end_frame_number(num_samples) - frames_to_skip
        if total_frames <= 0:
            self.external_broadcast("Unable to generate video. Start Time is after the end of the case.")
            return

        # start the animation
        ani = animation.FuncAnimation(fig, run_animation, repeat=False, frames=total_frames, interval=self.processingSettings.T_fast * 1000)
        if not self.do_save_animation:
            plt.show()
        else:
            file_ending = self.get_ouput_file_ending()
            writer = None
            if file_ending == 'gif':
                writer = animation.PillowWriter(fps=self.graphicsSettings.renderSettings.fps, metadata=dict(artist='Daniel J. Vickers'), bitrate=-1)
            elif file_ending == 'mp4':
                writer = animation.FFMpegWriter(fps=self.graphicsSettings.renderSettings.fps) #, extra_args=['-vcodec', 'libx264'])
            else:
                self.external_broadcast("ERROR: {file_ending} is not a valid output file format for animations", 'except')
                return

            self.external_broadcast(f"Saving Initial Animation to {self.outputFileName}")
            if file_ending == 'mp4' and self.do_add_audio_to_animation:
                if not tk_progress_bar:  # uses tqdm if there is no external progress bar in the GUI
                    with tqdm(total=total_frames, desc='Saving video') as progress_bar:
                        ani.save('temp.mp4', writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=lambda i, n: progress_bar.update(1))
                else:
                    tk_progress_bar.set_bar_max(total_frames)
                    ani.save(self.outputFileName, writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=tk_progress_bar.update_bar)

                self.external_broadcast(f"Generating Sonicated Audio")
                audio_rate = int(self.eegData.sampleRate * self.processingSettings.T_fast * self.graphicsSettings.renderSettings.fps)
                scaled_data = np.int16(self.eegData.data / np.max(np.abs(self.eegData.data)) * int(2 ** 15))
                wavfile.write('temp.wav', audio_rate, scaled_data)

                audio = mp.AudioFileClip('temp.wav')
                video1 = mp.VideoFileClip('temp.mp4')
                final_duration = min(audio.duration, video1.duration)
                video2 = video1.with_duration(final_duration)
                video2.write_videofile(self.outputFileName)
                final_video = video2.with_audio(audio.with_duration(final_duration))
                self.external_broadcast("Attaching Audio to Video")
                final_video.write_videofile(self.outputFileName)
                self.external_broadcast("Cleaning Up")
                os.remove('temp.mp4')
                os.remove('temp.wav')
            else:
                if not tk_progress_bar:  # uses tqdm if there is no external progress bar in the GUI
                    with tqdm(total=total_frames, desc='Saving video') as progress_bar:
                        ani.save(self.outputFileName, writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=lambda i, n: progress_bar.update(1))
                else:
                    tk_progress_bar.set_bar_max(total_frames)
                    ani.save(self.outputFileName, writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=tk_progress_bar.update_bar)
            self.external_broadcast("Complete", 'success')
        return

    def create_dsa_image(self, time):
        start_time_seconds = time * 60.
        try:
            dsa_array = self.eegData.get_dsa_frame(
                self.processingSettings.T_fast, 
                self.processingSettings.T_slow,
                self.graphicsSettings.frequencyDomainParameters.max_plot_frequency,
                start_time_seconds,
                channel_number=self.processingSettings.channel_number)
        except:
            self.external_broadcast("Unable to generate DSA Frame. Consider Checking the Start Time.", "error")
            return

        fig = plt.figure(figsize=self.graphicsSettings.renderSettings.figure_size)
        ax = plt.gca()
        sed_plot = plt.imshow(dsa_array, cmap='jet',
                                vmin=self.graphicsSettings.frequencyDomainParameters.min_db_power,
                                vmax=self.graphicsSettings.frequencyDomainParameters.max_db_power,
                                aspect='auto', interpolation='bilinear',
                                extent=[-int(self.processingSettings.T_slow / 60), 0,
                                self.graphicsSettings.frequencyDomainParameters.max_plot_frequency, 0])
        cbar = plt.colorbar()
        cbar.set_label('Power (dB)', fontsize=self.graphicsSettings.renderSettings.font_size)
        ax.set_yticks(np.array([-0. + i*self.graphicsSettings.frequencyDomainParameters.max_plot_frequency/4 for i in range(5)]))
        ax.set_yticklabels(np.arange(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency, -0.5,
                                        -int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency / 4)))
        plt.xlabel('Time (min)', fontsize=self.graphicsSettings.renderSettings.font_size)
        plt.ylabel('Frequency (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
        plt.tight_layout()
        plt.savefig(self.outputFileName, dpi=self.graphicsSettings.renderSettings.dpi)
        self.external_broadcast("Image Generated", "success")


    def create_spectrogram_animation(self, time_min, script, height_floor=-10, tk_progress_bar=None):
        # set up the animation variables and function
        # TODO :: Add an ability to control the rotation speed. Angles/second seem like a good unit
        def run_spec_animation(i):
            nonlocal script
            for scene in script:
                if scene["begin"] <= i <= scene['end']:
                    if scene['function'] == 'rotate':
                        window = scene['end'] - scene['begin']
                        self.rotate_to_angle(ax, i - scene['begin'], window, scene['start'], scene['stop'])
                    break

        time_seconds = time_min * 60
        # fetch the EEG data
        dsa_array = self.eegData.get_dsa_frame(
                self.processingSettings.T_fast, 
                self.processingSettings.T_slow,
                self.graphicsSettings.frequencyDomainParameters.max_plot_frequency,
                time_seconds,
                channel_number=self.processingSettings.channel_number)
        data = np.flip(dsa_array, 0)

        # adjust the height of the data
        data = data - (self.graphicsSettings.frequencyDomainParameters.min_db_power + height_floor)
        for i in range(len(data)):
            for j in range(len(data[i])):
                if data[i][j] < 0:
                    data[i][j] = 0.

        # create the mesh grid
        t = np.linspace(0,
            self.processingSettings.T_slow,
            int(self.processingSettings.T_slow / self.processingSettings.T_fast) ) / 60.
        f = np.linspace(0,
            self.graphicsSettings.frequencyDomainParameters.max_plot_frequency,
            int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency * self.processingSettings.T_fast) )
        T, F = np.meshgrid(t, f)

         # Create vertices
        vertices = np.zeros((len(t) * len(f), 3))
        vertices[:, 0] = T.ravel()
        vertices[:, 1] = F.ravel()
        vertices[:, 2] = data.ravel()

        # create the image
        ax = plt.figure(figsize=self.graphicsSettings.renderSettings.figure_size,
            dpi=self.graphicsSettings.renderSettings.dpi).add_subplot(projection='3d')
        self.external_broadcast("Plotting Triangle Mesh", "info")
        ax.plot_trisurf(T.ravel(), F.ravel(), data.ravel(), 
                        cmap='jet',
                        vmin=0,
                        vmax=self.graphicsSettings.frequencyDomainParameters.max_db_power - 
                            self.graphicsSettings.frequencyDomainParameters.min_db_power - height_floor,
                        lw=0)
        plt.xlabel('time (min)', fontsize=self.graphicsSettings.renderSettings.font_size)
        plt.ylabel('frequency (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
        ax.set_zlabel('power (dB)', fontsize=self.graphicsSettings.renderSettings.font_size)

        # set the view angle and total frame amount
        start_angle = script[0]["start"]
        ax.view_init(elev=start_angle[0], azim=start_angle[1])
        total_frames = script[-1]["end"]+1

        # start the animation
        fig = plt.gcf()
        ani = animation.FuncAnimation(fig, run_spec_animation, repeat=False, frames=total_frames, interval=30)

        file_ending = self.get_ouput_file_ending()
        writer = None
        if file_ending == 'gif':
            writer = animation.PillowWriter(fps=self.graphicsSettings.renderSettings.fps, metadata=dict(artist='Daniel J. Vickers'), bitrate=-1)
        elif file_ending == 'mp4':
            writer = animation.FFMpegWriter(fps=self.graphicsSettings.renderSettings.fps) #, extra_args=['-vcodec', 'libx264'])
        else:
            self.external_broadcast("ERROR: {file_ending} is not a valid output file format for animations", 'except')
            return

        self.external_broadcast(f"Saving Initial Animation to {self.outputFileName}")

        if not tk_progress_bar:  # uses tqdm if there is no external progress bar in the GUI
            with tqdm(total=total_frames, desc='Saving video') as progress_bar:
                ani.save(self.outputFileName, writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=lambda i, n: progress_bar.update(1))
        else:
            tk_progress_bar.set_bar_max(total_frames)
            ani.save(self.outputFileName, writer=writer, dpi=self.graphicsSettings.renderSettings.dpi, progress_callback=tk_progress_bar.update_bar)
        self.external_broadcast("Complete", 'success')
        return

    
    def create_spectrogram_image(self, time_min, angle=(30, 45), height_floor=-10):
        time_seconds = _time_min * 60
        # fetch the EEG data
        dsa_array = self.eegData.get_dsa_frame(
                self.processingSettings.T_fast, 
                self.processingSettings.T_slow,
                self.graphicsSettings.frequencyDomainParameters.max_plot_frequency,
                time_seconds,
                channel_number=self.processingSettings.channel_number)
        data = np.flip(dsa_array, 0)

        # adjust the height of the data
        data = data - (self.graphicsSettings.frequencyDomainParameters.min_db_power + height_floor)
        for i in range(len(data)):
            for j in range(len(data[i])):
                if data[i][j] < 0:
                    data[i][j] = 0.

        # create the mesh grid
        t = np.linspace(0,
            self.processingSettings.T_slow,
            int(self.processingSettings.T_slow / self.processingSettings.T_fast) ) / 60.
        f = np.linspace(0,
            self.graphicsSettings.frequencyDomainParameters.max_plot_frequency,
            int(self.graphicsSettings.frequencyDomainParameters.max_plot_frequency * self.processingSettings.T_fast) )
        T, F = np.meshgrid(t, f)

         # Create vertices
        vertices = np.zeros((len(t) * len(f), 3))
        vertices[:, 0] = T.ravel()
        vertices[:, 1] = F.ravel()
        vertices[:, 2] = data.ravel()

        # create the image
        ax = plt.figure(figsize=self.graphicsSettings.renderSettings.figure_size,
            dpi=self.graphicsSettings.renderSettings.dpi).add_subplot(projection='3d')
        self.external_broadcast("Plotting Triangle Mesh", "info")
        ax.plot_trisurf(T.ravel(), F.ravel(), data.ravel(), 
                        cmap='jet',
                        vmin=0,
                        vmax=self.graphicsSettings.frequencyDomainParameters.max_db_power - 
                            self.graphicsSettings.frequencyDomainParameters.min_db_power - height_floor,
                        lw=0)
        plt.xlabel('time (min)', fontsize=self.graphicsSettings.renderSettings.font_size)
        plt.ylabel('frequency (Hz)', fontsize=self.graphicsSettings.renderSettings.font_size)
        ax.set_zlabel('power (dB)', fontsize=self.graphicsSettings.renderSettings.font_size)

        # set the view angle and save
        ax.view_init(elev=angle[0], azim=angle[1])
        plt.savefig(self.outputFileName)
        self.external_broadcast("Image Generated", 'success')
