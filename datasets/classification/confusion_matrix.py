import os
import re
import json
import numpy as np
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

# Select sensor to plot confusion matrix for 
sensor = "photo"
# sensor = "soil"

def dtw_matching(sequence1, sequence2):
    _, warp_paths = fastdtw(sequence1, sequence2)

    warped_sequence1 = []
    warped_sequence2 = []

    for index in warp_paths:
        warped_sequence1.append(sequence1[index[0]])
        warped_sequence2.append(sequence2[index[1]])

    return (warped_sequence1, warped_sequence2)

def phase_difference(channel_wise_warped_phases):
    difference = {}
    for channel, rfs in channel_wise_warped_phases.items():
        difference[channel] = []
        for rf1, rf2 in zip(rfs[0], rfs[1]):
            difference[channel].append(abs(rf1 - rf2))

    return difference

def clean_phase_difference(phase_difference):
    for channel,diff_list in phase_difference.items():
        for i in range(len(diff_list)):
            if (diff_list[i] > 270):
                phase_difference[channel][i] = abs(diff_list[i] - 360)
            elif (diff_list[i] > 135):
                phase_difference[channel][i] = abs(diff_list[i] - 180)
    return phase_difference

def phase_resolution(phase_data):
    channel_wise_warped_phases = {}
    for i in range(1, 51):
        try:
            warped_rf1, warped_rf2 = dtw_matching(phase_data[0][i], phase_data[1][i])
            channel_wise_warped_phases[i] = [warped_rf1, warped_rf2]
        except Exception as e:
            pass

    return channel_wise_warped_phases



environment = {
    "soil": {
        "classification": {
            "saturated": 27,
            "moist": 55,
            "dry": 150
        }
    },
    "photo": {
        "classification": {
            "bright": 23,
            "medium": 35,
            "dark": 50
        }
    }
}

def classifier(environment_phase_data):
    categorized_data = {}
    for env,phases in environment_phase_data.items():
        for phase_diff in phases:
            for category,threshold in environment.items():
                if phase_diff < threshold:
                    try:
                        categorized_data[env].append(category)
                    except:
                        categorized_data[env] = [category]
                    break

    expected_categorization = []
    actual_categorization = []

    for env,categorized_values in categorized_data.items():
        for category in categorized_values:
            expected_categorization.append(env)
            actual_categorization.append(category)
    
    return (expected_categorization, actual_categorization)

def compute_percentage_matrix(matrix):
    perc_matrix = []
    for row in matrix:
        perc_row = []
        sum = np.sum(row)
        for val in row:
            perc_row.append((val / sum) * 100)
        perc_matrix.append(perc_row)
    return perc_matrix
    
def print_confusion_matrix(matrix):
    for row in matrix:
        for value in row:
            print("{:.2f}".format(value), end = " ")
        print()

cwd = os.getcwd()
data_path = os.path.join(cwd, "data")
regex_strings = []
for env in environment:
    rgx = fr".*?{env}.*?\d+?.json"
    regex_strings.append(rgx)

all_files = os.listdir(data_path)

data_files = []
for rgx in regex_strings:
    for file in all_files:
        if re.match(rgx, file):
            data_files.append(file)

classification_data = {}
for file in data_files:
    with open(os.path.join(data_path, file), 'r') as f:
        data = json.load(f)
        rf1 = data[0]
        rf2 = data[1]
    rf1 = {int(key): value for key, value in rf1.items()}  
    rf2 = {int(key): value for key, value in rf2.items()}
    data = [rf1, rf2]

    for env in environment:
        if env in file:
            try:
                classification_data[env].append(data)
            except:
                classification_data[env] = [data]

environment_phase_data = {}
for env,data in classification_data.items():
    for read in data:
        phase_diff = clean_phase_difference(phase_difference(phase_resolution(read)))
        phase_diff = [diff for sublist in phase_diff.values() for diff in sublist]
        try:
            environment_phase_data[env].extend(phase_diff)
        except:
            environment_phase_data[env] = phase_diff

(expected_categorization, actual_categorization) = classifier(environment_phase_data)

cm = confusion_matrix(expected_categorization, actual_categorization)
print("Confusion Matrix")
print_confusion_matrix(cm)

print()

perc_confusion_matrix = np.array(compute_percentage_matrix(cm))
print("Percentage Confusion Matrix")
print_confusion_matrix(perc_confusion_matrix)

# Plot confusion matrix with labels
fig, ax = plt.subplots()
classes = unique_labels(expected_categorization, actual_categorization)
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)
ax.set(xticks=np.arange(cm.shape[1]),
    yticks=np.arange(cm.shape[0]),
    xticklabels=classes, yticklabels=classes,
    title=f'Confusion Matrix for {sensor.title()}',
    ylabel='True Label',
    xlabel='Predicted Label')

# Increase font sizes for title, labels, and ticks
ax.title.set_fontsize(20)
ax.set_xlabel('Predicted Label', fontsize=20)
ax.set_ylabel('True Label', fontsize=20)
ax.tick_params(axis='both', which='major', labelsize=18)

# Adjust layout to fit the labels inside the figure
plt.tight_layout()

plt.savefig(f'{sensor}_cm.png', format='png', dpi=300)

# Plot percentage confusion matrix with labels
fig, ax = plt.subplots()
classes = unique_labels(expected_categorization, actual_categorization)
im = ax.imshow(perc_confusion_matrix, interpolation='nearest', cmap=plt.cm.Reds)
ax.figure.colorbar(im, ax=ax)
ax.set(xticks=np.arange(perc_confusion_matrix.shape[1]),
    yticks=np.arange(perc_confusion_matrix.shape[0]),
    xticklabels=classes, yticklabels=classes,
    title=f'Percentage Confusion Matrix for {sensor.title()}',
    ylabel='True Label',
    xlabel='Predicted Label')

# Increase font sizes for title, labels, and ticks
ax.title.set_fontsize(18)
ax.set_xlabel('Predicted Label', fontsize=17)
ax.set_ylabel('True Label', fontsize=17)
ax.tick_params(axis='both', which='major', labelsize=16)

# Adjust layout to fit the labels inside the figure
plt.tight_layout()

plt.savefig(f'{sensor}_cm_perc.png', format='png', dpi=300)
