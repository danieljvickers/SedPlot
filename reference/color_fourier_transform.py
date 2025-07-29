import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import scipy.ndimage
import pyedflib
import math
from matplotlib import cm
from matplotlib import colors

'''
THE OUTPUT OF THIS FILE IS A COLORED FOURIER TRANSFORM, WHICH I WOULD LIKE TO HAVE ADDED TO THE DSA SPLIT IMAGE
'''

def interpolate_signal(sig, rate):
    f_sig = np.fft.fft(sig)
    f_out = np.zeros(int(len(f_sig) * rate), dtype=complex)
    f_out[:int(len(sig) / 2)] = f_sig[:int(len(sig) / 2)]
    f_out[-int(len(sig) / 2):] = f_sig[-int(len(sig) / 2):]
    return np.fft.ifft(f_out)


def main():
    label = 'eeg'

    file_name = 'data/EEG_240505_084705.edf'
    signals, signal_headers, header = pyedflib.highlevel.read_edf(file_name)
    sample_rate = signal_headers[0]['sample_rate']
    data = signals[0]  # indexed by channel number

    period = 10
    num_samples = int(math.floor(sample_rate * period))

    start_frame = 80
    start_sample = num_samples * start_frame
    sig = np.array(data[start_sample:start_sample + num_samples], dtype=complex)

    freq = np.fft.fftshift(np.fft.fftfreq(len(sig), 1. / sample_rate))
    f_sig = np.abs(np.fft.fftshift(np.fft.fft(sig)))

    f_sig = scipy.ndimage.median_filter(f_sig, size=3)

    norm_sig = f_sig / np.max(np.abs(f_sig))

    plt.figure(figsize=(10, 10), dpi=100)
    plt.plot(freq, 20. * np.log10(np.abs(norm_sig)), linewidth=3, color='black')
    plt.xlim((0, 40))
    plt.ylim(-50., 4.)
    plt.xlabel('frequency (Hz)', fontsize=18)

    # plt.savefig('dft_figures/' + label + '_freq.png')

    '''plt.figure(figsize=(10, 10), dpi=100)
    plt.scatter(freq, 20. * np.log10(np.abs(norm_sig)), c=20. * np.log10(np.abs(norm_sig)), vmax=0, vmin=-40, cmap=cm.jet)
    plt.xlim((0, 40))
    plt.ylim(-50., 4.)
    plt.xlabel('frequency (Hz)', fontsize=18)'''

    plt.figure(figsize=(10, 10), dpi=100)
    log_sig = 20. * np.log10(np.abs(norm_sig))
    cNorm  = colors.Normalize(vmin=-40, vmax=0)
    ref_cm = cm.ScalarMappable(norm=cNorm, cmap='jet')

    for i in range(len(log_sig) - 1):
        left = log_sig[i]
        right = log_sig[i+1]
        mid = 0.5 * (left + right)
        norm_mid = max(min(1, (mid + 40) / 40), 0)
        color = ref_cm.to_rgba(mid)
        plt.plot((freq[i], freq[i+1]), (left, right), color=color, linewidth=3)
    # plt.scatter(freq, 20. * np.log10(np.abs(norm_sig)), c=20. * np.log10(np.abs(norm_sig)), vmax=0, vmin=-40, cmap=cm.jet)
    plt.xlim((0, 40))
    plt.ylim(-50., 4.)
    plt.xlabel('frequency (Hz)', fontsize=18)

    plt.savefig('dft_figures/' + label + '_color_freq.png')

    interpolation_rate = 10
    sig = interpolate_signal(sig, interpolation_rate)
    time = np.array([i / sample_rate / interpolation_rate for i in range(len(sig))])
    
    plt.figure(figsize=(10, 10), dpi = 100)
    plt.plot(time, np.real(sig), linewidth=3, color='blue')
    plt.xlim([0, 4])
    plt.xlabel('time (s)', fontsize=18)
     
    # plt.savefig('dft_figures/' + label + '_time.png')

    plt.show()


if __name__ == '__main__':
    main()
