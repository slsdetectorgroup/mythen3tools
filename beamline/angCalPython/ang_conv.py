
import read_mythen as my3

import plot_scan as psc

import fit_scurve as fsc

import matplotlib.pyplot as plt

import numpy as np

import sys

#import ROOT

import csv

from lmfit import  Model

import os.path

 

def gaussian(x, amp, cen, wid, b, a):

    #"1-d gaussian: gaussian(x, amp, cen, wid)"

    #return (amp/(np.sqrt(2*np.pi)*wid)) * np.exp(-(x-cen)**2 /(2*wid**2))+b+a*(x-cen)
    return (amp) * np.exp(-(x-cen)**2 /(2*wid**2))+b+a*(x-cen)

 
binsize=0.004#376 #4mdeg bins
angle_bins=np.arange(-180-binsize,180+binsize,binsize)
angle_bin_centers=(angle_bins[1:]+angle_bins[:-1])*0.5

nbins=angle_bins.shape[0]-1
data_bins=np.zeros((nbins),dtype=np.float64)
error_bins=np.zeros((nbins),dtype=np.float64)
mult_bins=np.zeros((nbins),dtype=np.float64)

def reset_binning():
    data_bins.fill(0)
    mult_bins.fill(0)
    error_bins.fill(0)
    
def finalize_binning():
    mult_bins[mult_bins==0]=-1
    d=data_bins/mult_bins
    e=np.sqrt(error_bins/mult_bins)
    #data_bins=d
    #error_bins=e
    a=np.where(mult_bins>0)[0]
    #print(a)
    return angle_bin_centers[a[0]:a[-1]],d[a[0]:a[-1]],e[a[0]:a[-1]]

def add_to_binning(angles,vals, errs):
    #print(angles,angle_bins[bins-1],angle_bins[bins])
    stripsize=np.abs(angles[1:]-angles[:-1])
    #print(stripsize[0],stripsize[640])
    if (angles[1]-angles[0])>0:
        bins=np.searchsorted(angle_bins,angles,side='left')
        binmin=bins[:-1]
        binmax=bins[1:]
    else:
        bins=np.searchsorted(angle_bins,angles,side='right')
        binmin=bins[:-1]-1
        binmax=bins[1:]-1
    #print(angles,angle_bins[binmin],angle_bins[binmax])
    #print(binmin,binmax,binmax-binmin,np.where((binmax-binmin)!=1))
    aa=np.where(np.abs(binmax-binmin)==1)
    bb=np.where(np.abs(binmax-binmin)!=1)
    #print("good bin size",aa)
    #print("bin size",bb,angle_bins[binmin[bb]],np.abs(binmax[bb]-binmin[bb]))
    w=np.abs(angle_bins[binmin]-angles[:-1])
    data_bins[binmin[aa]-1]+=data_bins[binmin[aa]-1]+vals[aa]*w[aa]/stripsize[aa]
    error_bins[binmin[aa]-1]+=error_bins[binmin[aa]-1]+(errs[aa])**2*(w[aa]/stripsize[aa])# ** 2 #*errs[aa]*w[aa]/stripsize[aa]
    mult_bins[binmin[aa]-1]+=mult_bins[binmin[aa]-1]+w[aa]/stripsize[aa]
    w1=np.abs(angles[1:]-angle_bins[binmin])
    data_bins[binmax[aa]-1]+=data_bins[binmax[aa]-1]+vals[aa]*w1[aa]/stripsize[aa]
    mult_bins[binmax[aa]-1]+=mult_bins[binmax[aa]-1]+w1[aa]/stripsize[aa]
    error_bins[binmax[aa]-1]+=error_bins[binmax[aa]-1]+(errs[aa]**2)*(w1[aa]/stripsize[aa])#**2 #*errs[aa]*w1[aa]/stripsize[aa]
    aa=np.where(np.abs(binmax-binmin)<1)
    #print("bin size too large",aa)
    #print(angles[aa],angle_bins[binmin[aa]],angle_bins[binmax[aa]])
    data_bins[binmax[aa]-1]+=data_bins[binmax[aa]-1]+vals[aa]
    error_bins[binmax[aa]-1]+=error_bins[binmax[aa]-1]+errs[aa]**2#*errs[aa]
    mult_bins[binmax[aa]-1]+=mult_bins[binmax[aa]-1]+1
    if len(np.where(np.abs(binmax-binmin)>1)[0])>0:
        print("bin size too small!",np.where(np.abs(binmax-binmin)>1))
    
    #print("weights",np.where((w+w1)!=stripsize))
    
    #print("bin size too small!",np.where((binmax-binmin)>1))
    #print("bin size too large!",np.where((binmax-binmin)<1))
    #mult_bins=mult_bins+

def module_angles(off,r,c=1279.*0.5,dir=1,p=0.05):
    x=np.arange(-0.5,1280)
    #print(x)
    ang=off+np.degrees(c*p/np.abs(r)+dir*np.arctan(p*(x-c)/r))
    #print(ang)
    return ang

def test():
    off0=20
    r0=-762
    vals=gaussian(np.arange(-640,640), 1000, 0, 100, 5)
    errs=np.sqrt(vals)
    
    angles=module_angles(off0,r0)
    
    reset_binning()
    add_to_binning(angles,vals,errs)
    angs,d_b,e_b=finalize_binning()
    
    plt.plot((angles[:-1]+angles[1:])*0.5,vals)
    plt.plot((angles[:-1]+angles[1:])*0.5,errs)
   
    plt.plot(angs,d_b)
    plt.plot(angs,e_b)
    plt.show()


def calc_ffcorr(fd):
    fftot=np.sum(fd,axis=0)
    fftot[fftot==0]=1
    me=np.median(fftot)
    ffcorr=me/fftot
    fferr=np.sqrt(fftot)/fftot*ffcorr
    return ffcorr,fferr

def ffcorr(data, ffcorr,fferr): 
    cdata=data*ffcorr
    cerr=cdata*np.sqrt(1./data+(fferr/ffcorr)**2)
    return cdata,cerr
