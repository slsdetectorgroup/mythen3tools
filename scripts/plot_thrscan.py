import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
#import ROOT

ncounters=1
dr = 24

#head, adata=my3.read_my3_file()

#fname="/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/Ag_40kV_40mA_cnt0_TB0_d0_f0_1.raw"
fname=sys.argv[1]#"/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/testTB0.raw"
smin=int(sys.argv[2])
smax=int(sys.argv[3])

head, data=my3.read_my3_file(fname,ncounters,dr)
if (data.shape[0]>1): 
    sstep=(smax-smin)/(data.shape[0]-1)
    thr = np.arange(smin, smax+sstep, sstep)
    psc.plot_thrscan(data,smin,smax,sstep)


