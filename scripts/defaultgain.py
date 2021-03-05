from slsdet import Mythen3
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt

d = Mythen3()
#setSuperHighGainMode(d)
setDefaultMode(d)
