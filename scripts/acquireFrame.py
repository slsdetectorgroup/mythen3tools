from slsdet import Mythen3,timingMode,detectorSettings,runStatus,dacIndex,scanParameters
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
#import fit_scurve as fsc
import matplotlib.pyplot as plt
from thrScan import *

import matplotlib
matplotlib.use('TkAgg')
#daclist [vcassh, vth2, vrshaper, vrshaper_n, vipre_out, vth3, vth1, vicin, vcas, vrpreamp, vcal_n, vipre, vishaper, vcal_p, vtrim, vdcsh, vthreshold]

#vipre
#vipre_out (?)
#vicin


d = Mythen3()
rx=makeReceiver(d)
#d.powerchip=1
d.fname="noise_tb63"
d.fpath="/mnt/mythen_data/Mythen3_module/my30sTests_20211216/"



fig1, ax1 = plt.subplots()

fig1.show()
data=acquireFrame(d,rx, ax1)
mm=np.median(data)
print(np.median(data))
#if mm>100:
#    ax1.set_ylim(-1, mm*100) 
#else:
#    ax1.set_ylim(-1, 100) 
    
if mm==0:
    mm=100
#mm=500000
ax1.set_ylim(-1, mm) 
fig1.canvas.draw()
fig1.canvas.flush_events()

