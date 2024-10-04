import math
import threading
import numpy as np

class TagHistory:

    def __init__(self, name):
        self.name = name
        self.times = []
        self.phases = []
        self.phases_degrees = []
        self.corrects = []
        self.corrects_degrees = []
        self.diffs = [0, 0]
        self.diffs_degrees = [0, 0]
        self.dopplers = []
        self.rssis = []
        self.channels = []
        self.channel_start_phase = -np.ones(50)

        self.shift = 0
        self.last_size = 0
        self.last_channel = None

        self.data_by_id = {
            0: self.phases_degrees,
            1: self.corrects_degrees,
            2: self.dopplers,
            3: self.rssis,
            4: self.diffs_degrees
        }

        self.data_lock = threading.Lock()

    def add_data(self, data_time, rssi=-120, channel=1, phase=None,
                 doppler=None):
        with self.data_lock:
            self.times.append(data_time)
            self.rssis.append(rssi)

            self.channels.append(channel)

            if phase is None:
                # What for default value?
                phase = 0
            

            self.phases.append(phase * ((math.pi * 2) / 4096))
            if(self.channel_start_phase[channel-1]!=-1):
                # correct for phase jumps
                curr_phase = phase * ((math.pi * 2) / 4096)
                diff = (curr_phase-self.channel_start_phase[channel-1])
                # First check if diff > 6
                if diff > 5.8:
                    curr_phase -= 2*math.pi
                elif diff < -5.8:
                    curr_phase += 2*math.pi

                # calc diff again
                diff = (curr_phase-self.channel_start_phase[channel-1])
                # Now check if diff > 3 (most probab its pi jump)
                if diff > 2.5:
                    curr_phase -= math.pi
                elif diff < -2.5:
                    curr_phase += math.pi

                self_diff_phase = curr_phase -self.channel_start_phase[channel-1] 
                self.phases_degrees.append(curr_phase*180/math.pi)
            else:
                curr_phase = phase * ((math.pi * 2) / 4096)
                self.phases_degrees.append(curr_phase*180/math.pi)
                self.channel_start_phase[channel-1] = curr_phase
                self_diff_phase = -1

            if doppler is None:
                # What for default value?
                doppler = 0
            self.dopplers.append(doppler)

            # Useless if not impinj, but let it for a first version 
            self.phase_diff()

            return curr_phase*180/math.pi, self_diff_phase*180/math.pi

    def remove_shift(self, sine):
        if self.last_channel is None:
            # print(self.channels)
            if(len(self.channels)>0):
                self.last_channel = self.channels[0]
            else:
                return
        times_len = len(self.times)
        missed = times_len - self.last_size
        if missed:
            for i in range(times_len - missed, times_len):
                if self.channels[i] != self.last_channel:
                    self.shift = self.phases[i] - self.corrects[-1]
                    curr_corrected_phase = (self.phases[i] - self.shift) % (math.pi * 2)
                    self.corrects.append(curr_corrected_phase)
                    self.corrects_degrees.append(curr_corrected_phase*180/math.pi)
                    self.last_channel = self.channels[i]
                else:
                    curr_corrected_phase =(self.phases[i] - self.shift) % (math.pi * 2)
                    self.corrects.append(curr_corrected_phase)
                    self.corrects_degrees.append(curr_corrected_phase*180/math.pi)
            self.last_size = times_len

    def remove_shift_dummy(self):
        DEFAULT_VALUE = 0
        times_len = len(self.times)
        missed = times_len - self.last_size
        if missed:
            self.corrects += [DEFAULT_VALUE for _ in range(missed)]
            self.last_size = times_len

    def phase_diff(self):
        if len(self.times) > 2:
            if self.channels[-1] != self.channels[-2]:
                # make smarter
                curr_diff = self.diffs[-1];
                self.diffs.append(curr_diff)
                self.diffs_degrees.append(curr_diff*180/math.pi)
            else:
                diff = self.phases[-1] - self.phases[-2]
                
                # First check if diff > 6
                if diff > 6:
                    diff -= math.pi * 2
                elif diff < -6:
                    diff += math.pi * 2

                # First check if diff > 3 (most probab its pi jump)
                if diff > 3:
                    diff -= math.pi
                elif diff < -3:
                    diff += math.pi

                curr_diff = (self.diffs[-1] + diff)
                self.diffs.append(curr_diff)
                self.diffs_degrees.append(curr_diff*180/math.pi)