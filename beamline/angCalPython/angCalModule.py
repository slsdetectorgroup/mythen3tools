
import read_mythen as my3

import plot_scan as psc

import fit_scurve as fsc

import matplotlib.pyplot as plt

import numpy as np

import sys

#import ROOT

import csv

from lmfit import  Model

 
import ang_conv as ac




r0=-762 #negative if the module is "flipped"

c0=1280./2.

off0=20

 

 

angpeak=69.225

angmin=angpeak-0.1
angmax=angpeak+0.1

 

mingood=0.5*(angmax-angmin)/ac.binsize
print(mingood)

ncounters=1

dr = 24


fformat="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/angularCalibration_15keV_1s_d{}_f0_100.raw"
logfile="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/angularCalibration_15keV_1s_100.log"
ffformat="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/flatfield/flatField_15keV_th7500eV_d{}_f0_101.raw"



minmod=1
nmod=28

smin=2
smax=87
sstep=0.1

ncol=1280
thr = np.arange(smin, smax, sstep)
nrow=len(thr)

data = np.zeros((nmod,nrow,ncol), dtype =  np.int32)
#ffcorr = np.zeros((nmod,ncol), dtype =np.float64)
ffcorr = np.zeros((nmod,ncol), dtype =np.float64)
fferr = np.zeros((nmod,ncol), dtype =np.float64)
for imod in range(minmod,nmod):
    fname=fformat.format(imod)
    head, data[imod]=my3.read_my3_file(fname,ncounters,dr)    
    fffname=ffformat.format(imod)
    head,fd=my3.read_my3_file(fffname,ncounters,dr)
    #psc.plot_thrscan(fd, 0, fd.shape[0]-1,1 )
    ffcorr[imod],fferr[imod]=ac.calc_ffcorr(fd)
    #print(imod,np.sum(fd),np.sum(fftot))

print(np.median(ffcorr,axis=1))

"""
fig1, axs1 = plt.subplots()
for imod in range(minmod,nmod):
    axs1.plot(ffcorr[imod])
    #axs1.plot(fferr[imod])
    #print(np.mean(ffcorr[imod]),np.mean(fferr[imod]),np.sum(fd)/1280.,np.sqrt(np.sum(fd)/1280.))
fig1.show()
"""

badchans=np.where((ffcorr<0.5) | (ffcorr>1.5))

for imod in np.arange(minmod,nmod):

    #off0=65-5.003*imod-7.925
    ii=imod
    #correcting for missing modules!
    """if ii>13:
        ii=imod+1
    if ii>17:
        ii=imod+2
    if ii>18:
        ii=imod+3
    """
    bchm=badchans[1][np.where(badchans[0]==imod)]
    myfile = open('bad_d'+str(ii)+'.chans', 'w')
    for ich in bchm:
        myfile.write(str(ich)+'\n')
    myfile.close()



angles = np.genfromtxt(logfile)

#print(angles.shape,data.shape)

imod=9
fname=fformat.format(imod)


cols=['r','b','g','m','y','c','k','tab:pink','tab:gray','tab:olive','tab:orange','tab:purple','tab:brown']

