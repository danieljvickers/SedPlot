import numpy

from spectrogram.SoundDisplay import SoundDisplay
from spectrogram.EegDisplay import EegDisplay
import os

os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"


def gen_all_in_dir():
    files = ['c_scale.mp3'] # os.listdir("C:\\Users\\Daniel\\Documents\\eeg_video\\sounds_clips\\")
    # files = os.listdir("C:\\Users\\Daniel\\Documents\\eeg_video\\sounds_clips\\")
    for audio_file in files:
        file = audio_file.split('.')[0]
        print("File Name: " + audio_file)
        spec_display = SoundDisplay()
        spec_display.load_data_from_file("C:\\Users\\Daniel\\Documents\\eeg_video\\sounds_clips\\" + file + ".mp3")
        spec_display.output_file_name = "C:\\Users\\Daniel\\Documents\\eeg_video\\sound_videos\\" + file + "_time.mp4"
        spec_display.frequency_domain_parameters.max_plot_frequency = 500
        spec_display.do_add_audio_to_animation = True
        spec_display.do_save_animation = True
        spec_display.do_spectrogram_plot = False
        spec_display.frequency_domain_parameters.do_frequency_domain_plot = False
        spec_display.create_plot_from_data()

        spec_display.frequency_domain_parameters.do_frequency_domain_plot = True
        spec_display.frequency_domain_parameters.do_frequency_domain_as_colored_scatter = False
        spec_display.output_file_name = "C:\\Users\\Daniel\\Documents\\eeg_video\\sound_videos\\" + file + "_freq.mp4"
        spec_display.create_plot_from_data()

        spec_display.frequency_domain_parameters.do_frequency_domain_as_colored_scatter = True
        spec_display.output_file_name = "C:\\Users\\Daniel\\Documents\\eeg_video\\sound_videos\\" + file + "_freq_color.mp4"
        spec_display.create_plot_from_data()

        spec_display.do_spectrogram_plot = True
        spec_display.output_file_name = "C:\\Users\\Daniel\\Documents\\eeg_video\\sound_videos\\" + file + "_spec.mp4"
        spec_display.create_plot_from_data()

        print('Done with file: ' + audio_file)


def gen_specific_file():
    # C:\Users\Daniel\Documents\scripts\music_spectrogram\small_animations\open_eeg
    # spec_display = EegDisplay(input_file_name="EEG_240420_075441.edf", channel_number=0)  # this is the file we are loading
    spec_display = EegDisplay(input_file_name="../small_animations/open_eeg/EEG/Propofol - Burst and Isoelectric/EEG_240417_120540.edf", channel_number=3)  # this is the file we are loading
    spec_display.output_file_name = "test.mp4"  # output file name
    spec_display.do_save_animation = True
    spec_display.do_spectrogram_plot = True
    spec_display.do_plot_spectral_edge_on_spectrogram = False
    spec_display.frequency_domain_parameters.do_frequency_domain_plot = False
    spec_display.time_domain_parameters.do_time_domain_plot = False
    spec_display.do_spectral_edge_frequency = False
    spec_display.do_add_audio_to_animation = True
    spec_display.graphics_settings.figure_size = (16, 9)
    spec_display.fps = 30
    spec_display.T_slow = 20*60
    # spec_display.graphics_settings.dpi = 250  # uncomment this to save in 4k
    spec_display.do_add_audio_to_animation = True

    spec_display.frequency_domain_parameters.max_db_power = 65
    spec_display.frequency_domain_parameters.min_db_power = 20

    spec_display.create_plot_from_data()


def gen_audio_spec():
    # C:\Users\Daniel\Documents\scripts\music_spectrogram\small_animations\open_eeg
    spec_display = SoundDisplay(input_file_name=r"bin/freebird.mp3", num_channels=2)  # this is the file we are loading
    spec_display.output_file_name = r"bin/freebird.mp4"  # output file name
    spec_display.do_save_animation = True
    spec_display.do_spectrogram_plot = True
    spec_display.do_plot_spectral_edge_on_spectrogram = False
    spec_display.frequency_domain_parameters.do_frequency_domain_plot = False
    spec_display.time_domain_parameters.do_time_domain_plot = False
    spec_display.do_spectral_edge_frequency = False
    spec_display.do_add_audio_to_animation = True
    spec_display.graphics_settings.figure_size = (16, 9)
    spec_display.fps = 30
    # spec_display.graphics_settings.dpi = 250  # uncomment this to save in 4k
    spec_display.do_add_audio_to_animation = True
    spec_display.graphics_settings.do_render_plot_axis = False
    # spec_display.frequency_domain_parameters.max_plot_frequency = 1800
    spec_display.frequency_domain_parameters.max_plot_frequency = 3000

    spec_display.frequency_domain_parameters.max_db_power = 130
    spec_display.frequency_domain_parameters.min_db_power = 100

    # spec_display.frequency_domain_parameters.max_db_power = 120
    # spec_display.frequency_domain_parameters.min_db_power = 100
    # spec_display.total_frames = 1000

    spec_display.create_plot_from_data()


