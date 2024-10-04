#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastdtw import fastdtw

def phase_resolution(phase_data):
    """
        Resolves phase data using dynamic time warping (DTW) matching for each channel.

        Parameters:
        - phase_data (list): A list of two lists representing phase data for two different sources.

        Returns:
        - channel_wise_warped_phases (dict): A dictionary containing channel-wise warped phases.

        Description:
        - The `phase_resolution` function takes in phase data and performs dynamic time warping (DTW)
        matching for each channel. It uses the `dtw_matching` function to calculate the warped RF1
        and RF2 phases for each channel. The results are then stored in a dictionary
        `channel_wise_warped_phases`, where the keys represent the channel numbers and the values
        are lists containing the warped RF1 and RF2 phases.

        - If an exception occurs during the DTW matching process for a particular channel, it is
        caught and ignored, allowing the function to continue processing the remaining channels.

        Example:
         phase_data = [[1, 2, 3], [4, 5, 6]]
         phase_resolution(phase_data)
        {1: [warped_rf1_1, warped_rf2_1], 2: [warped_rf1_2, warped_rf2_2], 3: [warped_rf1_3, warped_rf2_3]}
    """
    channel_wise_warped_phases = {}
    for i in range(1, 51):
        try:
            warped_rf1, warped_rf2 = dtw_matching(phase_data[0][i], phase_data[1][i])
            channel_wise_warped_phases[i] = [warped_rf1, warped_rf2]
        except Exception as e:
            pass

    return channel_wise_warped_phases


def dtw_matching(sequence1, sequence2):
    """
        Performs dynamic time warping (DTW) matching between two sequences.

        Parameters:
        - sequence1 (list): The first sequence.
        - sequence2 (list): The second sequence.

        Returns:
        - warped_sequence1 (list): The warped sequence 1.
        - warped_sequence2 (list): The warped sequence 2.

        Description:
        - The `dtw_matching` function takes in two sequences, `sequence1` and `sequence2`, and performs
        dynamic time warping (DTW) matching between them. It uses the `fastdtw` algorithm, which is
        an approximate DTW algorithm with lower time and memory complexities compared to the standard
        DTW algorithm.

        - The `fastdtw` function from the `fastdtw` library is used to calculate the optimal or
        near-optimal alignments between the sequences. The resulting warp paths are then used to
        extract the warped sequences.

        Example:
         sequence1 = [1, 2, 3, 4, 5]
         sequence2 = [2, 3, 4, 5, 6]
         dtw_matching(sequence1, sequence2)
        ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6])
    """
    _, warp_paths = fastdtw(sequence1, sequence2)

    warped_sequence1 = []
    warped_sequence2 = []

    for index in warp_paths:
        warped_sequence1.append(sequence1[index[0]])
        warped_sequence2.append(sequence2[index[1]])

    return (warped_sequence1, warped_sequence2)

def phase_difference(channel_wise_warped_phases):
    """
        Calculates the absolute phase difference between two warped RF1 and RF2 phases for each channel.

        Parameters:
        - channel_wise_warped_phases (dict): A dictionary containing channel-wise warped phases.

        Returns:
        - difference (dict): A dictionary containing the absolute phase difference for each channel.

        Description:
        - The `calculate_phase_difference` function takes in a dictionary `channel_wise_warped_phases`
        that contains channel-wise warped RF1 and RF2 phases. It calculates the absolute phase
        difference between the RF1 and RF2 phases for each channel and stores the results in a
        dictionary `difference`. The keys of the `difference` dictionary represent the channel
        numbers, and the values are lists containing the absolute phase differences.

        Example:
         channel_wise_warped_phases = {1: [warped_rf1_1, warped_rf2_1], 2: [warped_rf1_2, warped_rf2_2]}
         calculate_phase_difference(channel_wise_warped_phases)
        {1: [phase_difference_1], 2: [phase_difference_2]}
    """
    difference = {}
    for channel, rfs in channel_wise_warped_phases.items():
        difference[channel] = []
        for rf1, rf2 in zip(rfs[0], rfs[1]):
            difference[channel].append(abs(rf1 - rf2))

    return difference

def clean_phase_difference(phase_difference):
    """
        Adjusts the phase differences based on specific conditions.

        Parameters:
        - phase_difference (dict): A dictionary containing the phase differences for each channel.

        Returns:
        - phase_difference (dict): The adjusted phase differences.

        Description:
        - The `adjust_phase_difference` function takes in a dictionary `phase_difference` that contains
        the phase differences for each channel. It iterates over each channel and each phase difference
        in the list of differences. If a phase difference meets certain conditions, it is adjusted
        accordingly.

        - If a phase difference is greater than 270, it is adjusted by subtracting 360 from its absolute
        value. If a phase difference is greater than 135, it is adjusted by subtracting 180 from its
        absolute value.

        - The adjusted phase differences are then returned as a dictionary.

        Example:
         phase_difference = {1: [phase_difference_1], 2: [phase_difference_2]}
         adjust_phase_difference(phase_difference)
        {1: [adjusted_phase_difference_1], 2: [adjusted_phase_difference_2]}
    """
    for channel,diff_list in phase_difference.items():
        for i in range(len(diff_list)):
            if (diff_list[i] > 270):
                phase_difference[channel][i] = abs(diff_list[i] - 360)
            elif (diff_list[i] > 135):
                phase_difference[channel][i] = abs(diff_list[i] - 180)
    return phase_difference