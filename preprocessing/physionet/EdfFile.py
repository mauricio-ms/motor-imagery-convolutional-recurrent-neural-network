import re
import pyedflib
import os
import numpy as np

MOVEMENT_SINGLE_MEMBER_RUNS = [3, 4, 7, 8, 11, 12]
MOVEMENT_BOTH_MEMBERS_RUNS = [5, 6, 9, 10, 13, 14]


class EdfFile:
    def __init__(self, edf_path_dir, edf_file_name, channels=None):
        self.edf_path_dir = edf_path_dir
        self.edf_file_name = edf_file_name

        groups_edf_file = re.match("S(\\d+)R(\\d+).edf", edf_file_name).groups()
        self.subject = groups_edf_file[0]
        self.run_execution = groups_edf_file[1]
        self.__file = pyedflib.EdfReader(os.path.join(edf_path_dir, edf_file_name))

        annotations = self.__file.readAnnotations()
        self.__onset_events = annotations[0]
        self.__duration_events = annotations[1]
        self.__events = annotations[2]

        self.frequency = self.__file.getSampleFrequencies()[0]
        self.n_samples = int(np.round(np.sum(self.__duration_events), decimals=2) * self.frequency)
        self.n_channels = self.__file.signals_in_file if channels is None else len(channels)
        self.channels = np.arange(self.n_channels) if channels is None else channels
        self.channels_labels = np.array(self.__file.getSignalLabels())[self.channels]
        self.data, self.labels = self.__read()

    def get_path_file(self, path_dir, extension):
        return os.path.join(path_dir, f"S{self.subject}R{self.run_execution}.{extension}")

    def close(self):
        self.__file.close()

    def __read(self):
        data = np.zeros((self.n_samples, self.n_channels))
        # Set invalid label to verify skipped samples
        labels = np.full(self.n_samples, "invalid", dtype="U256")
        end_index = None
        for index_event in range(len(self.__onset_events)):
            onset_event = self.__onset_events[index_event]
            duration_event = self.__duration_events[index_event]
            event = self.__events[index_event]

            onset_index = int(onset_event * self.frequency)
            if end_index is not None and onset_index != end_index:
                onset_index = end_index
            end_index = np.minimum(int(np.round(onset_event + duration_event, decimals=2) * self.frequency),
                                   self.n_samples)
            event_samples = end_index - onset_index

            for ch_index, ch in enumerate(self.channels):
                data[onset_index:end_index, ch_index] = self.__file.readSignal(ch, onset_index, event_samples)
            labels[onset_index:end_index] = np.repeat(self.__get_label_for_event(
                event, int(self.run_execution)), event_samples)

        if np.sum(labels == "invalid") > 0:
            print("WARNING: Samples skipped when reading the file " + self.edf_file_name)

        return data, labels

    """
        The events of real movements are not handled because these files are not read
    """
    @staticmethod
    def __get_label_for_event(event, run_execution):
        if event == "T0":
            if run_execution == 1:
                return "eyes-open"
            elif run_execution == 2:
                return "eyes-closed"
            else:
                return "rest"

        if event == "T1":
            if run_execution in MOVEMENT_SINGLE_MEMBER_RUNS:
                return "left-fist"
            elif run_execution in MOVEMENT_BOTH_MEMBERS_RUNS:
                return "both-fists"

        if event == "T2":
            if run_execution in MOVEMENT_SINGLE_MEMBER_RUNS:
                return "right-fist"
            elif run_execution in MOVEMENT_BOTH_MEMBERS_RUNS:
                return "both-feet"

        return None
