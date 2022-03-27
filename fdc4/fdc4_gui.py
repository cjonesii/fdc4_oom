#
# fdc4_gui.py - a tool for FDC4 board
# Copyright 2022 Adnacom Inc
#
from oom import *
from oom.oomlib import type_to_str
from oom.decode import get_hexstr
from qsfp_gui import *
from sysmon_gui import *
import sys

from tkinter import *

import logging

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("gpio").setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

class Window(Frame):
    def __init__(self, master=None):
        # load the json shim if a URL has been provided
        parms = sys.argv
        if len(parms) > 1:
            if parms[1] == '-url':
                oomlib.setshim("oomjsonshim", parms[2])

        Frame.__init__(self, master)
        self.master = master

        self.pack(fill=BOTH, expand=1)

        sysmonButton = Button(self, text="System Monitor", command=self.clickSysmonButton)
        sysmonButton.pack(side=LEFT)

        qsfpButton = Button(self, text="QSFP Tool", command=self.clickQsfpButton)
        qsfpButton.pack(side=LEFT)

        pcieButton = Button(self, text="PCIe Tool", command=self.clickPcieButton)
        pcieButton.pack(side=LEFT)

        exitButton = Button(self, text="Exit", command=self.clickExitButton)
        exitButton.pack(side=LEFT)

        # the Finisar logo at the bottom of the screen
        logo = PhotoImage(file="adnacom_logo.png")
        self.label = Label(self.master, image=logo)
        self.label.image = logo  # kludge required by Tkinter
        self.label.pack(side=BOTTOM)

    def clickQsfpButton(self):
        qsfpGui = Toplevel()  # get a new window; Toplevel is used because Tk() has a pyimage2 error
        OOM(qsfpGui)

    def clickSysmonButton(self):
        sysmonGui = Toplevel()  # get a new window; Toplevel is used because Tk() has a pyimage2 error
        SYSMON(sysmonGui)

    def clickPcieButton(self):
        exit()

    def clickExitButton(self):
        exit()

root = Tk()
app = Window(root)
root.wm_title("FDC4 Utility")
root.mainloop()
