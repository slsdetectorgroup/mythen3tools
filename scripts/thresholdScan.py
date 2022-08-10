from slsdet import Mythen3,timingMode,detectorSettings,runStatus,dacIndex,scanParameters
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
#import fit_scurve as fsc
import matplotlib.pyplot as plt
from thrScan import *


#import matplotlib
#matplotlib.use('TkAgg')

#daclist [vcassh, vth2, vrshaper, vrshaper_n, vipre_out, vth3, vth1, vicin, vcas, vrpreamp, vcal_n, vipre, vishaper, vcal_p, vtrim, vdcsh, vthreshold]

#vipre
#vipre_out (?)
#vicin


d = Mythen3()
print(d.hostname)
rx=makeReceiver(d)
print("receiver done")
#d.powerchip=1
#d.fname="test"
#d.fpath="/mnt/mythen_data/Mythen3_module/my30sTests_20211216/"

#d.settings=detectorSettings.HIGHGAIN

#import superhighgain

#d.highvoltage=200

#d.counters=[0]
smin=1800
smax=700
sstep=-10
dac=dacIndex.VTH1
#d.dacs.vth2=2400
#d.dacs.vth3=200


#d.exptime=0.1



data_thr=scan(d,rx,dac, smin, smax, sstep)
aa=np.concatenate(data_thr,axis=1)

psc.plot_thrscan(aa,smin,smax,sstep)
#plt.show()

