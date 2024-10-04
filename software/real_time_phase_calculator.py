#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from sys import exit, argv
from PyQt5 import QtWidgets

from Gui import Gui
from params import STORE_DATA

def main():
    # Add codes for arduino command
    # loop start
        # start QUI
        # command arduino
        # stop GUI
        # save file
    # continue looping
    # app = QApplication(sys.argv)
    app = QtWidgets.QApplication(argv)
    num_args = len(argv)
    if(num_args<2):
        print("Please supply file name")
        exit(0)
    fname = argv[1]
    if STORE_DATA:
        print("Saving to file: "+fname)
    else:
        print("Not storing data")
    # sleep(5)
    gui = Gui(fname)
    gui.show()
    # app.exec_()
    sleep(1)
    gui.connect()
    sleep(1)
    gui.startInventory()
    # sleep(40)
    if(not app.exec_()):
        gui.disconnect()
    # sys.exit(app.exec_())

if __name__ == "__main__":
    main()