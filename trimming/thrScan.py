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

def acquire(d,rx,longwait=False):
    d.timing=timingMode.TRIGGER_EXPOSURE 
    d.startReceiver()
    d.startDetector()
    time.sleep(0.1)
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
        if longwait:
            time.sleep(0.75)
        while d.rx_framescaught==nf:
            d.sendSoftwareTrigger()
            time.sleep(d.exptime)
            time.sleep(0.1)
        #print(nf,"frames",d.rx_framescaught)
        nf=d.rx_framescaught
        #print(d.dacs.vth1,d.dacs.vth2,d.dacs.vth3,d.dacs.vtrim)
        for imod in range(len(d.hostname)):
            #print("imod",imod)
            dd, hh = rx[imod].receive_one_frame()
            fn=hh["frameIndex"]
            #print("frames",d.rx_framescaught,imod,nf)
            #        if dd is not None:
            data.append(dd)
            header.append(hh)
            #nodata=0
            #else:
            #    print("module",imod,"frame",i,"is none")
        #print(i,d.status,d.dacs.vth1)
        i+=1     
    d.stopDetector()
    d.stopReceiver()
    return data,header


#def stopAcquisition(d):
#    d.stopDetector()
#    d.stopReceiver()


    
def scan(d,rx,dac, minthr, maxthr, thrstep):
    sp=scanParameters()

    d.rx_zmqstream=1
    d.rx_zmqfreq=1


    sp.enable=1
    sp.startOffset=minthr
    sp.stopOffset=maxthr
    sp.stepSize=thrstep
    sp.dacSettleTime_ns = int(50e6)
    sp.dacInd=dac
    threshold=np.arange(sp.startOffset, sp.stopOffset+sp.stepSize,sp.stepSize)
    
    
    nmod=len(d.hostname)
    #print(nmod)
    ncol=len(d.counters)*1280
    nrow = len(threshold)
    data_thr = np.zeros((nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    d.setScan(sp)

    
    if dac==dacIndex.TRIMBIT_SCAN:
        longwait=True
    else:
        longwait=False

    data,header=acquire(d,rx,longwait)
    #print(len(data),len(header))
    #print(header[0])
   

    for i in range(int(len(header)/nmod)):
        for imod in range(nmod):
            fn=header[imod+i*nmod]["frameIndex"]
            #print(i,imod,fn)
            if data[imod+i*nmod] is not None:
                if fn<data_thr.shape[1]:
                    data_thr[imod,fn]=data[imod+i*nmod]
                else:
                    print(i, imod,header[imod+i*nmod])
   
    sp.enable=0
    d.setScan(sp)
    return data_thr

    """
    d.acquire()
    print("received ",d.rx_framescaught,"frames")
    for i in range(d.rx_framescaught+1):
        dd, header = rx.receive_one_frame()
        if dd is None:
            break
            if header["frameIndex"]<len(threshold):
                data_thr[ic,header["frameIndex"]]=dd
                nodata=0
    """


def makeReceiver(d):
    d.rx_zmqstream=1
    d.rx_zmqfreq=1
    rx = [] 
    nmod=len(d.hostname)
    for imod in range(nmod):
        zmqport=d.zmqport[imod]
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
    d.exptime=0.1
    d.fwrite=0
    smin=2800
    smax=600
    sstep=-10
    #smin=0
    #smax=63
    #sstep=1
    dac=dacIndex.VTH1
    #dac=dacIndex.VTH1
    data_thr=scan(d,rx,dac, smin, smax, sstep)
    psc.plot_thrscan(np.concatenate(data_thr,axis=1),smin,smax,sstep)
    return data_thr

