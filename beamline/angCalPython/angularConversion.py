
import read_mythen as my3

import plot_scan as psc

import fit_scurve as fsc

import matplotlib.pyplot as plt

import numpy as np

import sys

#import ROOT

import csv


import os.path

import ang_conv as ac
"""
from lmfit import  Model
r0=-762 #negative if the module is "flipped"

c0=1280./2.

off0=20
 

 

angpeak=69.225

angmin=angpeak-0.1

angmax=angpeak+0.1

"""
 

 

ncounters=1

dr = 24

 

#head, adata=my3.read_my3_file()

 



fformat="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/angularCalibration_15keV_1s_d{}_f0_100.raw"
logfile="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/angularCalibration_15keV_1s_100.log"
ffformat="/mnt/mythen_data/Diamond_20240523/newAngularCalibration/flatfield/flatField_15keV_th7500eV_d{}_f0_101.raw"




minmod=1
nmod=28
#nmod=25

smin=2
smax=87
sstep=0.1

ncol=1280
#thr = np.arange(smin, smax, sstep)


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


"""

fig1, axs1 = plt.subplots()
for imod in range(minmod,nmod):
    axs1.plot(ffcorr[imod])
    axs1.plot(fferr[imod])
    #print(np.mean(ffcorr[imod]),np.mean(fferr[imod]),np.sum(fd)/1280.,np.sqrt(np.sum(fd)/1280.))
fig1.show()
"""

angles = np.genfromtxt(logfile)

print(angles.shape,data.shape)




cols=['r','b','g','m','y','c','k','tab:pink','tab:gray','tab:olive','tab:orange','tab:purple','tab:brown']

offs=np.zeros((nmod),dtype=np.float64)
rs=np.zeros((nmod),dtype=np.float64)
cs=np.zeros((nmod),dtype=np.float64)

x=np.empty((0),dtype=np.float64)
y=np.empty((0),dtype=np.float64)

icol=0
ac.reset_binning()
fig2, axs2 = plt.subplots()
for imod in np.arange(minmod,nmod):

    peaks=np.array([],dtype=np.float64)

    angs=np.array([],dtype=np.float64)

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
    if os.path.isfile('ang_d'+str(ii)+'.off')!=True:
        print("can't find ang conv ",'ang_d'+str(ii)+'.off')
        continue

    with open('ang_d'+str(ii)+'.off') as f:
        line=f.read()
    f.close()
    print(line)
    #module 10 offset 17.997807296250137 conv -6.561462368464345e-05 center 686.3666306286403
    off0=np.float64(line.split(' ')[3])
    r0=0.05/np.float64(line.split(' ')[5])
    c0=np.float64(line.split(' ')[7])
    
    ch_ang=ac.module_angles(off0,r0,c0)

    #read bad channels

    mask = np.ones(ch_ang.shape, dtype=bool)
    if os.path.isfile('bad_d'+str(ii)+'.chans')!=True:
        print("can't find bad channel file ",'bad_d'+str(ii)+'.chans')
        continue
    bchm=np.empty((0),dtype=np.int32)
    #bchm=np.genfromtxt('bad_d'+str(ii)+'.chans')
   
    with open('bad_d'+str(ii)+'.chans') as f:
        line=f.read()
        try: 
            cc=np.int32(line)
        except ValueError:
            bchm=bchm
        else:
            bchm=np.concatenate((bchm,np.array([cc],dtype=np.int32)))
    f.close()
    print(imod," - ",bchm.shape," bad channels")
    if bchm.shape[0]>0:
        mask[bchm]=False
    if bchm.shape[0]>1000:
        print("Too many bad channels ",ii,bchm.shape[0])
        continue

    icol=0
    ch_ang=ac.module_angles(off0,r0,c0)
    for iang in np.arange(0,angles.shape[0],85):
        ang=ch_ang+angles[iang]
        cdata,cerr=ac.ffcorr(data[imod][iang],ffcorr[imod],fferr[imod])
        ac.add_to_binning(ang,cdata,cerr)
angs,d_b,e_b=ac.finalize_binning()
axs2.plot(angs,d_b)
fig2.show()
