from slsdet import Mythen3
import mythen3tools as m3
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc




d = Mythen3()

d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
#print(d.hostname)

d.stopReceiver()

d.rx_zmqstream=1
d.rx_zmqfreq=1


rx = m3.ZmqReceiver(f"tcp://{d.zmqip}:{d.zmqport}")

d.counters=[0,1,2]
n_counters=len(d.counters)



print('TEST SERIAL IN')
val=0xbbbbbb
serInErrorMask1=testSerialIn(d,val)
val=0xaaaaaa
serInErrorMask2=testSerialIn(d,val)

if serInErrorMask2|serInErrorMask1==0:
    print("serial IN test succeeded")
else:
    print("serial IN test failed")





print('DIGITAL PULSING')
npuls=[8,5,3]
digPulseErrorMask,chipErrorMask=testDigitalPulsing(d,rx,8,5,3)
print('done')

"""

npu=1000
smin=2000
smax=800
sstep=-5
threshold = np.arange(smin, smax+sstep, sstep)


d.dacs.vth1=2800
d.dacs.vth2=2800
d.dacs.vth3=2800
d.dacs.vcal_n=1100
d.dacs.vcal_p=1400
d.dacs.vtrim=900


data=np.empty(3, dtype=object)
for ic in range(3):
    

    d.dacs.vth1=2800
    d.dacs.vth2=2800
    d.dacs.vth3=2800
    
    d.counters=[ic]
    
    d.trimval=0
    data[ic]=analogPulsingScan(d, rx,  npu, threshold)
    



    print("Fitting")
    fsc.init_params(1100,npu)
    fsc.init_fix_cs(0)
    fsc.init_fix_ampl(npu)

    fig0,ax0=psc.plot_simple_thrscan(np.where(data[ic]<npu*2,data[ic],npu*2),threshold)
    flex0,noise0,ampl0,cs0,counts0=fsc.fit_all(threshold,data[ic])
    ax0.plot(np.where(flex0>0,flex0,threshold[0]),'ro')
    fig0.show()



d.counters=[0]
d.trimval=63



print("trimval 63")


d.dacs.vth1=2800
d.dacs.vth2=2800
d.dacs.vth3=2800

data63 = analogPulsingScan(d, rx,  npu, threshold)

fig63,ax63=psc.plot_simple_thrscan(np.where(data63<npu*2,data63,npu*2),threshold)
fig63.show()

print("Fitting")
fsc.init_params(1300,npu)
fsc.init_fix_cs(0)
fsc.init_fix_ampl(npu)

flex63,noise63,ampl63,cs63,counts63=fsc.fit_all(threshold,data63)
ax63.plot(np.where(flex63>0,flex63,threshold[0]),'ro')

"""