def gen_all_edf():
    directory = r"C:\Users\Daniel\Documents\eeg_video\0506_data\Root_2000026958_20240505_081711\\"
    files = os.listdir(directory)
    print("Found " + str(len(files)) + " total files")
    spec_display = EegDisplay()
    spec_display.do_save_animation = True
    spec_display.do_spectrogram_plot = True
    spec_display.do_plot_spectral_edge_on_spectrogram = False
    spec_display.frequency_domain_parameters.do_frequency_domain_plot = False
    spec_display.time_domain_parameters.do_time_domain_plot = False
    spec_display.do_spectral_edge_frequency = False
    spec_display.do_add_audio_to_animation = True
    spec_display.graphics_settings.figure_size = (16, 9)
    spec_display.fps = 30
    spec_display.T_slow = 20 * 60
    # spec_display.graphics_settings.dpi = 250  # uncomment this to save in 4k
    spec_display.do_add_audio_to_animation = True

    spec_display.frequency_domain_parameters.max_db_power = 65
    spec_display.frequency_domain_parameters.min_db_power = 20

    for edf_file in files:
        if not edf_file.split('.')[-1] == 'edf':
            continue
        file = edf_file.split('.')[0]
        print("File Name: " + edf_file)
        spec_display.load_data_from_file(directory + edf_file, channel_number=3)
        spec_display.output_file_name = directory + file + ".mp4"

        try:
            spec_display.create_plot_from_data()
        except:
            print('ERROR :: Encountered in file ' + edf_file)
            continue
        print('Done with file: ' + edf_file)


def gen_full_case(directory):
    ch_number = 0
    files = os.listdir(directory)
    files.sort()
    print(files)

    spec_display = EegDisplay()
    spec_display.do_save_animation = True
    spec_display.do_spectrogram_plot = True
    spec_display.do_plot_spectral_edge_on_spectrogram = False
    spec_display.frequency_domain_parameters.do_frequency_domain_plot = False
    spec_display.time_domain_parameters.do_time_domain_plot = False
    spec_display.do_spectral_edge_frequency = False
    spec_display.do_add_audio_to_animation = True
    spec_display.graphics_settings.figure_size = (16, 9)
    spec_display.fps = 30
    spec_display.T_slow = 20 * 60
    # spec_display.graphics_settings.dpi = 250  # uncomment this to save in 4k
    spec_display.do_add_audio_to_animation = True

    db_offset = 5
    spec_display.frequency_domain_parameters.max_db_power = 55 + db_offset
    spec_display.frequency_domain_parameters.min_db_power = 25 + db_offset

    files_to_load = []
    for edf_file in files:
        if edf_file.split('.')[-1] == 'edf':
            files_to_load.append(directory + edf_file)
    # files_to_load.pop(0)
    print("Found " + str(len(files_to_load)) + " total files")
    spec_display.load_array_of_data(files_to_load, channel_number=ch_number)
    spec_display.output_file_name = directory + str(ch_number) + "_full_case.mp4"

    spec_display.create_plot_from_data()
    '''try:
        spec_display.create_plot_from_data()
    except:
        print('ERROR :: Encountered in file ' + edf_file)'''


def gen_series_of_dir_eeg(directory):
    directories = [os.path.join(directory, name) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    print(directories)
    for path in directories:
        gen_full_case(path + '/')


def main():
    gen_full_case(r"/home/dan/Documents/data/lambert_eeg_data/20250212_from_Lambert/")
    # gen_audio_spec()
    # gen_series_of_dir_eeg(r"/home/dan/Documents/data/lambert_eeg_data/")


if __name__ == '__main__':
    main()
