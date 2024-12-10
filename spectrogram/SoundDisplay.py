import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from matplotlib import cm
import pydub
import moviepy as mp
import os
import math
import tqdm


import warnings
warnings.filterwarnings('ignore')


class TimeDomainParameters:
    time_amplitude = 40
    do_time_domain_plot = True


class FrequencyDomainParameters:
    min_db_power = 100
    max_db_power = 130
    outside_db_to_plot = 10
    max_plot_frequency = 1200
    do_frequency_domain_plot = True
    do_frequency_domain_as_colored_scatter = True


class GraphicsSettings:
    figure_size = [10, 10]
    font_size = 18
    dpi = 100
    do_render_plot_axis = True


class SoundDisplay:
    do_save_animation = False
    do_add_audio_to_animation = False
    do_spectrogram_plot = True
    do_spectral_edge_frequency = False
    do_plot_spectral_edge_on_spectrogram = False
    input_file_name = ''
    output_file_name = ''
    fps = 40
    T_slow = 10
    time_domain_parameters = TimeDomainParameters()
    frequency_domain_parameters = FrequencyDomainParameters()
    graphics_settings = GraphicsSettings()
    sample_rate = 1
    data = []
    total_frames = -1

    def __init__(self, input_file_name='', num_channels=2):
        if input_file_name != '':
            self.load_data_from_file(input_file_name, num_channels=num_channels)

    def load_data_from_file(self, file_name, num_channels=2):
        file_ending = file_name.split('.')[-1]
        if file_ending == 'mp3':
            try:
                sound = pydub.AudioSegment.from_mp3(file_name)
                data = sound.get_array_of_samples()
                self.data = np.array(data[::num_channels])  # what is going on with factor of 2 here?
                self.sample_rate = sound.frame_rate
            except:
                print('ERROR: Failed to open file ' + str(file_name))
        elif file_ending == 'm4a' or file_ending == 'wav':
            try:
                sound = pydub.AudioSegment.from_file(file_name)
                data = sound.get_array_of_samples()
                self.data = np.array(data[::num_channels])
                self.sample_rate = sound.frame_rate
            except:
                print('ERROR: Failed to open file ' + str(file_name))
        else:
            print(str(file_ending) + ' is not a supported file type')
            return
        self.input_file_name = file_name

    def create_plot_from_data(self):
        # check if we should return immediately
        if self.do_save_animation and self.output_file_name == '':
            print('No output filename set')
            return

        # define the animation function
        def run_animation(i):
            y = np.array(self.data[num_samples * i:num_samples * (i + 1)])
            if self.time_domain_parameters.do_time_domain_plot:
                fast_time_line.set_data(t, np.real(y) / 1000)

            y_f_linear = abs(np.fft.fftshift(np.fft.fft(y)))
            spectral_edge = np.fft.ifftshift(f)[num_frequency_points]
            if self.do_spectral_edge_frequency or self.do_plot_spectral_edge_on_spectrogram:
                y_in_sum = np.fft.ifftshift(y_f_linear)[:num_frequency_points]
                y_in_sum[0] = 0
                total_power = sum(y_in_sum)
                for i in range(len(y_in_sum)):
                    if sum(y_in_sum[:i]) > total_power * 0.9:
                        spectral_edge = np.fft.ifftshift(f)[i-1]
                        break
                if self.do_spectral_edge_frequency:
                    spectral_edge_data = np.roll(sef_line.get_ydata(), -1, axis=0)
                    spectral_edge_data[-1] = spectral_edge
                    sef_line.set_ydata(spectral_edge_data)
            for i in range(1, len(y_f_linear)):
                if y_f_linear[i] == 0.:
                    y_f_linear[i] = 1e-16
            y_f = 20 * np.log10(y_f_linear)

            if self.frequency_domain_parameters.do_frequency_domain_plot:
                if self.frequency_domain_parameters.do_frequency_domain_as_colored_scatter:
                    scatter_data = np.column_stack((f, y_f))
                    frequency_line.set_offsets(scatter_data)
                    normalized_data = plt.Normalize(self.frequency_domain_parameters.min_db_power,
                                                    self.frequency_domain_parameters.max_db_power)(y_f)
                    colors = cm.jet(normalized_data)
                    frequency_line.set_color(colors)
                else:
                    frequency_line.set_data(f, np.real(y_f))

            if self.do_spectrogram_plot:
                sed_array = sed_plot.get_array().transpose()
                sed_array = np.roll(sed_array, -1, axis=0)
                if self.do_plot_spectral_edge_on_spectrogram:
                    spectral_edge_data = np.roll(sef_on_spec.get_ydata(), -1, axis=0)
                    spectral_edge_data[-1] = self.frequency_domain_parameters.max_plot_frequency - spectral_edge
                    sef_on_spec.set_ydata(spectral_edge_data)
                    # y_f[np.where(f == spectral_edge)] = 'nan'
                sed_array[-1] = np.flip(np.fft.ifftshift(y_f)[:len(sed_array[0])])
                sed_plot.set_array(sed_array.transpose())

        # initialize some variables used in the plot generation
        T_fast = 1 / self.fps  # fast time period in seconds
        num_samples = int(self.sample_rate * T_fast)
        t = np.array([i / self.sample_rate for i in range(num_samples)])
        f = np.fft.fftshift(np.fft.fftfreq(len(t), d=1 / self.sample_rate))
        num_frequency_points = 0
        for f_sample in f:
            if 0. <= f_sample <=self.frequency_domain_parameters.max_plot_frequency:
                num_frequency_points += 1
        if self.total_frames < 0:
            self.total_frames = int(len(self.data) / num_samples)

        # start the outline of the basic plots
        fig = plt.figure(figsize=self.graphics_settings.figure_size)
        total_number_plot = 0
        t_index, f_index, s_index, sef_index = -1, -1, -1, -1
        if self.time_domain_parameters.do_time_domain_plot:
            t_index = total_number_plot
            total_number_plot += 1
        if self.frequency_domain_parameters.do_frequency_domain_plot:
            f_index = total_number_plot
            total_number_plot += 1
        if self.do_spectrogram_plot:
            s_index = total_number_plot
            total_number_plot += 1
        if self.do_spectral_edge_frequency:
            sef_index = total_number_plot
            total_number_plot += 1
        if total_number_plot == 0:
            print("ERROR: No plots configured to display")
            return

        fast_time_line = 0
        frequency_line = 0
        sed_plot = 0
        sef_line = 0
        sef_on_spec = 0
        # create a subplot for each type of plot specified
        for i in range(total_number_plot):
            ax3 = plt.subplot(total_number_plot, 1, int(i+1))
            if i == t_index:
                if self.time_domain_parameters.do_time_domain_plot:
                    fast_time_line = plt.plot([])[0]
                    plt.xlabel('Time (s)', fontsize=self.graphics_settings.font_size)
                    plt.ylabel('Pressure (mN/m$^2$)', fontsize=self.graphics_settings.font_size)
                    plt.xlim([0, T_fast])
                    plt.ylim([-self.time_domain_parameters.time_amplitude, self.time_domain_parameters.time_amplitude])
            elif i == f_index:
                if self.frequency_domain_parameters.do_frequency_domain_plot:
                    if self.frequency_domain_parameters.do_frequency_domain_as_colored_scatter:
                        frequency_line = plt.scatter(np.zeros(int(self.frequency_domain_parameters.max_plot_frequency * T_fast)),
                                                     np.zeros(int(self.frequency_domain_parameters.max_plot_frequency * T_fast)),
                                                     cmap='jet', vmin=self.frequency_domain_parameters.min_db_power,
                                                     vmax=self.frequency_domain_parameters.max_db_power)
                    else:
                        frequency_line = plt.plot([])[0]
                    plt.xlim([0, self.frequency_domain_parameters.max_plot_frequency])
                    plt.ylim([self.frequency_domain_parameters.min_db_power - self.frequency_domain_parameters.outside_db_to_plot,
                              self.frequency_domain_parameters.max_db_power + self.frequency_domain_parameters.outside_db_to_plot])
                    plt.xlabel('Frequency (Hz)', fontsize=self.graphics_settings.font_size)
                    plt.ylabel('Power (dB)', fontsize=self.graphics_settings.font_size)
            elif i == s_index:
                if self.do_spectrogram_plot:
                    empty_sed_array = np.array([np.zeros(num_frequency_points) for i in range(int(self.T_slow / T_fast))])
                    sed_plot = plt.imshow(empty_sed_array.transpose(), cmap='jet',
                                          vmin=self.frequency_domain_parameters.min_db_power,
                                          vmax=self.frequency_domain_parameters.max_db_power,
                                          aspect='auto', interpolation='bilinear',
                                          extent=[-10, 0, self.frequency_domain_parameters.max_plot_frequency, 0])
                    if self.graphics_settings.do_render_plot_axis:
                        cbar = plt.colorbar()
                        cbar.set_label('Power (dB)', fontsize=self.graphics_settings.font_size)
                        ax3.set_yticks(np.array([-0. + i*self.frequency_domain_parameters.max_plot_frequency/4 for i in range(5)]))
                        ax3.set_yticklabels(np.arange(self.frequency_domain_parameters.max_plot_frequency, -0.5,
                                                      -int(self.frequency_domain_parameters.max_plot_frequency / 4)))
                        plt.xlabel('Time (s)', fontsize=self.graphics_settings.font_size)
                        plt.ylabel('Frequency (Hz)', fontsize=self.graphics_settings.font_size)
                    else:
                        ax3.set_yticks(np.array([]))
                        ax3.set_xticks(np.array([]))
                        plt.xlabel('Time', fontsize=self.graphics_settings.font_size)
                        plt.ylabel('Frequency', fontsize=self.graphics_settings.font_size)
                    if self.do_plot_spectral_edge_on_spectrogram:
                        negative_times = [-self.T_slow + i * T_fast for i in range(int(self.T_slow / T_fast))]
                        sef_on_spec = ax3.plot(negative_times, [self.frequency_domain_parameters.max_plot_frequency
                                                                for i in range(int(self.T_slow / T_fast))],
                                               color='white', linewidth=3)[0]
            elif i == sef_index:
                if self.do_spectral_edge_frequency:
                    negative_times = [-self.T_slow + i * T_fast for i in range(int(self.T_slow / T_fast))]
                    sef_line = plt.plot(negative_times, [0 for i in range(int(self.T_slow / T_fast))])[0]
                    plt.xlabel('Time (s)', fontsize=self.graphics_settings.font_size)
                    plt.ylabel('SEF (Hz)', fontsize=self.graphics_settings.font_size)
                    plt.ylim([0, self.frequency_domain_parameters.max_plot_frequency])
                    plt.xlim([-self.T_slow, 0])
        plt.tight_layout()

        # start the animation
        ani = animation.FuncAnimation(fig, run_animation, repeat=False, frames=self.total_frames, interval=T_fast * 1000)
        if not self.do_save_animation:
            plt.show()
        else:
            file_ending = self.output_file_name.split('.')[-1]
            writer = 0
            if file_ending == 'gif':
                writer = animation.PillowWriter(fps=self.fps, metadata=dict(artist='Daniel J. Vickers'), bitrate=-1)
            elif file_ending == 'mp4':
                writer = animation.FFMpegWriter(fps=self.fps)
            else:
                print('ERROR: ' + file_ending + ' is not a valid output file format')
                return

            if file_ending == 'mp4' and self.do_add_audio_to_animation:
                with tqdm.tqdm(total=self.total_frames, desc='Saving video') as progress_bar:
                    ani.save('temp.mp4', writer=writer, dpi=self.graphics_settings.dpi, progress_callback=lambda i, n: progress_bar.update(1))
                audio = mp.AudioFileClip(self.input_file_name)
                video1 = mp.VideoFileClip('temp.mp4')
                final_duration = min(audio.duration, video1.duration)
                video2 = video1.with_duration(final_duration)
                video2.write_videofile(self.output_file_name)
                final_video = video2.with_audio(audio.with_duration(final_duration))
                final_video.write_videofile(self.output_file_name)
                os.remove('temp.mp4')
            else:
                ani.save(self.output_file_name, writer=writer, dpi=self.graphics_settings.dpi)
        return

