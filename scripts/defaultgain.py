import slsdet 
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt

def bits_to_string(val):
    gains = [g for g in slsdet.M3_GainCaps.__members__ if int(getattr(slsdet.M3_GainCaps, g)) & val]
    return ','.join([g for g in gains])

d = slsdet.Mythen3()
#setDefaultMode(d)


print('Before: ', bits_to_string(d.getChipStatusRegister()[0]))
d.setGainCaps(slsdet.M3_GainCaps.M3_C10pre | slsdet.M3_GainCaps.M3_C30sh)
print('After: ', bits_to_string(d.getChipStatusRegister()[0]))

