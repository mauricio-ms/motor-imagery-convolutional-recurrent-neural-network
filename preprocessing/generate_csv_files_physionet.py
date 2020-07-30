import os
import numpy as np
import pandas as pd
import pyedflib
import re
import functools
import operator
import shutil


MOTOR_IMAGERY_LABEL = {
    0: "REST",
    1: "LEFT_FIST",
    2: "RIGHT_FIST",
    3: "BOTH_FISTS",
    4: "BOTH_FEET"
}


# T0 corresponds to rest
# T1 corresponds to onset of motion (real or imagined) of
#   the left fist (in runs 3, 4, 7, 8, 11, and 12)
#   both fists (in runs 5, 6, 9, 10, 13, and 14)
# T2 corresponds to onset of motion (real or imagined) of
#   the right fist (in runs 3, 4, 7, 8, 11, and 12)
#   both feet (in runs 5, 6, 9, 10, 13, and 14)
def get_event(event, run_execution):
    if event == "T0":
        return 0

    movement_single_member_runs = [3, 4, 7, 8, 11, 12]
    movement_both_members_runs = [5, 6, 9, 10, 13, 14]

    if event == "T1":
        if run_execution in movement_single_member_runs:
            return 1
        elif run_execution in movement_both_members_runs:
            return 3

    if event == "T2":
        if run_execution in movement_single_member_runs:
            return 2
        elif run_execution in movement_both_members_runs:
            return 4


PROJECT_NAME = "motor-imagery-convolutional-recurrent-neural-network"
ROOT_DIR = os.getcwd()[:os.getcwd().index(PROJECT_NAME) + len(PROJECT_NAME)]
PHYSIONET_DIR = os.path.join(ROOT_DIR, "data/physionet")
CSV_FILES_DIR = os.path.join(PHYSIONET_DIR, "csv-files")

if os.path.exists(CSV_FILES_DIR):
    shutil.rmtree(CSV_FILES_DIR)

os.makedirs(CSV_FILES_DIR)

subjects = sorted(os.listdir(os.path.join(PHYSIONET_DIR, "edf-files")))
# subjects = ["S098"]
for subject in filter(lambda f: re.match("S(\\d+)", f), subjects):
    print("Subject: " + subject)
    edf_subject_directory = os.path.join(PHYSIONET_DIR, "edf-files", subject)
    edf_files_names = sorted(os.listdir(edf_subject_directory))
    # edf_files_names = ["S098R11.edf"]
    for edf_file_name in filter(lambda f: f.endswith(".edf"), edf_files_names):
        print("File: " + edf_file_name)
        groups_edf_file = re.match("S(\\d+)R(\\d+).edf", edf_file_name).groups()
        run_execution = groups_edf_file[1]

        edf_file = pyedflib.EdfReader(os.path.join(edf_subject_directory, edf_file_name))

        n_channels = edf_file.signals_in_file
        n_samples = edf_file.getNSamples()[0]
        data = np.zeros((n_samples, n_channels+1))
        # Set invalid label to verify skipped samples
        data[:, -1] = -1

        frequency = edf_file.getSampleFrequencies()[0]

        annotations = edf_file.readAnnotations()
        start_events = annotations[0]
        duration_events = annotations[1]
        events = annotations[2]
        for index_event in range(len(start_events)):
            start_event = start_events[index_event]
            duration_event = duration_events[index_event]
            event = events[index_event]

            start_index = int(start_event * frequency)
            end_index = np.minimum(int((start_event + duration_event) * frequency), n_samples)
            event_samples = end_index-start_index
            for ch in np.arange(n_channels):
                data[start_index:end_index, ch] = edf_file.readSignal(ch, start_event, event_samples)
            data[start_index:end_index, -1] = np.repeat(get_event(event, int(run_execution)), event_samples)

        csv_subject_directory = os.path.join(CSV_FILES_DIR, subject)
        if not os.path.exists(csv_subject_directory):
            os.makedirs(csv_subject_directory)

        channels_labels = edf_file.getSignalLabels()
        header = functools.reduce(operator.iconcat, [channels_labels, ["LABEL"]], [])
        csv_path_file = os.path.join(csv_subject_directory, f"S{subject}R{run_execution}.csv")
        pd.DataFrame(data)\
            .to_csv(csv_path_file, header=header, index=False)