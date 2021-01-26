import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
#from slsdet import Mythen3, scanParameters,dacIndex #Mythen3,scanParameters, 
import fit_scurve as fsc

ncounters=1
dr = 24
nmod=12

dacNames={'vcassh':0,'vth2':1,'vrfsh':2,'vrfshnpol':3,'vipreout':4,'vth3':5,'vth1':6,'vicin':7,'vcas':8,'vpreamp':9,'vph':10,'vipre':11,'viinsh':12,'vpl':13,'vtrim':14,'vdcsh':15}
#head, adata=my3.read_my3_file()
sn=[0x18, 0x19, 0x1a, 0x1d, 0x1e, 0x1f, 0x20, 0x2, 0x4, 0x17, 0x15, 0x1b]

ens=np.zeros(3,dtype=np.float)
tbf=np.empty(3,dtype=object)

for ien in range(3):
    ens[ien]=np.float(sys.argv[ien*2+1])
    tbf[ien]=sys.argv[ien*2+2]


inds=[dacNames['vth1'], dacNames['vth2'], dacNames['vth3'], dacNames['vtrim']]
print(ens[0],ens[1],ens[2])
dacs=np.zeros((3,16),dtype=np.int32)
tbs=np.zeros((3,1280*3),dtype=np.int32)
for imod in range(nmod):
    for ien in range(2):
        tfname=tbf[ien]+'.sn'+str(sn[imod]).zfill(4)
        dacs[ien],tbs[ien]=my3.read_my3_trimbits(tfname)
        if ien==0:
            for idac in range(16):
                dacs[2,idac]=dacs[0,idac]
    for idac in inds:
        m=(dacs[1,idac]-dacs[0,idac])/(ens[1]-ens[0])
        dacs[2,idac]=m*(ens[2]-ens[0])+dacs[0,idac]
        if dacs[2,idac]>2800:
            dacs[2,idac]=2800
        if dacs[2,idac]<0:
            dacs[2,idac]=0
        print(idac,dacs[0,idac],dacs[1,idac],dacs[2,idac])
    for ich in range(1280*3):
        m=(tbs[1,ich]-tbs[0,ich])/(ens[1]-ens[0])
        tbs[2,ich]=m*(ens[2]-ens[0])+tbs[0,ich]
        if tbs[2,ich]<0:
            tbs[2,ich]=0
        if tbs[2,ich]>63:
            tbs[2,ich]=63
        #print(ich,tbs[0,ich],tbs[1,ich],tbs[2,ich])
    
    tfname=tbf[2]+'.sn'+str(sn[imod]).zfill(4)       
    print(tfname,dacs[2])
    my3.write_my3_trimbits(tfname,np.int32(dacs[2]),np.int32(tbs[2]))