off1=np.zeros((nmod),dtype=np.float64)
r1=np.zeros((nmod),dtype=np.float64)
c1=np.zeros((nmod),dtype=np.float64)
off1=np.zeros((nmod),dtype=np.float64)
gmodel = Model(ac.gaussian)
for imod in np.arange(minmod,nmod):

    #peaks=np.array([],dtype=np.float64)

    #angs=np.array([],dtype=np.float64)

    #

    #off0=65-5.003*imod-7.925
    ii=imod
    #correcting for missing modules!
    """if ii>13:
        ii=imod+1
    if ii>17:
        ii=imod+2
    if ii>18:
        ii=imod+3
    """
    if ii<14:
        off0=62.455-5.003*ii+5.54
        r0=762
    else:
        off0=5.003*(ii-14)+0.45
        r0=-762
        
    ch_ang=ac.module_angles(off0,r0,c0)
    
    mask = np.ones(ch_ang.shape, dtype=bool)
    bchm=badchans[1][np.where(badchans[0]==imod)]

    myfile = open('bad_d'+str(ii)+'.chans', 'w')
    for ich in bchm:
        myfile.write(str(ich)+'\n')
    myfile.close()

    print(imod," - ",bchm.shape," bad channels",bchm)
    mask[bchm]=False
    if bchm.shape[0]>1000:
        continue

    good_angles=[]
    for iang in np.arange(0,angles.shape[0]):
        ang=ch_ang+angles[iang]
        angrange=np.where((ang[:-1]>angmin) & (ang[:-1]<angmax) &  (ffcorr[imod]>0.7) & (ffcorr[imod]<1.3))[0]
        if angrange.shape[0]>mingood:
            good_angles.append(iang)

    rs= np.arange(r0-5,r0+5,0.1)
    cs= np.arange(c0,c0+1,1)
    chi2=np.zeros((rs.shape[0],cs.shape[0]))
    for ir,r in enumerate(rs):
        #print(r)
        for ic,c in enumerate(cs):
            #print(c)
            nang=0
            ch_ang=ac.module_angles(off0,r,c)
            for i,iang in enumerate(good_angles[1:-1]):
                ang=ch_ang+angles[iang]
                angrange=np.where((ang[:-1]>angmin) & (ang[:-1]<angmax) &  (ffcorr[imod]>0.7) & (ffcorr[imod]<1.3))[0]
                cdata,cerr=ac.ffcorr(data[imod][iang],ffcorr[imod],fferr[imod])
                ac.reset_binning()
                ac.add_to_binning(ang,cdata,cerr)
                angs,d_b,e_b=ac.finalize_binning()
                angrange1=np.where((angs>angmin) & (angs<angmax))[0]
                if (nang==0):
                    nang=len(angrange1)
                    angdata=np.zeros((len(good_angles),nang),dtype=np.float64)
                    #angerr=np.array((len(good_angles),nang),dtype=np.float64)
                if (nang==len(angrange1)):
                    angdata[i,:]=d_b[angrange1]
                    #angerr[iang]=d_e[angrange1]
                var=np.var(angdata,axis=0)
                chi2[ir,ic]=np.sum(var)
    k = chi2.argmin()
    x1=int(k/chi2.shape[1]) 
    y1=k%chi2.shape[1]
    #print("###",x1,y1,rs[x1],cs[y1],chi2[x1,y1])
    #print("***",x1,y1,rs[y1],cs[x1],chi2[y1,x1])
    r1[imod]=rs[x1]
    c1[imod]=cs[y1]

    #z = np.polyfit(rs, chi2, 2)
    #r1[imod]=-z[1]/(2*z[0])
    #c1[imod]=c0


    ch_ang=ac.module_angles(off0,r1[imod],c1[imod])

    nang=0
    ac.reset_binning()
    for i,iang in enumerate(good_angles[1:-1]):
        ang=ch_ang+angles[iang]
        angrange=np.where((ang[:-1]>angmin) & (ang[:-1]<angmax) &  (ffcorr[imod]>0.7) & (ffcorr[imod]<1.3))[0]
        cdata,cerr=ac.ffcorr(data[imod][iang],ffcorr[imod],fferr[imod])
        ac.add_to_binning(ang,cdata,cerr)
    angs,angall,angerr=ac.finalize_binning()
    angrange1=np.where((angs>angmin) & (angs<angmax))[0]
    #result = gmodel.fit(angall[angrange1], x=angs[angrange1], amp=np.max(angall[angrange1]), cen=angpeak, wid=0.03,b=0, a=0)
    gmodel.set_param_hint('a',vary=False)
    gmodel.set_param_hint('b',vary=False)
    result = gmodel.fit(angall[angrange1], x=angs[angrange1], amp=np.max(angall[angrange1]), cen=angpeak, wid=0.02,b=0, a=0) 
    print(result.params)
    """
    fig1, ax1 = plt.subplots()
    ax1.plot(angs[angrange1],angall[angrange1],'ro')
    ax1.plot(angs[angrange1], result.init_fit, 'y-', lw=2)
    ax1.plot(angs[angrange1], result.best_fit, 'b-', lw=2)
    fig1.show()
    """
    off1[imod]=angpeak-result.params['cen'].value+off0
    print(imod,'r=',r1[imod],'c=',c1[imod],'o=',off1[imod],'chi2=',chi2[k]) 



fig2, ax2 = plt.subplots()
angall1=None
binsall1=None
for imod in np.arange(minmod,nmod):
    ch_ang=ac.module_angles(off1[imod],r1[imod],c0)
    nang=0
    good_angles=[]
    for iang in np.arange(0,angles.shape[0]):
        ang=ch_ang+angles[iang]
        angrange=np.where((ang[:-1]>angmin) & (ang[:-1]<angmax) &  (ffcorr[imod]>0.7) & (ffcorr[imod]<1.3))[0]
        if angrange.shape[0]>mingood:
            good_angles.append(iang)
        
    ac.reset_binning()
    for i,iang in enumerate(good_angles[1:-1]):
        ang=ch_ang+angles[iang]
        angrange=np.where((ang[:-1]>angmin) & (ang[:-1]<angmax) &  (ffcorr[imod]>0.7) & (ffcorr[imod]<1.3))[0]
        cdata,cerr=ac.ffcorr(data[imod][iang],ffcorr[imod],fferr[imod])
        ac.add_to_binning(ang,cdata,cerr)
    angs,d_b,e_b=ac.finalize_binning()
    angrange1=np.where((angs>angmin) & (angs<angmax))[0]

    if (nang==0):
        nang=len(angrange1)

    if angall1 is None:
        angall1=np.zeros((nmod,nang),dtype=np.float64)
    if binsall1 is None:
        binsall1=np.zeros((nmod,nang),dtype=np.float64)
    angall1[imod,:]=d_b[angrange1]
    angall1[imod,:]= angall1[imod,:]#/np.max(angall1[imod,:])
    binsall1[imod,:]=angs[angrange1]
    ax2.plot(binsall1[imod,:],angall1[imod,:])
fig2.show()




for imod in np.arange(minmod,nmod):
    ii=imod
    myfile = open('ang_d'+str(ii)+'.off', 'w')
    #line='** module '+str(ii)+' offset '+str(off0)+' conv '+str(0.05/r0)+' center '+str(c0)+'\n'
    #print(line)
    line='module '+str(imod)+' offset '+str(off1[imod])+' conv '+str(0.05/r1[imod])+' center '+str(c1[imod])+'\n'
    print(line)
    myfile.write(line)
    myfile.close()

