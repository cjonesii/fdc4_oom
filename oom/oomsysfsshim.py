# /////////////////////////////////////////////////////////////////////
#
#  oomsysfsshim.py : An OOM Southbound SHIM, in Python, that
#  reads optical EEPROM data directly from the /sys file system
#  and presents it to the OOM decode layer.  This shim eliminates
#  the compilation phase required for most other OOM shims.
#
#  Copyright 2017  Finisar Inc.
#
#  Author: Don Bollinger don@thebollingers.org
#
# ////////////////////////////////////////////////////////////////////

from .oomtypes import c_port_t
from .oomtypes import port_class_e
import errno
import os
import re
from threading import Lock
import gpio as GPIO
import time

mutex = Lock()


#
# where to find eeprom data:  '<root>/<device_name>/<eeprom>'
#
class paths_class:
    def __init__(self):
        self.locs = {
            'OPTOE':  ('/sys/bus/i2c/devices/',
                       '/port_name',
                       '/eeprom'),
            }


paths = paths_class()
MAXPORTS = 512


# build a class that holds the portlist info, state of the shim
class ports:
    def __init__(self):
        # state values:
        #   0 - not initialized (port_array has not been filled)
        #   1 - initialized, port_array is filled, but not copied to user
        #   2 - oom_get_portlist(list, len) has returned the portlist to user
        self.shimstate = 0
        self.portcount = 0
        self.retval = 0
        cport_array = c_port_t * MAXPORTS
        self.portlist = cport_array()

    def initports(self):
        # fill an array of ports
        self.portcount = 0
        self.portname_list = []
        portname = None
        pyportlist = []

        # sequence through known styles, looking for optical devices
        # Basically going to check every possible device, of each naming
        # style, looking for optical devices.  Any found will be added
        # to the portlist inventory
        for key in paths.locs:
            (dirpath, portpath, eepromname) = paths.locs[key]
            try:      # See if the directory (eg /sys/bus/i2c...) exists
                filenames = os.listdir(dirpath)
            except:     # On error, skip to the next one
                continue
            for name in filenames:   # candidates...  screen them
                eeprompath = dirpath + name + eepromname
                if not os.path.exists(eeprompath):
                    continue
                namepath = dirpath + name + portpath
                try:
                    with open(namepath, 'r') as fd:
                        portlabel = fd.readline()
                except:
                    continue

                # special code for each style of naming...
                # OPTOE uses an 'eeprom' file and a port name (not number)
                if key == 'OPTOE':
                    # device names look like '<num>-00<addr>',
                    # eg 54-0050.  addr is the i2c address of the
                    # EEPROM.  We want only devices with addr '50'
                    if name[-2:] != '50':
                        continue
                    portname = portlabel

                else:
                    raise NotImplementedError("OOM designer screwed up")

                # Looks good, add this as a new port to the list
                newport = c_port_t()
                newport.handle = self.portcount
                newport.oom_class = port_class_e['SFF']

                # build the name, put it into the c_port_t
                # note the type of newport.cport.name is c_ubyte_Array_32
                # so I can't just assign the string to newport.cport.name
                for i in range(0, 32):
                    if i < (len(portname)-1):
                        newport.name[i] = ord(portname[i])
                    else:
                        newport.name[i] = 0
                pyportlist.append(newport)
                self.portname_list.append(eeprompath)
                self.portcount += 1
            # next key

        # sort the keys by port name
        # abandoned sorting the keys, because names like 'port1' and 'port2'
        # will intersperse with names like 'port10' and 'port20' - ugly
        # list.sort(pyportlist, key=lambda plist: bytearray(plist.name))

        # and stuff them into the C portlist array
        count = 0
        for item in pyportlist:
            self.portlist[count] = item
            count += 1
        self.shimstate = 1
        self.retval = self.portcount
        return self.retval

    def filllist(self, c_port_list, listsize):
        # shimstate 1 means we populated the portlist, but just
        # returned the number of ports.  Don't rebuild the portlist,
        # just copy the one we have.  For any other value, build the list
        # before copying it to c_port_list
        # (0 hasn't been initialized, initialized)
        # (2 has already been returned, caller must want a refresh)
        if self.shimstate != 1:
            if self.initports() < 0:
                return

        # if not enough room, return error
        if listsize < self.portcount:
            self.retval = -errno.ENOMEM
            return

        # if portlist has changed, need to return new portcount, else 0
        self.retval = 0
        if listsize > self.portcount:
            self.retval = self.portcount
        for i in range(0, self.portcount):
            if c_port_list[i] != self.portlist[i]:
                c_port_list[i] = self.portlist[i]
                self.retval = self.portcount
        shimstate = 2
        return


