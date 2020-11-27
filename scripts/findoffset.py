from slsdet import Mythen3
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt
import sys

def changeClkdDiv(val,off=0):
    d.clkdiv[0]=val
    d.clkdiv[1]=val
    d.clkdiv[2]=val
    d.writeRegister(0x110,off)

d = Mythen3()

##d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
#print(d.hostname)

d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1


rx = ZmqReceiver(f"tcp://{d.zmqip}:{d.zmqport}")

d.counters=[0,1,2]
n_counters=len(d.counters)

#using the module with long cables
clkdiv=np.int(sys.argv[1])
changeClkdDiv(clkdiv)

d.fwrite=0
print('DIGITAL PULSING')

npuls=[0xaa,0xbb,0xcc]
#for i in range (0,65536):
 #   print("pulsing",hex(i),d.clkdiv[0])
good=[]
goodph=[]
for i in range(4):
    for j in range(16):
        off=i | (j<<4)
        d.writeRegister(0x110,off)
        for ph in np.arange(0,180+10,10):
            d.setClockPhaseinDegrees(1,ph)
            digPulseErrorMask,chipErrorMask=testDigitalPulsing(d,rx,npuls[0],npuls[1],npuls[2])
            if digPulseErrorMask==0:
                good.append(off)
                goodph.append(ph)
if len(good)==0:
    print("no good offset found")
else:
    for i in range(len(good)):
        print(i,"GOOD OFFSET IS",hex(good[i]),"PHASE",hex(goodph[i]))
    d.writeRegister(0x110,good[0])
    d.setClockPhaseinDegrees(1,goodph[0])

    d.fname='testOff'
    npu=100
    smin=2000
    smax=800
    sstep=-10
    threshold = np.arange(smin, smax+sstep, sstep)


    d.dacs.vth1=2800
    d.dacs.vth2=2800
    d.dacs.vth3=2800
    d.dacs.vcal_n=1100
    d.dacs.vcal_p=1200
    d.dacs.vtrim=900


    ff=d.fname

    

    d.dacs.vth1=2800
    d.dacs.vth2=2800
    d.dacs.vth3=2800
        
    d.counters=[0,1,2]
    
    d.fwrite=1
    d.fname=ff+'_clk'+str(clkdiv)
    d.trimval=0
    data=analogPulsingScan(d, rx,  npu, threshold)
    


    d.fname=ff
    fig0,ax0=psc.plot_simple_thrscan(np.where(data<npu*2,data,npu*2),threshold)
    fig0.show()


