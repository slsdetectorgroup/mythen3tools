from slsdet import Mythen3,timingMode,detectorSettings,runStatus
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
import numpy as np
from slsdet.lookup import view, find
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt

d = Mythen3()

#d.loadConfig('../slsDetectorPackageDeveloper/examples/my30module_standard.config')
#print(d.hostname)

d.stopReceiver()

d.counters=[0,1,2]
n_counters=len(d.counters)

d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1

d.period=0

rx = ZmqReceiver(f"tcp://{d.zmqip}:{d.zmqport}")

#d.trimbits='/mnt/mythen_data/Mythen3_module/testData2/myTrimbitsCu.trim'

setPumpProbeMode(d)

t=1.





d.parallel=0

d.frames=1

dt=t/(d.frames)

d.exptime=dt
d.gatedelay=[0,dt,2*dt]



d.fname='pumpprobe_one_frame'

d.acquire()


nodata=1
print("received ",d.rx_framescaught,"frames")
for i in range(d.rx_framescaught+1):
    dd, header = rx.receive_one_frame()
    if dd is None:
        break
    #print(":-)")
    oneframe=dd
        


d.frames=1000

dt=t/(d.frames)

d.parallel=0

d.exptime=dt
d.gatedelay=[0,dt,2*dt]




d.fname='pumpprobe_no_parallel'

d.acquire()


nodata=1
print("received ",d.rx_framescaught,"frames")
for i in range(d.rx_framescaught+1):
    dd, header = rx.receive_one_frame()
    if dd is None:
        break
    #print(":-)")
    if nodata==1:
        noparallel=dd
        nodata=0
    else:
        noparallel=noparallel+dd
        


d.parallel=1
d.fname='pumpprobe_parallel'
d.acquire()

nodata=1
print("received ",d.rx_framescaught,"frames")
for i in range(d.rx_framescaught+1):
    dd, header = rx.receive_one_frame()
    if dd is None:
        break
    #print(":-)")
    if nodata==1:
        parallel=dd
        nodata=0
    else:
        parallel=parallel+dd
        

fig, ax = plt.subplots()
#ax.title('Counts')
ax.plot(oneframe,label='one frame')
ax.plot(noparallel, label='10000 frames non parallel')
ax.plot(parallel, label='10000 frames parallel')
ax.legend()
fig.show()


vv=np.array(noparallel,dtype=np.int32)-np.array(oneframe,dtype=np.int32)
vv1=np.array(parallel,dtype=np.int32)-np.array(oneframe,dtype=np.int32)
fig1, ax1 = plt.subplots()
#ax1.title('Residuals')
ax1.plot(vv,label='non parallel')
ax1.plot(vv1,label='parallel')
ax1.legend()
fig1.show()

val=max(10.,np.sqrt(np.var(oneframe)))
fig2, ax2 = plt.subplots()
#ax2.title('Residuals')
ax2.hist(vv,bins=100,label='non parallel',histtype='step',range=(-val,val))
ax2.hist(vv1,bins=100,label='parallel',histtype='step',range=(-val,val))
ax2.legend()
fig2.show()
