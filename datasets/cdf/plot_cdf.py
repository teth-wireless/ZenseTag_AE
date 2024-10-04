import numpy as np
import scipy
import os
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from collections import defaultdict

# select the type of CDF that has to be plotted here
# typ = "dmrt"
typ = "phase"

cwd = os.getcwd()
mat_dir = os.path.join(cwd,"data")

def pair_files(files):
    # Dictionary to hold base names and their associated files
    file_dict = defaultdict(list)
    
    # Loop through all files and group by their base name (before '_diff' or '.mat')
    for file in files:
        # Remove '_diff' and '.mat' to get the base name
        base_name = file.replace('_diff', '').replace('.mat', '')
        # Add the file to the corresponding base name's list
        file_dict[base_name].append(file)
    
    # Create a list of paired files
    paired_files = [file_list for file_list in file_dict.values() if len(file_list) == 2]
    
    return paired_files

files = [os.path.join(mat_dir,f) for f in os.listdir(mat_dir) if os.path.isfile(os.path.join(mat_dir, f))]
files = pair_files(files)

dzt = []
cotag = []

# Function to clean phases and fix phase shifts
def clean_phases(phase_list):
    cleaned = []
    for phase in phase_list:
        if phase > 270:
            cleaned.append(abs(phase - 360))
        elif phase > 135:
            cleaned.append(abs(phase - 180))
        else:
            cleaned.append(abs(phase))
    return np.array(cleaned)

# Function to calculate DTW alignment between two sequences
def dynamic_time_warp(signal1, signal2):
    _, path = fastdtw(signal1, signal2)
    aligned_signal1 = [signal1[i] for i, j in path]
    aligned_signal2 = [signal2[j] for i, j in path]
    return np.array(aligned_signal1), np.array(aligned_signal2)

def extract_phase_data(file_path):
    """
    Extract phase data in degrees from the .mat file and
    segregate it channel wise
    """
    data = scipy.io.loadmat(file_path)
    if "diff" not in file_path:
        phases = data['raw_phases'][0]
        channels = data['channels'][0]
    else:
        phases = data['raw_phases_diff'][0]
        channels = data['channels_diff'][0]
    phase_data_by_channel = {}
    for i, channel in enumerate(channels):
        if channel not in phase_data_by_channel:
            phase_data_by_channel[channel] = []
        phase_data_by_channel[channel].append(phases[i])

    return phase_data_by_channel

def get_phase_diff(phases_1, phases_2, raw):
    """
    Process all .mat files in a directory, calculate DTW distances, and generate a heatmap.
    """
    sensed_phase = []
    common_channels = set(phases_1.keys()) & set(phases_2.keys())
    
    for idx, channel in enumerate(common_channels):
        phase_1 = np.array(phases_1[channel])
        phase_2 = np.array(phases_2[channel])

        if raw:
            # Plot raw cleaned phases if raw_flag is True
            aligned_phase_1, aligned_phase_2 = phase_1, phase_2
        else:
            aligned_phase_1, aligned_phase_2 = dynamic_time_warp(phase_1, phase_2)

        # Find the minimum length of the two arrays
        min_length = min(len(aligned_phase_1), len(aligned_phase_2))

        # Truncate both arrays to the same length
        aligned_phase_1 = aligned_phase_1[:min_length]
        aligned_phase_2 = aligned_phase_2[:min_length]

        # Calculate phase difference
        phase_diff = np.abs(aligned_phase_1 - aligned_phase_2)
        # if not raw:
        #     phase_diff = clean_phases(phase_diff)
        phase_diff = clean_phases(phase_diff)

        sensed_phase.extend(phase_diff)

    return sensed_phase

def extract_rssi(file_path):
    data = scipy.io.loadmat(file_path)
    rssi = data['rssis'][0]
    return np.array(rssi)

def get_dmrt(rssi_1, rssi_2):
    min_length = min(len(rssi_1), len(rssi_2))
    rssi_1 = rssi_1[:min_length]
    rssi_2 = rssi_2[:min_length]

    dmrt = np.abs(rssi_1 - rssi_2)

    return dmrt


for f in files:
    if "cotags" not in f[0]:
        if typ == "phase":
            dzt_phases_1 = extract_phase_data(f[0])
            dzt_phases_2 = extract_phase_data(f[1])
            dzt.extend(get_phase_diff(dzt_phases_1,dzt_phases_2,raw=False))

        if typ == "dmrt":
            dzt_rssi_1 = extract_rssi(f[0])
            dzt_rssi_2 = extract_rssi(f[1])
            dzt.extend(get_dmrt(dzt_rssi_1,dzt_rssi_2))
    else:
        if typ == "phase":
            cot_phases_1 = extract_phase_data(f[0])
            cot_phases_2 = extract_phase_data(f[1])
            cotag.extend(get_phase_diff(cot_phases_1,cot_phases_2,raw=True))

        if typ == "dmrt":
            cot_rssi_1 = extract_rssi(f[0])
            cot_rssi_2 = extract_rssi(f[1])
            cotag.extend(get_dmrt(cot_rssi_1,cot_rssi_2))

def plot_cdf(array_1, array_2):
    # Sort the arrays to calculate CDF
    sorted_array_1 = np.sort(array_1)
    sorted_array_2 = np.sort(array_2)
    
    # Calculate the CDF values for each array
    cdf_array_1 = np.arange(1, len(sorted_array_1)+1) / len(sorted_array_1)
    cdf_array_2 = np.arange(1, len(sorted_array_2)+1) / len(sorted_array_2)
    
    # Plotting the CDF for both arrays
    plt.figure()
    plt.plot(sorted_array_1, cdf_array_1, label='ZenseTag', linewidth=5)
    plt.plot(sorted_array_2, cdf_array_2, label='Colocated Tags', linewidth=5)

    # Mark a horizontal line at y = 0.5 (for CDF = 0.5)
    plt.axhline(y=0.5, color='r', linestyle='--', label="y = 0.5")

    # Calculate the intercepts for both arrays where CDF is approximately 0.5
    idx_1 = np.searchsorted(cdf_array_1, 0.5)  # Find index where CDF ~ 0.5 for array 1
    intercept_x1 = sorted_array_1[idx_1]
    
    idx_2 = np.searchsorted(cdf_array_2, 0.5)  # Find index where CDF ~ 0.5 for array 2
    intercept_x2 = sorted_array_2[idx_2]
    
    # Plot and annotate the intercepts
    plt.scatter([intercept_x1], [0.5], color='blue')
    plt.text(intercept_x1, 0.5, f"{intercept_x1:.2f}", verticalalignment='bottom', horizontalalignment='right')
    
    plt.scatter([intercept_x2], [0.5], color='green')
    plt.text(intercept_x2, 0.5, f"{intercept_x2:.2f}", verticalalignment='bottom', horizontalalignment='right')

    if typ == "phase":
        plt.title(f"CDF for Differential Phase")
        plt.xlabel("Differential Phase (degrees)")
    elif typ == "dmrt":
        plt.title(f"CDF for Differential RSSI")
        plt.xlabel("Differential RSSI (dB)")
    
    plt.ylabel("CDF")
    plt.xticks()
    plt.yticks()
    plt.grid(True)
    plt.legend()

    plt.savefig(f'cdf_{typ}.png') 

    plt.show()

plot_cdf(dzt,cotag)