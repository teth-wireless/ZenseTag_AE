#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import scipy
import os
import json

from params import DATA_DIR, STORE_DATA
from params import SENSORS, SENSOR_DEF

data_dir = DATA_DIR
store_data = STORE_DATA
epc_to_save = SENSORS[SENSOR_DEF]["EPC"][0]
epc_to_save_diff = SENSORS[SENSOR_DEF]["EPC"][1]
real_time_data_window = SENSORS[SENSOR_DEF]['real_time_data_window']

def get_raw_data_per_rf(prev_history, real_time = False):
    """
    Retrieves raw data per RF from a given previous history object.

    Parameters:
    - prev_history (object): A previous history object containing data.
    - real_time (boolean): Boolean that defines if real-time data is needed or all-time

    Returns:
    - raw_data (dict): A dictionary containing the raw data per RF.

    Description:
    - The `get_raw_data_per_rf` function takes in a previous history object and extracts the
      necessary data from it. The function retrieves the differences in degrees, RSSIs, channels,
      timestamps, and phases in degrees from the previous history object. 
      If real-time is enabled, then the data is only captured for the last N values
      to make it more real-time oriented. N values correspond to the selected data_window length of data
      where each second of data corresponds to approx 35 data points

    - The extracted data is then stored in a dictionary `raw_data`, with the following keys:
      'timestamps', 'channels', 'diffs', 'rssis', and 'raw_phases'. The corresponding values are
      lists containing the extracted data. 

    - The `raw_data` dictionary is returned as the output of the function.

    Example:
     prev_history = PreviousHistory()
     get_raw_data_per_rf(prev_history)
    {'timestamps': [timestamp_1, timestamp_2, ...],
     'channels': [channel_1, channel_2, ...],
     'diffs': [diff_1, diff_2, ...],
     'rssis': [rssi_1, rssi_2, ...],
     'raw_phases': [phase_1, phase_2, ...]}
    """
    data_window = real_time_data_window * 35
    if (real_time):
      diffs = prev_history.diffs_degrees[-data_window:]
      rssis = prev_history.rssis[-data_window:]
      channels = prev_history.channels[-data_window:]
      timestamps = prev_history.times[-data_window:]
      phases_degrees = prev_history.phases_degrees[-data_window:]
    else:
      diffs = prev_history.diffs_degrees
      rssis = prev_history.rssis
      channels = prev_history.channels
      timestamps = prev_history.times
      phases_degrees = prev_history.phases_degrees

    raw_data = {'timestamps': timestamps,'channels': channels, 'diffs': diffs, 'rssis': rssis, 'raw_phases': phases_degrees}

    return raw_data

def channel_wise_data_per_rf(prev_history, real_time = False):
    """
    Organizes raw data per RF into a channel-wise dictionary.

    Parameters:
    - prev_history (object): A previous history object containing data.
    - real_time (boolean): Boolean that defines if real-time data is needed or all-time

    Returns:
    - rf_data (dict): A dictionary containing channel-wise data per RF.

    Description:
    - The `channel_wise_data_per_rf` function takes in a previous history object and extracts the
      raw data per RF from it using the `get_raw_data_per_rf` function. It then organizes the raw data
      into a channel-wise dictionary.

    - The function creates an empty dictionary `rf_data` to store the channel-wise data. It iterates
      over the channel data and phase data, and for each channel, it appends the corresponding phase
      data to the channel's list in the `rf_data` dictionary.

    - The `rf_data` dictionary has the channel numbers as keys and lists of phase data as values.

    - The `rf_data` dictionary is returned as the output of the function.

    Example:
     prev_history = PreviousHistory()
     channel_wise_data_per_rf(prev_history)
    {1: [phase_1, phase_2, ...],
     2: [phase_3, phase_4, ...],
     ...}
    """

    rf_data = {}

    raw_data = get_raw_data_per_rf(prev_history, real_time)

    channel_data = raw_data['channels']
    phase_data   = raw_data['raw_phases']

    for i in range(len(channel_data)):
        try:
            rf_data[channel_data[i]].append(phase_data[i])
        except:
            rf_data[channel_data[i]] = [phase_data[i]]

    return rf_data

def get_date_string():
    now = datetime.datetime.now()
    date_string = now.strftime("%d%m%Y_%H%M%S")

    return date_string

