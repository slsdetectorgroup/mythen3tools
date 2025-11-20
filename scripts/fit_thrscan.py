import read_mythen as my3
import plot_scan as psc
import trimming as trim
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
#import ROOT

ncounters=1
dr = 24

fname=sys.argv[1]
smin=int(sys.argv[2])
smax=int(sys.argv[3])
logfile='fitparams.log'
initNph=1000 #initial number of photons
initFlex=1200 #initial inflection point (usually non influent)
chanmask=[]
nSigma=5

#open threshold scan data

head, data=my3.read_my3_file(fname,ncounters,dr)
if (data.shape[0]>1): 
    sstep=(smax-smin)/(data.shape[0]-1)
    psc.plot_thrscan(data,smin,smax,sstep)

thresholds = np.arange(smin, smax+sstep, sstep)

fsc.init_params(initFlex,initNph)
print('**badchans',chanmask)
flex,noise,ampl,cs,counts=fsc.fit_all(thresholds,data,chanmask)
print("saving results to",logfile)
if logfile!=None:
    fsc.save_scurve_fit_file(logfile,flex,noise,ampl,cs,counts)
 
for ich in chanmask:
    flex[ich]=0
    counts[ich]=0

fig, axs = plt.subplots(2, 1, figsize=(5, 10))

axs[0].plot(flex)
axs[0].set_title("Inflection point")

axs[1].plot(counts)
axs[1].set_title("Counts")

fig.show()

fig, axs = plt.subplots(2, 1, figsize=(5, 10))

axs[0].hist(flex[flex>0], bins=30)
axs[0].set_title("Inflection point")

axs[1].hist(counts[counts>0], bins=30)
axs[1].set_title("Counts")

fig.show()
