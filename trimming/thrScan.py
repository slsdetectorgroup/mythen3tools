from slsdet import Mythen3,timingMode,detectorSettings,runStatus,dacIndex,scanParameters
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
#import fit_scurve as fsc
import matplotlib.pyplot as plt


#def startAcquisition(d):
    ## use for many modules until fixed
"""
def acquire(d,rx,longwait=False):
    #d.timing=timingMode.TRIGGER_EXPOSURE 
    d.startReceiver()
    d.startDetector()
    #print("before:",d.status)
    i=0
    data=[]

    header=[]
    nodata=1
    nf=0
    while d.status != runStatus.IDLE:
    #for iframe in range(len(threshold)):
        #print(threshold[iframe])
        nodata=1
        #while nodata==1:
        time.sleep(0.1)
        if longwait:
            time.sleep(0.75)
        while d.rx_framescaught==nf:
            d.sendSoftwareTrigger()
            time.sleep(d.exptime)
            #time.sleep(0.15)
        #print(nf,"frames",d.rx_framescaught)
        
        nf=d.rx_framescaught
        #time.sleep(0.05)

        #print(d.dacs.vth1,d.dacs.vth2,d.dacs.vth3,d.dacs.vtrim)
        for imod in range(len(d.hostname)):
            #print("imod",imod)
            dd, hh = rx[imod].receive_one_frame()
            fn=hh["frameIndex"]
            data.append(dd)
            header.append(hh)
            if fn!=i:
                print(imod,"**",i,fn)
        i+=1   
    print("Acquired ",d.rx_framescaught,fn,i)
    #d.stopDetector()
    #d.stopReceiver() 
    #receive dummy packet
    for imod in range(len(d.hostname)):
        dd, hh = rx[imod].receive_one_frame()
            
    return data,header


#def stopAcquisition(d):
#    d.stopDetector()
#    d.stopReceiver()

"""
 
def acquireFrame(d,rx, ax1=None):
    

    nmod=len(d.hostname)

    d.rx_zmqstream=1
    d.rx_zmqfreq=1
    d.startReceiver()
    d.startDetector()
    #d.acquire()  
    #d.status
    data=np.zeros((nmod,len(d.counters)*1280), dtype =  to_dtype(d.dr))
    header=[]
    nf0=0
    time.sleep(d.exptime)
    while d.status != runStatus.IDLE:
        time.sleep(0.01)

    nf=np.min(d.rx_framescaught)
    if nf>nf0:
    #for iframe in range(nf):
        nf0=nf
        for imod in range(len(d.hostname)):
            dd, hh = rx[imod].receive_one_frame()
            if dd is not None:
                data[imod]=dd
            if imod==0:
                print(hh["frameIndex"])
   

                
    d.stopReceiver()
    #receive dummy packet
    for imod in range(len(d.hostname)):
        dd, hh = rx[imod].receive_one_frame()
    #sp.enable=0
    #d.setScan(sp)
    if ax1 is not None:
        aa=np.concatenate(data,axis=0)
        ax1.plot(aa)
    return data
   
def scan(d,rx,dac, minthr, maxthr, thrstep):
    sp=scanParameters()

    d.rx_zmqstream=1
    d.rx_zmqfreq=1


    sp.enable=0
    #sp.startOffset=minthr
    #sp.stopOffset=maxthr
    #sp.stepSize=thrstep
    #sp.dacSettleTime_ns = int(50e6)
    #sp.dacInd=dac
    #threshold=np.arange(sp.startOffset, sp.stopOffset+sp.stepSize,sp.stepSize)
    
    
    nmod=len(d.hostname)
    #print(nmod)
    ncol=len(d.counters)*1280
    threshold=np.arange(minthr,maxthr+thrstep,thrstep)
    nrow = len(threshold)
    data_thr = np.zeros((nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    d.setScan(sp)

    
    #if dac==dacIndex.TRIMBIT_SCAN:
    #    longwait=True
    #else:
    #    longwait=False
    ff=d.fname
    ind=d.findex
    data=[]
    header=[]
    nf0=0
    d.startReceiver()
    for ith in range(minthr,maxthr+thrstep,thrstep):
        #d.fname=ff+"_S"+str(ith)
        #d.findex=ind

        if dac==dacIndex.TRIMBIT_SCAN:
            d.trimval=ith
            #print("tb",ith);
        if dac==dacIndex.VTH1:
            d.dacs.vth1=ith
            #print("vth1",d.dacs.vth1);
        if dac==dacIndex.VTH2:
            d.dacs.vth2=ith
            #print("vth2",d.dacs.vth2);
        if dac==dacIndex.VTH3:
            d.dacs.vth3=ith
            #print("vth3",d.dacs.vth3);
        if dac==dacIndex.VTRIM:
            d.dacs.vtrim=ith
            #print("vtrim",d.dacs.vtrim);
        #print(d.settings,d.exptime,d.timing)
        time.sleep(0.05)
        d.startDetector()
        #d.acquire()  
        #print(d.status)
        time.sleep(d.exptime)
        while d.status != runStatus.IDLE:
            time.sleep(0.01)
            #print(d.status)

        nf=np.min(d.rx_framescaught)
        if nf>nf0:
        #for iframe in range(nf):
            nf0=nf
            for imod in range(len(d.hostname)):
                dd, hh = rx[imod].receive_one_frame()
                data.append(dd)
                header.append(hh)
                #if imod==0:
                    #print(ith, hh["frameIndex"])
   

    for i in range(int(len(header)/nmod)):
        for imod in range(nmod):
            fn=header[imod+i*nmod]["frameIndex"]
            if data[imod+i*nmod] is not None:
                if fn<data_thr.shape[1]:
                    data_thr[imod,fn]=data[imod+i*nmod]
                else:
                    print(i, imod,header[imod+i*nmod])
            else:
                print(i, imod,"lost frame")
                
    d.stopReceiver()
    #receive dummy packet
    for imod in range(len(d.hostname)):
        dd, hh = rx[imod].receive_one_frame()
    #sp.enable=0
    #d.setScan(sp)
    return data_thr


def makeReceiver(d):
    d.rx_zmqstream=1
    d.rx_zmqfreq=1
    rx = [] 
    nmod=len(d.hostname)
    for imod in range(nmod):
        if nmod>1:
            zmqport=d.zmqport[imod]
        else:
            zmqport=d.zmqport
        rx.append(ZmqReceiver(f"tcp://{d.zmqip}:{zmqport}"))
    return rx

def thrScan(dac, smin, smax, sstep):
    d = Mythen3()
    #d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
    #print(d.hostname)
    rx=makeReceiver(d)
    data_thr=scan(d,rx,dac, smin, smax, sstep)
    psc.plot_thrscan(np.concatenate(data_thr,axis=1),smin,smax,sstep)
    return data_thr


#psc.plot_thrscan(data_thr[0],smin,smax,sstep)
#psc.plot_thrscan(data_thr[1],smin,smax,sstep)
def testThrscan():

    d = Mythen3()
    #d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
    #print(d.hostname)
    rx=makeReceiver(d)

    d.counters=[0]
    n_counters=len(d.counters)
    #d.exptime=0.1
    d.fwrite=0
    smin=1500
    smax=900
    sstep=-5
    #smin=0
    #smax=63
    #sstep=1
    dac=dacIndex.VTH1
    #dac=dacIndex.VTH1
    data_thr=scan(d,rx,dac, smin, smax, sstep)
    psc.plot_thrscan(np.concatenate(data_thr,axis=1),smin,smax,sstep)
    plt.plot(np.median(np.concatenate(data_thr,axis=1),axis=1))
    plt.show()
    return data_thr