def store_raw_data_as_json(raw_data, fname):
    """
    Stores raw data as a JSON file.

    Parameters:
    - raw_data (dict): A dictionary containing the raw data.
    - fname (str): The base name for the JSON file.

    Returns:
    - None

    Description:
    - The `store_raw_data_as_json` function takes in a dictionary `raw_data` containing the raw data
      and a string `fname` as the base name for the JSON file. It stores the raw data as a JSON file
      with a timestamp in the filename.

    - The function first generates a date string using the `get_date_string` function. It then creates
      a directory path for the JSON files and constructs the filename using the base name, date string,
      and a suffix.

    - If the `raw_data` dictionary is not empty, the function opens the JSON file in write mode and
      uses the `json.dump` function to write the raw data to the file with an indentation of 4 spaces.

    - If the `raw_data` dictionary is empty, a message "Raw data not captured" is printed.

    - The function does not return any value.

    Example:
     raw_data = {'timestamps': [timestamp_1, timestamp_2, ...],
                    'channels': [channel_1, channel_2, ...],
                    'diffs': [diff_1, diff_2, ...],
                    'rssis': [rssi_1, rssi_2, ...],
                    'raw_phases': [phase_1, phase_2, ...]}
     fname = "data"
     store_raw_data_as_json(raw_data, fname)
    (JSON file named "data_<date>_raw.json" is created with the raw data)
    """

    date_string = get_date_string()

    json_dir = os.path.join(data_dir, "json")
    raw_json_name = fname + "_" + date_string + "_raw" + ".json"
    raw_json_path = os.path.join(json_dir, raw_json_name)

    if (raw_data):
        with open (raw_json_path, "w") as rawfile:
            json.dump(raw_data, rawfile, indent=4)
    else:
        print("Raw data not captured")

def store_channelwise_data_as_json(channel_wise_data, fname):
    """
    Stores channel-wise data as a JSON file.

    Parameters:
    - channel_wise_data (list): A list containing channel-wise data.
    - fname (str): The base name for the JSON file.

    Returns:
    - None

    Description:
    - The `store_channelwise_data_as_json` function takes in a list `channel_wise_data` containing
      channel-wise data and a string `fname` as the base name for the JSON file. It stores the
      channel-wise data as a JSON file with a timestamp in the filename.

    - The function first generates a date string using the `get_date_string` function. It then creates
      a directory path for the JSON files and constructs the filename using the base name, date string,
      and a suffix.

    - If both channel-wise data for RF1 and RF2 are present (i.e., `channel_wise_data[0]` and
      `channel_wise_data[1]` are not empty), the function opens the JSON file in write mode and uses
      the `json.dump` function to write the channel-wise data to the file with an indentation of 4 spaces.

    - If either channel-wise data for RF1 or RF2 is missing, a message "Channelwise data not captured"
      is printed.

    - The function does not return any value.

    Example:
     channel_wise_data = [[channel_1_data], [channel_2_data], ...]
     fname = "data"
     store_channelwise_data_as_json(channel_wise_data, fname)
    (JSON file named "data_<date>.json" is created with the channel-wise data)
    """

    date_string = get_date_string()

    json_dir = os.path.join(data_dir, "json")
    json_name = fname + "_" + date_string + ".json"
    json_path = os.path.join(json_dir, json_name)

    if (channel_wise_data[0] and channel_wise_data[1]):
        with open (json_path, "w") as outfile:
            json.dump(channel_wise_data, outfile, indent=4)
    else:
        print("Channelwise data not captured")

def store_raw_data_as_mat(raw_data, fname):
    """
    Stores raw data as a MATLAB .mat file.

    Parameters:
    - raw_data (list): A list containing raw data for each channel.
    - fname (str): The base name for the MATLAB .mat file.

    Returns:
    - None

    Description:
    - The `store_raw_data_as_mat` function takes in a list `raw_data` containing raw data for each
      channel and a string `fname` as the base name for the MATLAB .mat file. It stores the raw data
      as a MATLAB .mat file with a timestamp in the filename.

    - The function first generates a date string using the `get_date_string` function. It then creates
      a directory path for the MATLAB files and constructs the filenames for each channel using the
      base name, date string, and appropriate suffixes.

    - The function uses the `scipy.io.savemat` function to save the raw data for each channel as separate
      MATLAB .mat files. The `mdict` parameter of `savemat` is set to the raw data for each channel,
      and the files are saved with the appropriate filenames.

    - If the raw data for both channels (i.e., `raw_data[0]` and `raw_data[1]`) is present, the MATLAB
      .mat files are created and saved. Otherwise, a message "Channelwise data not captured" is printed.

    - The function does not return any value.

    Example:
     raw_data = [[channel_1_data], [channel_2_data]]
     fname = "data"
     store_raw_data_as_mat(raw_data, fname)
    (MATLAB .mat files named "data_<date>.mat" and "data_<date>_diff.mat" are created with the raw data)
    """
    
    date_string = get_date_string()

    mat_dir = os.path.join(data_dir, "matlab")
    base_mat_name = fname + "_" + date_string

    # For channel-1
    mat_name = base_mat_name + ".mat"
    mat_path = os.path.join(mat_dir, mat_name)
    scipy.io.savemat(mat_path, mdict = raw_data[0])
    
    # For channel-2
    mat_name_diff = base_mat_name + "_diff" + ".mat"
    mat_path_diff = os.path.join(mat_dir, mat_name_diff)
    scipy.io.savemat(mat_path_diff, mdict = raw_data[1])