from slsdet import Mythen3,timingMode,detectorSettings,runStatus,dacIndex,scanParameters
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
#import fit_scurve as fsc
import matplotlib.pyplot as plt
from thrScan import *
#from epics import caput, caget

import matplotlib
matplotlib.use('TkAgg')
#daclist [vcassh, vth2, vrshaper, vrshaper_n, vipre_out, vth3, vth1, vicin, vcas, vrpreamp, vcal_n, vipre, vishaper, vcal_p, vtrim, vdcsh, vthreshold]

#vipre
#vipre_out (?)
#vicin


d = Mythen3()
rx=makeReceiver(d)
#d.powerchip=1
#d.fname="noise_tb63"
#d.fpath="/mnt/mythen_data/Mythen3_module/my30sTests_20211216/"

fig1, ax1 = plt.subplots()
nmod=len(d.hostname)
fig1.show()
fname="angularCalibration_15keV_1s"
d.fwrite=1
d.exptime=0.1
d.fname=fname
d.findex=0
myfile = open(str(d.fpath)+'/'+fname+'_'+str(d.findex)+'.log', 'w')
data=np.zeros((nmod,len(d.counters)*1280), dtype =  to_dtype(d.dr))

nf0=0
d.startReceiver()
for angle in np.arange(2,87,0.1):
    #caput('BL11I-MO-DIFF-01:DELTA.VAL',angle,wait=True)
    #data=acquireFrame(d,rx, ax1)
    d.startDetector()
    time.sleep(d.exptime)
    while d.status != runStatus.IDLE:
        time.sleep(0.01)

    nf=np.min(d.rx_framescaught)
    ang=0#caget('BL11I-MO-DIFF-01:DELTA.RBV')
    myfile.write(str(ang)+'\n')
    print(ang)
    if nf>nf0:
        for imod in range(nmod):
            dd, hh = rx[imod].receive_one_frame()
            if dd is not None:
                data[imod]=dd
            if imod==0:
                print(hh["frameIndex"])
    mm=500000
    if ax1 is not None:
        aa=np.concatenate(data,axis=0)
        ax1.plot(aa)
    ax1.set_ylim(-1, mm) 
    ax1.set_xlim(1280, 1280*14) 
    fig1.canvas.draw()
    fig1.canvas.flush_events()

myfile.close()

d.stopReceiver()
#receive dummy packet
for imod in range(nmod):
    dd, hh = rx[imod].receive_one_frame()

"""
mm=np.median(data)
print(np.median(data))
#for i in range(0,data.shape[0]):
print(np.median(data,axis=1))
if mm>100:
    ax1.set_ylim(-1, mm*100) 
else:
    ax1.set_ylim(-1, 100) 
"""    
#if mm<100:
#    mm=100
#mm=500000
