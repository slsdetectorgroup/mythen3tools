import slsdet 
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt

d = slsdet.Mythen3()
setDefaultMode(d)
#d.setGainCaps(int(slsdet.M3_GainCaps.M3_C30sh)|int(slsdet.M3_GainCaps.M3_C15pre))

#print('Before: ', bits_to_string(d.getChipStatusRegister()[0]))
#print('After: ', bits_to_string(d.getChipStatusRegister()[0]))

