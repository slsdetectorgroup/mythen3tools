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
nmod=np.int(sys.argv[2])
smin=np.int(sys.argv[3])
smax=np.int(sys.argv[4])
sstep=np.int(sys.argv[5])
ncol=1280
thr = np.arange(smin, smax+sstep, sstep)
nrow=len(thr)
data = np.zeros(nmod, dtype =  object)
for imod in range(nmod):
    print(fformat,imod)
    fname=fformat.format("{}",imod)
    print(fname)
    head, data[imod]=my3.read_my3_files(fname,smin,smax,sstep,ncounters,dr)
    #if (data.shape[0]>1): 
        #psc.plot_thrscan(data,smin,smax,sstep)

print(np.concatenate(data,axis=0).shape)
print(np.concatenate(data,axis=1).shape)
#print(np.concatenate(data,axis=2).shape)
print(12*1280,len(thr))
plt.ion()
psc.plot_thrscan(np.concatenate(data,axis=1),smin,smax,sstep)

