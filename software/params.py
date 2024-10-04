#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import os

SENSORS = {
    "stub": {
        "EPC": ["ADDAFB63AC1F3841EC880467", "ADDA1B63AC1F3841EC880467"],
        "classification": {

        },
        "real_time_data_window": 1,
        "y_range": 60
    },
    "soil": {
        "EPC": ["DEEDDEEDAC1F3841EC880467", "BABABABAAC1F3841EC880467"],
        # "EPC": ["3005FB63AC1F3681EC880468", "DADBFB63AC1F3841EC880467"],
        # "EPC": ["DADCFB63AC1F3841EC880467", "DADDFB63AC1F3841EC880467"],
        "classification": {
            "saturated": 27,
            "moist": 55,
            "dry": 150
        },
        "real_time_data_window": 10,
        "y_range": 120
    },
    "force": {
        "EPC": ["EDDEFB63AC1F3681EC880468", "DEEDFB63AC1F3681EC880468"],
        "classification": {
            "light": 30,
            "heavy": 90
        },
        "real_time_data_window": 4,
        "y_range": 90
    },
    "photo": {
        "EPC": ["ECECFB63AC1F3841EC880467", "CECEFB63AC1F3841EC880467"],
        "classification": {
            "bright": 23,
            "medium": 35,
            "dark": 50
        },      
        "real_time_data_window": 4,
        "y_range": 30
    },
    "test": {
        "EPC": ["ABBAFB63AC1F3841EC880467", "BAABFB63AC1F3841EC880467"],
        "classification": {
            "bright": 30,
            "medium": 45,
            "dark": 60
        },      
        "real_time_data_window": 4,
        "y_range": 30
    }
}

# Choose the default sensor from the following list only: soil, force, light, stub
# SENSOR_DEF = "soil"
# SENSOR_DEF = "force"
SENSOR_DEF = "photo"
# SENSOR_DEF = "stub"
# SENSOR_DEF = "test"

IMPINJ_HOST_IP = "169.254.34.180"
IMPINJ_HOST_PORT = 5084

repo_name = "py-RFID"
directory = os.getcwd()
data_dir = os.path.join(directory, "data")
DATA_DIR = os.path.join(data_dir, "rf_data")
STORE_DATA = True

GUI_APP_TITLE = 'SLLURP GUI - RFID inventory control'
GUI_ICON_PATH = 'rfid.png'

TAGS_TABLE_HEADERS = ["EPC", "Antenna", "Best\nRSSI", "First\nChannel",
                      "Tag Seen\nCount", "Last\nRSSI", "Last\nChannel"]
TAGS_TABLE_COLUMNS = ['epc', 'antenna_id', 'rssi', 'channel_index',
                      'seen_count', 'last_rssi', 'last_channel_index']

DEFAULT_POWER_TABLE = [index for index in range(15, 25, 1)]
DEFAULT_ANTENNA_LIST = [1,2]

READER_MODES_TITLES = OrderedDict(sorted({
    '0 - (Impinj: Max Throughput)': 0,
    '1 - (Impinj: Hybrid M=2)': 1,
    '2 - (Impinj: Dense Reader M=4)': 2,
    '3 - (Impinj: Dense Reader M=8)': 3,
    '4 - (Impinj: Max Miller M=4)': 4,
    '5 - (Impinj: Dense Reader 2 M=4)': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    '11': 11,
    '12': 12,
    '13': 13,
    '14': 14,
    '15': 15,
    '16': 16,
    '17': 17,
    '18': 18,
    '19': 19,
    '20': 20,
    '1000 - (Impinj: Autoset)': 1000,
    '1002 - (Impinj: Autoset Static)': 1002,
    '1003 - (Impinj: Autoset Static Fast)': 1003,
    '1004 - (Impinj: Autoset Static DRM)': 1004,
    '1005': 1005,
}.items(), key=lambda x: x[1]))

IMPINJ_SEARCH_MODE_TITLES = OrderedDict(sorted({
    '0 - Reader Selected (default)': 0,
    '1 - Single Target Inventory': 1,
    '2 - Dual Target Inventory': 2,
    '3 - Single Target Inventory with Suppression': 3,
    '5 - Single Target Reset Inventory': 5,
    '6 - Dual Target Inventory with Reset': 6,
}.items(), key=lambda x: x[1]))

readerSettingsParams = [
    {
        'name': 'time',
        'title': 'Time (seconds to inventory)',
        'type': 'float', 'value': 10
    }, {
        'name': 'report_every_n_tags',
        'title': 'Report every N tags (issue a TagReport every N tags)',
        'type': 'int', 'value': 2
    }, {
        'name': 'tari',
        'title': 'Tari (Tari value; default 0=auto)',
        'type': 'int', 'value': 0
    }, {
        'name': 'session',
        'title': 'Session (Gen2 session; default 2)',
        'type': 'list', 'values': [0, 1, 2, 3],
        'value': 1
    }, {
        'name': 'mode_identifier',
        'title': 'Mode identifier (ModeIdentifier value)',
        'type': 'list', 'values': READER_MODES_TITLES,
        'value': 0
    }, {
        'name': 'tag_population',
        'title': 'Tag population (Tag Population value; default 4)',
        'type': 'int', 'value': 2
    }, {
        'name': 'frequencies',
        'title': 'Frequencies to use (Comma-separated; 0=all; default 1)',
        'type': 'str', 'value': '1'
    }, {
        'name': 'impinj_extensions',
        'title': 'Impinj readers extensions',
        'type': 'group',
        'expanded': True,
        'children': [
            {
                'name': 'enabled',
                'title': 'Enable Impinj extensions',
                'type': 'bool',
                'value': True
            }, {
                'name': 'search_mode',
                'title': 'Impinj search mode',
                'type': 'list',
                'values': IMPINJ_SEARCH_MODE_TITLES,
                'value': 2
            }
        ]
    }, {
        'name': 'zebra_extensions',
        'title': 'Zebra readers extensions',
        'type': 'group',
        'expanded': True,
        'children': [
            {
                'name': 'enabled',
                'title': 'Enable Zebra extensions',
                'type': 'bool',
                'value': False
            }
        ]

    }
]
