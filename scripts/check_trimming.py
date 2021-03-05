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

tf=["/sls/X04SA/Data1/ES2/now/Mythen3_20200122/12000eV/fast/defaultGain/fast_defaultGain_12000eV_200V_400ms_2", \
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/12000eV/highgain/defaultGain/highgain_defaultGain_12000eV_200V_400ms_2",\
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/12000eV/standard/defaultGain/standard_defaultGain_12000eV_200V_400ms_1",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/15000eV/fast/defaultGain/fast_defaultGain_15000eV_200V_300ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/15000eV/highgain/defaultGain/highgain_defaultGain_15000eV_200V_300ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/15000eV/standard/defaultGain/standard_defaultGain_15000eV_200V_300ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/18000eV/fast/defaultGain/fast_defaultGain_18000eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/18000eV/highgain/defaultGain/highgain_defaultGain_18000eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/18000eV/standard/defaultGain/standard_defaultGain_18000eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/7100eV/fast/defaultGain/fast_defaultGain_7100eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/7100eV/highgain/defaultGain/highgain_defaultGain_7100eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/7100eV/standard/defaultGain/standard_defaultGain_7100eV_200V_1000ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/fast/defaultGain/fast_defaultGain_9000eV_200V_500ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/fast/highestGain/fast_highestGain_9000eV_200V_500ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/highgain/defaultGain/highgain_defaultGain_9000eV_200V_500ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/highgain/defaultGain/highgain_defaultGain_9000eV_200V_500ms_1",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/highgain/highestGain/highgain_highestGain_9000eV_200V_500ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/standard/defaultGain/standard_defaultGain_9000eV_200V_500ms_0",
"/sls/X04SA/Data1/ES2/now/Mythen3_20200122/9000eV/standard/highestGain/standard_highestGain_9000eV_200V_500ms_0"]
"""
for tformat in tf:
    for imod in range(nmod):
        tfname=tformat+'.sn'+str(sn[imod]).zfill(4)
        dacs,tb=my3.read_my3_trimbits(tfname)
        print(tfname, dacs, tb)
        #vth[imod]=dacs[dacIndex.VTH1]
"""









#fname="/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/Ag_40kV_40mA_cnt0_TB0_d0_f0_1.raw"
fformat=sys.argv[1]#"/mnt/mythen_data/Mythen3_module/Module030161/testTrimming/testTB0.raw"

tformat=sys.argv[2]

smin=np.int(sys.argv[3])
smax=np.int(sys.argv[4])
sstep=np.int(sys.argv[5])
ncol=1280
thr = np.arange(smin, smax+sstep, sstep)
nrow=len(thr)
data = np.zeros((nmod,3,nrow,ncol), dtype =  np.int32)
for imod in range(nmod):
    for ic in range(3):
        fname=fformat.format(ic,imod)
        print(fname)
        head, data[imod,ic]=my3.read_my3_file(fname,ncounters,dr)
    #if (data.shape[0]>1): 
        #psc.plot_thrscan(data,smin,smax,sstep)

vth=np.zeros((nmod,3))
vth_new=np.zeros((nmod,3))
dacs=np.zeros((nmod,16),dtype=np.int32)
tb=np.zeros((nmod,1280*3),dtype=np.int32)
for imod in range(nmod):
    tfname=tformat+'.sn'+str(sn[imod]).zfill(4)
    dacs[imod],tb[imod]=my3.read_my3_trimbits(tfname)
    #print(tfname, dacs, tb)
    ind=dacNames['vth1']
    vth[imod,0]=dacs[imod,np.int(ind)]
    ind=dacNames['vth2']
    vth[imod,1]=dacs[imod,np.int(ind)]
    ind=dacNames['vth3']
    vth[imod,2]=dacs[imod,np.int(ind)]
  
inds=np.digitize(vth,thr)

vals = np.zeros((nmod,3,ncol), dtype =  np.int32)
vals1 = np.zeros((nmod,3,ncol), dtype =  np.int32)
proj = np.zeros((nmod,3,nrow), dtype =  np.int32)
bads=[]


for imod in range(nmod):
    fig2 = plt.figure(figsize=(6, 6))
    ax= fig2.add_subplot()
    for ic in range(3):
        vals[imod,ic]=data[imod,ic,inds[imod,ic]]
        proj[imod,ic]=np.median(data[imod,ic], axis=1)
        params=fsc.init_params(vth[imod,ic], 2000)#3*np.median(vals[imod,ic]))
        result=fsc.fit_scurve(thr, proj[imod,ic], params)
        vth_new[imod,ic]=result.params['flex'].value
        vals1[imod,ic]=data[imod,ic,np.digitize(result.params['flex'].value,thr)]
        print(vth[imod,ic],vth_new[imod,ic])
        ax.plot(thr, proj[imod,ic], 'o')
        #plt.plot(thr[0:result.init_fit.shape[0]], result.init_fit, 'k--', label='initial fit')
        plt.plot(thr[0:result.init_fit.shape[0]], result.best_fit, '-', label='best fit')
    ax.legend(loc='best')  
    fig2.show()
    #print(result.fit_report())
 

    """
        pp=vals[imod]
        vv=np.median(vals[imod])
        v1=np.array(np.where(pp<0.5*vv))+1280*imod
        v2=np.array(np.where(pp>2*vv))+1280*imod
        bads=np.append(bads,v1)
        bads=np.append(bads,v2)
    """
    tfname1=tformat+'_new.sn'+str(sn[imod]).zfill(4)
    dacs[imod,np.int(ind)]=vth_new[imod,0]
    ind=dacNames['vth2']
    dacs[imod,np.int(ind)]=vth_new[imod,1]
    ind=dacNames['vth3']
    dacs[imod,np.int(ind)]=vth_new[imod,2]
    my3.write_my3_trimbits(tfname1,np.int32(dacs),np.int32(tb))

    print(vth[imod],vth_new[imod])  

for ic in range(3):
    fig,ax=plt.subplots()
    ax.plot(np.concatenate(vals[:,ic]),label="old")
    ax.plot(np.concatenate(vals1[:,ic]),label="new")
    ax.legend(loc='best') 
    fig.show()