# initialize the ports class (in not initialized state!)
allports = ports()


def oom_get_portlist(cport_list, numports):
    GPIO.setup(360, GPIO.OUT)
    GPIO.setup(361, GPIO.OUT)
    GPIO.setup(362, GPIO.OUT)
    GPIO.setup(363, GPIO.OUT)
    time.sleep(1.0)
    GPIO.output(360, GPIO.HIGH)
    GPIO.output(361, GPIO.HIGH)
    GPIO.output(362, GPIO.HIGH)
    GPIO.output(363, GPIO.HIGH)
    time.sleep(1.0)

    if (cport_list == 0) and (numports == 0):   # how many ports?
        return allports.initports()
    else:   # return a list of ports
        allports.filllist(cport_list, numports)
        return allports.retval


def setparms(parms):
    return


# cport.handle is a c_void_p, but not really :-(
# turn it into an integer by handling '0 is None'
def gethandle(cport):
    handle = cport.handle
    if handle is None:
        handle = 0
    return handle


#
# common code between oom_{get, set}_memory_sff
#
def open_and_seek(cport, address, page, offset, flag):
    # sanity check
    if (address < 0xA0) or (address == 0xA1) or (address > 0xA2):
        return -errno.EINVAL

    try:
        # open the the EEPROM file
        handle = gethandle(cport)
        eeprompath = allports.portname_list[handle]
    except Exception as E:
        return None
    try:
        fd = open(eeprompath, flag, 0)
    except IOError as err:
        return -err.errno

    # calculate the place to start reading/writing data
    if offset < 128:
        # offset less than 128 is the same for all pages
        seekto = offset
    else:
        seekto = page * 128 + offset

    # If 0xA2 is being addressed, it is SFP, and starts at offset 256
    if address == 0xA2:
        seekto += 256

    try:
        fd.seek(seekto)
    except IOError as err:
        return -err.errno

    return fd


#
# note, we are in oomsouth, so 'cport' is actually a c_port_t
#
def oom_get_memory_sff(cport, address, page, offset, length, data):

    if length != len(data):
        return -errno.EINVAL
    with mutex:
        fd = open_and_seek(cport, address, page, offset, 'rb')
        if ((fd is None) or (fd.fileno() < 0)):
            try:
                fd.close()
            except:
                pass
            return fd

        # and read it!
        try:
            buf = fd.read(length)
        except IOError as err:
            return -err.errno
        finally:
            fd.close()

    # copy the buffer into the data array
    ptr = 0
    for c in buf:
        data[ptr] = c
        ptr += 1
    return len(data)


#
# oom_set_memory_sff
#
def oom_set_memory_sff(cport, address, page, offset, length, data):

    if not data or length > len(data):
        return -errno.EINVAL
    with mutex:
        fd = open_and_seek(cport, address, page, offset, 'rb+')
        if isinstance(fd, int):
            if fd < 0:
                return fd
        elif ((fd is None) or (fd.fileno() < 0)):
            try:
                fd.close()
            except:
                pass
            return fd

        # and write it!
        try:
            fd.write(data[0:length])
        except IOError as err:
            return -err.errno
        finally:
            fd.close()

    # success
    return length
