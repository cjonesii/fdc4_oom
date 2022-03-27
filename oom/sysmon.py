# /////////////////////////////////////////////////////////////////////
#
#  sysmon.py : 
#
#  Copyright Adnacom 2022
#
# ////////////////////////////////////////////////////////////////////

import requests
import json
from oomjsonshim import *

def sysmon_get_keyvalue( key ):
    js = requests.get(url.remote,
                      json={'cmd': 'sgp'})
    return js.text

def sysmon_get_data():
    return("Hola chika")