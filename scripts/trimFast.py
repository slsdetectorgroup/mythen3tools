from slsdet import Mythen3,detectorSettings
from slsdet.lookup import view, find

from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from trimming import *
from thrScan import *
import numpy as np
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt
import sys
import read_mythen as my3
import time
import multiprocessing as mp


acquireThresholdScan=1
fitData=1
findTrimbits=1
testTrimming=1
plot=1

nmod=1
gain="defaultGain"
sett="standard"

energy=7500
#calculate ca. 700+50*keV+100
minthr=1400
#no need to change it
maxthr=900
thrstep=-5
vtrim=1000



#5400
exptime=0.1
nph=[7000]
chanmask=[[]]
chanmask[0]=list(range(896,1280))
fpath='/mnt/mythen_data/Mythen3_module/trimTests/'+sett+'/'+gain+'/'
fname=sett+'_'+gain+'_'+str(energy)+'eV_200V_'+str(int(1000*exptime))+'ms'
findex=0


if acquireThresholdScan==1 or findTrimbits==1:
    d= Mythen3()
    rx=makeReceiver(d)
    d.exptime=exptime
    d.findex=findex
    d.fwrite=1
    d.fpath=fpath
    d.highvoltage=200
    d.stopReceiver()
    d.rx_zmqstream=1
    d.rx_zmqfreq=1
    setDefaultMode(d)
    d.settings=detectorSettings.STANDARD
    #setHighestGainMode(d)
    #d.settings=detectorSettings.HIGHGAIN
    #setLowGainMode(d)
    #d.settings=detectorSettings.STANDARD
    ind=d.findex
    d.counters=[2]
    d.dacs.vtrim=vtrim

ff=fname+'_TB32'

if acquireThresholdScan==1:
    d.fname=ff
    dac=dacIndex.VTH3
    d.trimval=32
    data_thr= scan(d,rx,dac, minthr, maxthr, thrstep)
else:
    thr=np.arange(minthr, maxthr+thrstep, thrstep)
    data_thr = np.zeros((nmod,len(thr),1280), dtype =  np.int32)
    for imod in range(nmod):
        fn=fpath+'/'+ff+'_d'+str(imod)+'_f0_'+str(findex)+'.raw'
        print("Opening file",fn)
        head, data_thr[imod]=my3.read_my3_file(fn,1,24)

if plot:
    psc.plot_thrscan(np.concatenate(data_thr,axis=1), minthr, maxthr, thrstep)


    
vth= np.zeros((nmod), dtype = np.int32)
counts= np.zeros((nmod,1280), dtype = np.int32)
cfname=str(fpath)+'/thrdisp_'+ff+'_'+str(findex)
if fitData:
    pool = mp.Pool(processes=nmod)
    args=[]
    for imod in range(nmod):
        cmfname=str(fpath)+'/thrdisp_'+ff+'_d'+str(imod)+'_'+str(findex)+'.dat'
        arg=[]
        arg.append(data_thr[imod])
        arg.append(minthr)
        arg.append(maxthr)
        arg.append(nph[imod])
        arg.append(1500) #guess for inflection point 
        arg.append(0)#nsigma not used in this case
        arg.append(cmfname)
        arg.append(chanmask[imod])
        args.append(arg)
    results = pool.map(find_target_threshold_pool, args)
    print("fitting done");
    for imod in range(nmod):
        vth[imod],counts[imod]=results[imod]
    print("writing to file",cfname+'.npy')
    with open(cfname+'.npy','wb') as f:
        np.save(f,vth)
        np.save(f,counts)
else:
    with open(cfname+'.npy','rb') as f:
        vth=np.load(f)
        counts=np.load(f)

for imod in range(nmod):
    print ("MODULE",imod,"THRESHOLD",vth[imod],"\n COUNTS:",counts[imod]);
    d.dacs.vth3=vth[imod]
        
if plot:     
    fig, ax = plt.subplots()
    ax.plot(np.concatenate(counts))
    fig.show()

    
ff=fname+'_TBscan'
if findTrimbits:
    d.fname=ff
    trimbits=search_trimbits(d,rx,counts)
    d.counters=[0,1,2]
    for imod in range(nmod):
        d.dacs.vth1[imod]=vth[imod]
        d.dacs.vth2[imod]=vth[imod]
        d.dacs.vth3[imod]=vth[imod]
    dacs= d.dacs.to_array()
    d.counters=[2]
    print(dacs)
    gain=d.getGainCaps()[0]
    print(gain)
    sn=d.getModuleId()
    for imod in range(nmod):
        fn=fpath+'/'+fname+'_'+str(findex)+'.sn'+str(sn[imod]).zfill(4)
        print(fn)
        my3.write_my3_trimbits_new(fn,np.int32(gain),np.int32(dacs[:,imod]),np.int32(trimbits[:,imod]))
    if plot:     
        fig, ax = plt.subplots()
        ax.plot(np.concatenate(trimbits))
        fig.show()


ff=fname+'_trimmed'

if testTrimming==1:
    d.trimbits = fpath+'/'+fname+'_'+str(findex)
    d.fname=ff
    dac=dacIndex.VTH3
    data_thr= scan(d,rx,dac, minthr, maxthr, thrstep)
    
    if plot:
        psc.plot_thrscan(np.concatenate(data_thr,axis=1), minthr, maxthr, thrstep)
