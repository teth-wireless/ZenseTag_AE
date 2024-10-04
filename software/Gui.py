#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import logging as logger
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets

from ReadSpeedCounter import ReadSpeedCounter
from TagHistory import TagHistory

from params import IMPINJ_HOST_IP, IMPINJ_HOST_PORT
from params import DATA_DIR, STORE_DATA
from params import SENSORS, SENSOR_DEF
from params import DEFAULT_ANTENNA_LIST

from phase_calculation_functions import phase_resolution, phase_difference, clean_phase_difference
from rf_data_collection_functions import (get_raw_data_per_rf, channel_wise_data_per_rf, store_raw_data_as_json, 
                                          store_channelwise_data_as_json, store_raw_data_as_mat)

try:
    from sllurp.version import __version__ as sllurp_version
except ImportError:
    print("Please install the `sllurp` package")
    raise
from sllurp.llrp import (LLRPReaderClient, LLRPReaderConfig)

logger.basicConfig(level=logger.INFO)

host = IMPINJ_HOST_IP
epc_to_save = SENSORS[SENSOR_DEF]["EPC"][0]
epc_to_save_diff = SENSORS[SENSOR_DEF]["EPC"][1]
store_data = STORE_DATA
data_dir = DATA_DIR

class Gui(QtWidgets.QMainWindow):
    """graphical user interface to open connection with a LLRP reader
    and inventory tags.
    """

    def __init__(self,fname, *args, **kwargs):
        # variables
        self.reader_start_time = None
        self.total_tags_seen = 0
        self.recently_updated_tag_keys = set()
        self.tags_db = {}
        self.tags_db_lock = threading.Lock()
        self.speed_counter = ReadSpeedCounter(6)
        self.history_enabled = True
        self.isConnected = False
        self.fname = fname
        self.reader = None

        super(Gui, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        n_data_pts = 100
        self.x = list(range(n_data_pts))  # 1000 time points
        self.y = [0]*n_data_pts

        self.graphWidget.setBackground('w')
        styles = {'color':'k', 'font-size':'20px'}
        self.graphWidget.setLabel('left', 'Phase (°)', **styles)
        self.graphWidget.setLabel('bottom', 'Tag Reads', **styles)

        pen = pg.mkPen(color=(255, 0, 0), width = 5)
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
        self.graphWidget.setYRange(0, SENSORS[SENSOR_DEF]["y_range"], padding=0)

        self.curr_phase = -1
        self.curr_phase_deg = -1
        self.ref_phase = -1
        self.num_vals_ref_table = 10
        self.ref_phases_table = np.zeros((50,self.num_vals_ref_table))
        self.curr_channel_count = np.zeros(50)
        

        self.vec_size = 20
        self.rolling_idx = 0
        self.diff_phase_arr = np.zeros(self.vec_size)
        self.array_populated = False
        self.std_threshold = 1000

    def connect(self):
        """open connection with the reader through LLRP protocol
        """
        logger.info("connecting...")
        if not self.isConnected:
            # r_param_fn = self.readerParam.param
            # duration_time = r_param_fn("time").value()
            # duration = None if duration_time == 0.0 else duration_time
            duration = 0.1
            factory_args = dict(
                duration=duration,
                report_every_n_tags=None,
                antennas=(DEFAULT_ANTENNA_LIST[0],),
                tx_power={
                    DEFAULT_ANTENNA_LIST[0]: 0,
                    # DEFAULT_ANTENNA_LIST[1]: 0
                },  # index of the power table to set the minimal power available
                tari=0,
                session=2,
                mode_identifier=1,
                tag_population=3,
                start_inventory=False,
                # disconnect_when_done=True,
                # tag_filter_mask=args.tag_filter_mask
                tag_content_selector={
                    "EnableROSpecID": False,
                    "EnableSpecIndex": False,
                    "EnableInventoryParameterSpecID": False,
                    "EnableAntennaID": False,
                    "EnableChannelIndex": False,
                    "EnablePeakRSSI": False,
                    "EnableFirstSeenTimestamp": False,
                    "EnableLastSeenTimestamp": False,
                    "EnableTagSeenCount": True,
                    "EnableAccessSpecID": True,
                },
                event_selector={
                    'HoppingEvent': False,
                    'GPIEvent': False,
                    'ROSpecEvent': True,
                    'ReportBufferFillWarning': True,
                    'ReaderExceptionEvent': True,
                    'RFSurveyEvent': False,
                    'AISpecEvent': True,
                    'AISpecEventWithSingulation': False,
                    'AntennaEvent': False,
                },
                # frequencies = {'ChannelList': [10,40],'Automatic': False}
            )
            # impinj_ext_fn = r_param_fn('impinj_extensions').param
            # if impinj_ext_fn('enabled').value():
            search_mode = 2
            factory_args['impinj_search_mode'] = search_mode

            factory_args['impinj_tag_content_selector'] = {
                'EnableRFPhaseAngle': True,
                'EnablePeakRSSI': True,
                'EnableRFDopplerFrequency': True
            }

            config = LLRPReaderConfig(factory_args)
            self.reader = LLRPReaderClient(host, IMPINJ_HOST_PORT, config)
            self.reader.add_tag_report_callback(self.tag_report_cb)
            # self.reader.add_state_callback(LLRPReaderState.STATE_CONNECTED,
            #                                self.onConnection)
            self.reader.add_event_callback(self.reader_event_cb)
            try:
                self.reader.connect()
                self.isConnected = True
            except Exception:
                logger.warning("%s Destination Host Unreachable", host)

    def disconnect(self):
        """
        close connection with the reader and store all available data collected so far
        """
        tags_db = self.tags_db

        key_1 = (epc_to_save, 1)
        prev_info_1 = tags_db.get(key_1, {})
        prev_history_1 = prev_info_1.get('history', TagHistory(key_1))

        key_2 = (epc_to_save_diff, 1)
        prev_info_2 = tags_db.get(key_2, {})
        prev_history_2 = prev_info_2.get('history', TagHistory(key_2))

        raw_rf1_data = get_raw_data_per_rf(prev_history_1)
        raw_rf2_data = get_raw_data_per_rf(prev_history_2)

        raw_data = []
        raw_data.append(raw_rf1_data)
        raw_data.append(raw_rf2_data)

        channel_data_1 = channel_wise_data_per_rf(prev_history_1)
        channel_data_2 = channel_wise_data_per_rf(prev_history_2)

        channel_wise_data = []
        channel_wise_data.append(channel_data_1)
        channel_wise_data.append(channel_data_2)

        if (store_data):
            store_raw_data_as_mat(raw_data, self.fname)
            store_raw_data_as_json(raw_data, self.fname)
            store_channelwise_data_as_json(channel_wise_data, self.fname)
        else:
            print("Not storing data")
        

        if self.reader is not None:
            logger.info("disconnecting...")
            self.reader.join(0.1)
            logger.info("Exit detected! Stopping readers...")
            try:
                self.reader.disconnect()
                self.reader.join(0.1)
                self.isConnected = False
            except Exception:
                logger.exception("Error during disconnect. Ignoring...")
                pass

    def check_connection_state(self):
        if self.isConnected and self.reader and not self.reader.is_alive():
            self.disconnect()
            self.isConnected = False
            # self.update_status("Unexpectedly disconnected")
            return False
        return True

    def startInventory(self, duration=None, report_every_n_tags=None,
                       antennas=None, tx_power=None, tari=None, session=None,
                       mode_identifier=None, tag_population=None,
                       tag_filter_mask=None):
        """ask to the reader to start an inventory
        """
        if self.isConnected and self.check_connection_state():
            logger.info("inventoring...")
            # r_param_fn = self.readerParam.param
            # if duration is None and r_param_fn("time").value() > 0.0:
            #     duration = r_param_fn("time").value()
            duration = 0.1
            if report_every_n_tags is None:
                report_every_n_tags = 1
            if antennas is None:
                antennas = (1,)
            if tx_power is None:
                tx_power = {
                    1: 0
                }
            if tari is None:
                tari = 0
            if session is None:
                session = 2
            if mode_identifier is None:
                mode_identifier = 1
            if tag_population is None:
                tag_population = 3
            if tag_filter_mask is None:
                tag_filter_mask = []
                # print(tag_filter_mask)

            factory_args = dict(
                duration=None,
                report_every_n_tags=report_every_n_tags,
                antennas=antennas,
                tx_power=tx_power,
                tari=tari,
                session=session,
                mode_identifier=mode_identifier,
                tag_population=tag_population,
                tag_filter_mask=tag_filter_mask,
                start_inventory=False,
                tag_content_selector={
                    "EnableROSpecID": False,
                    "EnableSpecIndex": False,
                    "EnableInventoryParameterSpecID": False,
                    "EnableAntennaID": True,
                    "EnableChannelIndex": True,
                    "EnablePeakRSSI": True,
                    "EnableFirstSeenTimestamp": True,
                    "EnableLastSeenTimestamp": True,
                    "EnableTagSeenCount": True,
                    "EnableAccessSpecID": True,
                },
                event_selector={
                    'HoppingEvent': False,
                    'GPIEvent': False,
                    'ROSpecEvent': True,
                    'ReportBufferFillWarning': True,
                    'ReaderExceptionEvent': True,
                    'RFSurveyEvent': False,
                    'AISpecEvent': True,
                    'AISpecEventWithSingulation': False,
                    'AntennaEvent': False,
                }
                # frequencies = {'ChannelList': [10,40],'Automatic': True}
            )

            # impinj_ext_fn = r_param_fn('impinj_extensions').param
            # if impinj_ext_fn('enabled').value():
            # search_mode = impinj_ext_fn('search_mode').value()
            factory_args['impinj_search_mode'] = 2

            factory_args['impinj_tag_content_selector'] = {
                'EnableRFPhaseAngle': True,
                'EnablePeakRSSI': True,
                'EnableRFDopplerFrequency': True
            }

            # update config
            self.reader.update_config(LLRPReaderConfig(factory_args))
            # update internal variable
            self.reader.llrp.parseCapabilities(self.reader.llrp.capabilities)
            # start inventory with update rospec which has been generated with
            # previous config
            self.reader.llrp.startInventory(force_regen_rospec=True)
            self.reader.join(0.1)

            
            # self.update_status('| STARTED')

    def stopInventory(self):
        """ask to the reader to stop inventory
        """
        if self.isConnected:
            if not self.check_connection_state():
                return
            logger.info("stopping inventory...")
            

            try:
                self.reader.llrp.stopPolitely()
            except Exception as exc:
                logger.warning("stop_inventory: Reader error ignored for "
                               "stopPolitely : %s" % str(exc))
            self.reader.join(0.1)

            unique_tags = len({x[0] for x in self.get_tags_db_copy().keys()})
            msg = '%d tags seen (%d uniques) | PAUSED' % (
                self.total_tags_seen, unique_tags)
            # self.update_status(msg)

    def tag_report_cb(self, reader, tags):
        """sllurp tag report callback, it emits a signal in order to perform
        the report parsing on the QT loop to avoid GUI freezing
        """
        with self.tags_db_lock:

            history_enabled = self.history_enabled
            tags_db = self.tags_db
            start_time = self.reader_start_time
            if start_time is None:
                start_time = 0

            new_tag_seen_count = 0
            updated_tag_keys = set()

            #logger.info('%s tag_filter_mask=<%s>', str(tags),
            #            str(self.reader.llrp.config.tag_filter_mask))
            #logger.info('Full: %s', pprint.pformat(tags))

            epc1 = epc_to_save
            epc2 = epc_to_save_diff
            time_diff=False

            # epc1 = 'E28011606000020EA5BAA803'
            # epc2 = 'E28011606000020EA5BA6CF3'

            tag1_detected = False
            tag2_detected = False
            phase_1 = 0
            phase_2 = 0
            channel_1 = -1
            channel_2 = -1

            # parsing each tag in the report
            for tag in tags:
                # get epc ID. (EPC covers EPC-96 and EPCData)
                epc = tag["EPC"].decode("utf-8").upper()
                ant_id = tag["AntennaID"]
                # Convert to milliseconds
                if start_time:
                    new_first_seen_tstamp = \
                        (tag.get('FirstSeenTimestampUTC', start_time)
                        - start_time) // 1000
                else:
                    # ROSpec start was missed, or data was cleared
                    # mid-inventory
                    new_first_seen_tstamp = 0
                    start_time = tag.get('FirstSeenTimestampUTC', 0)
                    self.reader_start_time = start_time

                last_seen_tstamp = (tag.get('LastSeenTimestampUTC', start_time)
                                    - start_time) // 1000
                key = (epc, ant_id)
                # print(key)
                prev_info = tags_db.get(key, {})
                prev_history = prev_info.get('history', TagHistory(key))

                seen_count_new = tag.get('TagSeenCount', 1)
                seen_count = prev_info.get('seen_count', 0) + seen_count_new

                channel_idx_new = tag.get('ChannelIndex', 0)
                channel_idx_old = prev_info.get('channel_index', 0)

                # PeakRSSI highest value
                peakrssi_new = tag.get('PeakRSSI', -120)
                peakrssi_best = max(peakrssi_new, prev_info.get('rssi', -120))

                first_seen_tstamp = prev_info.get('first_seen',
                                                new_first_seen_tstamp)

                new_info = {
                    'epc': epc,
                    'antenna_id': ant_id,
                    'history': prev_history,
                    'rssi': peakrssi_best,
                    'channel_index': channel_idx_old or channel_idx_new,
                    'seen_count': seen_count,
                    'first_seen': first_seen_tstamp,
                    'last_seen': last_seen_tstamp,
                    'last_rssi': peakrssi_new,
                    'last_channel_index': channel_idx_new
                }

                # Add Impinj specific data if available
                phase = tag.get('ImpinjRFPhaseAngle')
                if phase is not None:
                    new_info['impinj_phase'] = phase
                doppler_freq = tag.get('ImpinjRFDopplerFrequency')
                if doppler_freq is not None:
                    new_info['impinj_doppler'] = doppler_freq

                tags_db[key] = new_info

                if history_enabled:
                    phase_degree, self_diff_phase = prev_history.add_data(new_first_seen_tstamp,
                                                                        peakrssi_new,
                                                                        channel_idx_new,
                                                                        phase,
                                                                        doppler_freq)
                
                # *********************************************************************************************************************

                key_1 = (epc_to_save, 1)
                prev_info_1 = tags_db.get(key_1, {})
                prev_history_1 = prev_info_1.get('history', TagHistory(key_1))

                key_2 = (epc_to_save_diff, 1)
                prev_info_2 = tags_db.get(key_2, {})
                prev_history_2 = prev_info_2.get('history', TagHistory(key_2))

                real_time = True

                channel_data_1 = channel_wise_data_per_rf(prev_history_1, real_time)
                channel_data_2 = channel_wise_data_per_rf(prev_history_2, real_time)

                channel_wise_data = []
                channel_wise_data.append(channel_data_1)
                channel_wise_data.append(channel_data_2)

                channel_wise_warped_phases = phase_resolution(channel_wise_data)

                phase_diff = phase_difference(channel_wise_warped_phases)

                cleaned_phase_diff = clean_phase_difference(phase_diff)

                phase_separation = [diff for sublist in cleaned_phase_diff.values() for diff in sublist]

                if(epc==epc1):
                    tag1_detected = True
                    phase_1 = phase_degree
                    channel_1 = channel_idx_new
                    self.curr_phase = self_diff_phase
                    self.curr_channel = channel_1-1
                    self.curr_phase_deg = self_diff_phase

                if(epc==epc2):
                    tag2_detected = True
                    phase_2 = phase_degree
                    channel_2 = channel_idx_new
                    self.ref_phase = self_diff_phase

                new_tag_seen_count += seen_count_new
                updated_tag_keys.add(key)

            # Collecting
            # Time differential
            add_to_plot = False
            if(time_diff):
                diff_phase = self.curr_phase
                add_to_plot = True
            # RFID differential
            else:
                # Problem 1: reduced throughput because it assumes tag1+tag2
                # count number of 
                if(tag1_detected and self.ref_phase!=-1):
                    # 
                    diff_phase = self.curr_phase - self.ref_phase # useful data
                    add_to_plot = True
                # else
                # do counts 

            # Processing Data
            if(add_to_plot):
                # Cleaning Data (0-360)
                if(np.abs(diff_phase)>300):
                    diff_phase = diff_phase - np.sign(diff_phase)*360
                # Impinj induced changes (0-180)
                if(np.abs(diff_phase)>150):
                    diff_phase = diff_phase - np.sign(diff_phase)*180

                do_dtw = True
                dtw_mean_phase = np.mean(phase_separation)
                # if do_dtw:
                #     print("dtw_mean_phase: ", dtw_mean_phase)
                # else: 
                #     print("diff_phase: ", diff_phase)

                # Reject multipath v0
                if(self.array_populated):
                    self.rolling_idx=(self.rolling_idx+1)%self.vec_size
                    self.diff_phase_arr[self.rolling_idx] = diff_phase # add new phase

                    if(np.std(self.diff_phase_arr)<self.std_threshold): # if combined std dev is <3 degree
                        avg_phase = np.mean(self.diff_phase_arr) # report average phase of past vec_size values

                        # QT Code Add to plot: useful data
                        self.x = self.x[1:]  # Remove the first y element.
                        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
                        self.y = self.y[1:]  # Remove the first
                        if do_dtw:
                            self.y.append(dtw_mean_phase)  # Add dtw'ed phase diff mean
                        else:
                            self.y.append(avg_phase)  # Add a new random value.
                        self.data_line.setData(self.x, self.y)  # Update the data.

                    else:
                        if not do_dtw:
                            print("Multipath!")
                        # should you reset the array?
                        # any other way of avoiding?
                        # Roll back the rolling idx
                else:
                    self.rolling_idx=(self.rolling_idx+1)%self.vec_size # update rolling index
                    if do_dtw:
                        self.diff_phase_arr[self.rolling_idx] = dtw_mean_phase # add new dtw'ed phase diff to the array
                    else:
                        self.diff_phase_arr[self.rolling_idx] = diff_phase # add new diff_phase to the array
                    if(self.rolling_idx==self.vec_size-1): # if my roilling index reaches size
                        self.array_populated=True # set flag to true


            self.total_tags_seen += new_tag_seen_count


        # self.inventoryReportReceived.emit(updated_tag_keys)

    def reader_event_cb(self, reader, events):
        timestamp_event = events.get('UTCTimestamp', {})
        timestamp_us = timestamp_event.get('Microseconds', 0)
        if self.reader_start_time:
                timestamp_since_start = timestamp_us - self.reader_start_time
        else:
                timestamp_since_start = 0

        # Set reader_start at the time of the first ROSpec start event
        rospec_event = events.get('ROSpecEvent', {})
        if rospec_event:
            event_type = rospec_event.get('EventType')
            if event_type == 'Start_of_ROSpec' and not self.reader_start_time:
                self.reader_start_time = timestamp_us

    def clear_tags_db(self):
        with self.tags_db_lock:
            self.tags_db = {}

    def get_tags_db_copy(self):
        """Freeze the value of the tags db for display

        Warning: This is not a deep copy of the db, and except the tag key list
        itself, it will still be "reference" to inner tag info and history.
        This should be crash-free acceptable even if maybe not always
        perfectly consistent as tags info are updated atomically by
        tag_report_cb.
        The goal of the lock and copy is mainly to avoid unexecpected issues
        with the "clear_tags" operation at the wrong time.
        """
        with self.tags_db_lock:
            return self.tags_db.copy()

    def parseInventoryReport(self, updated_tag_keys):
        """Function called each time the reader reports seeing tags,
        It is run on the QT loop to avoid GUI freezing.
        """
        self.recently_updated_tag_keys.update(updated_tag_keys)
        #self.inventoryReportParsed.emit(updated_tag_keys)

    def exithandler(self):
        """called when the user closes the main window
        """
        self.disconnect()