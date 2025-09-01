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
nscans=1#00

d = Mythen3()
rx=makeReceiver(d)
#d.powerchip=1
#d.fname="noise_tb63"
#d.fpath="/mnt/mythen_data/Mythen3_module/my30sTests_20211216/"

fig1, ax1 = plt.subplots()
nmod=len(d.hostname)
fig1.show()
fname="flatField_15keV_th7500eV"
d.fwrite=1
d.exptime=1#180
d.fname=fname
d.frames=1
d.period=0
d.gatedelay=0.1
d.findex=200
myfile = open(str(d.fpath)+'/'+fname+'_'+str(d.findex)+'.log', 'w')
data=np.zeros((nmod,len(d.counters)*1280), dtype =  to_dtype(d.dr))

nf0=0
d.startReceiver()
for iscan in np.arange(0,nscans):
    for angle in [87,2]:
    
        d.startDetector()
        #caput('BL11I-MO-DIFF-01:DELTA.VAL',angle,wait=False)
        print("moving detector to ",angle)
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
                print("Data received")

        if ax1 is not None:
            aa=np.concatenate(data,axis=0)
            ax1.plot(aa)
            fig1.canvas.draw()
            fig1.canvas.flush_events()

myfile.close()

d.stopReceiver()
#receive dummy packet
for imod in range(nmod):
    dd, hh = rx[imod].receive_one_frame()

d.fname='dummy'
d.fwrite=0
