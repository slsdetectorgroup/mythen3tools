from slsdet import Mythen3,timingMode,detectorSettings,runStatus,dacIndex,scanParameters
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
#import fit_scurve as fsc
import matplotlib.pyplot as plt
from thrScan import *


d = Mythen3()
rx=makeReceiver(d)
d.powerchip=1
d.fname="arc2"
d.fpath="/mnt/mythen_data/Mythen3_module/moduleTest_20210805/"

d.highvoltage=200
d.counters=[0]
smin=1000
smax=800
sstep=-5
dac=dacIndex.VTH1
d.exptime=0.1
data_thr=scan(d,rx,dac, smin, smax, sstep)
psc.plot_thrscan(np.concatenate(data_thr,axis=1),smin,smax,sstep)
d.highvoltage=0
#tt=110
#vv=np.where(data_thr[0,tt,:]<np.mean(data_thr[0,tt,:])/2.)
#vv1=np.where(data_thr[0,tt,:]>np.mean(data_thr[0,tt,:])*3)
#print(d.fname,"BAD CHANS:",len(vv[0])+len(vv1[0]))
#print(vv,vv1)
d.powerchip=0
