from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt
import read_mythen as my3
from slsdet import Mythen3,detectorSettings


d = slsdet.Mythen3()
#gain=d.getChipStatusRegister()[0]
d.counters=[0,1,2]
ens=[4000,6000,8000,12000]
setts=[detectorSettings.STANDARD, detectorSettings.HIGHGAIN, detectorSettings.FAST]
ssetts=["standard","highgain","fast"]
gains=[40,50,20]
offs=[800,800,800]
tbs=np.zeros(1280*3,dtype=np.int32)
for en in ens:
    for isett in range(3):
        d.settings=setts[isett]
        d.dacs.vth1=int(offs[isett]+gains[isett]*en/1000.)
        d.dacs.vth2=int(offs[isett]+gains[isett]*en/1000.)
        d.dacs.vth3=int(offs[isett]+gains[isett]*en/1000.)
        d.dacs.vtrim=900
        dacs= d.dacs.to_array()
        tfname1="/afs/psi.ch/user/b/bergamaschi/project/Anna/slsDetectorPackageDeveloper/settingsdir/mythen3/"+ssetts[isett]+"/"+str(en)+"eV/trim.sn0000"
        print(tfname1)
        #my3.write_my3_trimbits_new(tfname1,np.int32(gain),np.int32(dacs),np.int32(tbs))
        my3.write_my3_trimbits(tfname1,np.int32(dacs),np.int32(tbs))



