#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import exit, argv
from time import sleep

from AntennaReader import AntennaReader
from params import STORE_DATA

# default time to collect data in seconds
time_to_collect = 10

def main():
    # Add codes for arduino command
    # loop start
        # start QUI
        # command arduino
        # stop GUI
        # save file
    # continue looping
    # app = QApplication(argv)
    num_args = len(argv)
    if(num_args<2):
        print("Please supply file name")
        exit(0)
    fname = argv[1]
    try:
        collection_time = argv[2]
        data_time = argv[2]
        if 's' in collection_time:
            collection_time = collection_time.replace('s','')
            collection_time = float(collection_time)
        elif 'm' in collection_time:
            collection_time = collection_time.replace('m','')
            collection_time = float(collection_time) * 60
        elif 'h' in collection_time:
            collection_time = collection_time.replace('h','')
            collection_time = float(collection_time) * 60 * 60
        else:
            collection_time = float(collection_time)
            data_time = data_time + "s"
    except:
        print(f"Using default {time_to_collect}s for data collection")
        collection_time = time_to_collect
        data_time = str(collection_time) + "s"
    fname = "_".join([fname,data_time])
    if STORE_DATA:
        print("Saving to file: "+fname)
    else:
        print("Not storing data")
    # sleep(5)
    dc = AntennaReader(fname)
    sleep(1)
    dc.connect()
    sleep(1)
    dc.startInventory()
    print(f"Collecting data for {collection_time} seconds")
    sleep(collection_time)
    dc.disconnect()
    # exit(app.exec_())

if __name__ == "__main__":
    main()