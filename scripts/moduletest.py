from slsdet import Mythen3
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt

def changeClkdDiv(val,off=0):
    d.clkdiv[0]=val
    d.clkdiv[1]=val
    d.clkdiv[2]=val
    d.writeRegister(0x110,off)

d = Mythen3()

d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
#print(d.hostname)

d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1


rx = ZmqReceiver(f"tcp://{d.zmqip}:{d.zmqport}")

d.counters=[0,1,2]
n_counters=len(d.counters)

#using the module with long cables
clkdiv=15
changeClkdDiv(clkdiv)

if clkdiv==10:
    d.writeRegister(0x110,0x80)
if clkdiv==15:
    d.writeRegister(0x110,0x70)
elif clkdiv==20:
    d.writeRegister(0x110,0x70)
else:
    d.writeRegister(0x110,0x60)

"""

print('TEST SERIAL IN')
val=0xbbbbbb
serInErrorMask1=testSerialIn(d,val)
val=0xaaaaaa
serInErrorMask2=testSerialIn(d,val)

if serInErrorMask2|serInErrorMask1==0:
    print("serial IN test succeeded")
else:
    print("serial IN test failed")

"""

d.fwrite=0
print('DIGITAL PULSING')

npuls=[0xaa,0xbb,0xcc]
#for i in range (0,65536):
 #   print("pulsing",hex(i),d.clkdiv[0])
good=[]
for i in range(4):
    for j in range(16):
        off=i | (j<<4)
        d.writeRegister(0x110,off)
        digPulseErrorMask,chipErrorMask=testDigitalPulsing(d,rx,npuls[0],npuls[1],npuls[2])
        if digPulseErrorMask==0:
            good.append(off)

if len(good)==0:
    print("no good offset found")

for i in range(len(good)):
    print(i,"GOOD OFFSET IS",hex(good[i]))
    d.writeRegister(0x110,good[0])



"""
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


data=np.empty(3, dtype=object)
flex0=np.empty(3, dtype=object)
ff=d.fname

for ic in range(0):
    

    d.dacs.vth1=2800
    d.dacs.vth2=2800
    d.dacs.vth3=2800
    
    d.counters=[ic]
    
    d.fwrite=1
    d.fname=ff+'_c'+str(ic)+'_tb0'
    d.trimval=0
    data[ic]=analogPulsingScan(d, rx,  npu, threshold)
    



    print("Fitting")
    fsc.init_params(1100,npu)
    fsc.init_fix_cs(0)
    fsc.init_fix_ampl(npu)

    #flex0[ic],noise0,ampl0,cs0,counts0=fsc.fit_all(threshold,data[ic])
    


d.counters=[0]
d.trimval=63



print("trimval 63")


d.dacs.vth1=2800
d.dacs.vth2=2800
d.dacs.vth3=2800

d.fname=ff+'_c0_tb63'
data63 = analogPulsingScan(d, rx,  npu, threshold)


print("Fitting")
fsc.init_params(1300,npu)
fsc.init_fix_cs(0)
fsc.init_fix_ampl(npu)

flex63,noise63,ampl63,cs63,counts63=fsc.fit_all(threshold,data63)





####Plotting..



figf,axf=plt.subplots()
for ic in range(3):
    fig0,ax0=psc.plot_simple_thrscan(np.where(data[ic]<npu*2,data[ic],npu*2),threshold)

    ax0.plot(np.where(flex0[ic]>0,flex0[ic],threshold[0]),'ro')
    fig0.show()

    lab="counter "+str(ic)+" tb 0"
    axf.hist(flex0[ic],bins=len(threshold),range=(threshold[-1],threshold[0]),label=lab)



fig63,ax63=psc.plot_simple_thrscan(np.where(data63<npu*2,data63,npu*2),threshold)
ax63.plot(np.where(flex63>0,flex63,threshold[0]),'ro')
fig63.show()


lab="counter 0 tb 63"
axf.hist(flex63,bins=len(threshold),range=(threshold[-1],threshold[0]),label=lab)

figf.show()

d.fname=ff
fig0,ax0=psc.plot_simple_thrscan(np.where(data[0]<npu*2,data[ic],npu*2),threshold)
fig0.show()

"""
