import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys

ncounters=1
dr = 24

#head, adata=my3.read_my3_file()

#fname="/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/Ag_40kV_40mA_cnt0_TB0_d0_f0_1.raw"
fformat=sys.argv[1]#"/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/testTB0.raw"
smin=np.int(sys.argv[2])
smax=np.int(sys.argv[3])
sstep=1
#fformat="/mnt/mythen_data/Mythen3_module/cSAXSPolarizationAnalysis_202009/scan242_d0_f0_{}.raw" 300 500


print(fformat,smin,smax)


thr, data=my3.read_my3_files(fformat, smin, smax, sstep, ncounters, dr) 


psc.plot_thrscan(data,smin,smax,sstep)


