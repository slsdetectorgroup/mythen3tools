#from slsdet import Mythen3
#from patterntools.zmqreceiver import ZmqReceiver
#from detConf_module import *
import read_mythen as my3
import numpy as np
from slsdet.lookup import view, find
#import plot_scan as psc 
import fit_scurve as fsc
from trimming import *
import matplotlib.pyplot as plt



fname="/mnt/mythen_data/Mythen3_module/testData2/trimTest_TB0_c0_TB0_c0_TB0_c0_TB0_c0_d0_f0_3.raw"

counters=[0]
smin=2000
smax=800
sstep=-2
nph=2000
nsigma=5
outfname='/mnt/mythen_data/Mythen3_module/testData2/thrdispMyTrimbitsCu.trim'
dr=32

head, data=my3.read_my3_file(fname,len(counters),dr)


initFlex=1500

#thrmin,initFlex,nph=fsc.find_start_param(data,smin,smax,sstep)
#print("Start value for inflection point is",initFlex)
#print("Start value for number of counts is",nph)
#print("Fit down to",thrmin)


thr,counts=find_target_threshold(data, smin, smax, nph, initFlex, 5, outfname)

plt.plot(counts)
plt.show()
