import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
argc=len(sys.argv)

ncounters=1
dr = 24
if argc<6:
    print("required: Input file,  scan min, scanmax, calibration file, outfile\n Optional: ncounters, dr")
    exit()

fname=sys.argv[1]

smin=np.int(sys.argv[2])
#print("Scan minimum ",smin)

smax=np.int(sys.argv[3])
#print("Scan maximum ",smax)

calFname=sys.argv[4]
outFname=sys.argv[5]

if argc>6:
    ncounters=np.int(sys.argv[6])
#print("The files contain ",ncounters," counters")

if argc>7:
    dr=np.int(sys.argv[7])
#print("Dynamic range is ",dr)

nSigma=3

if argc>8:
    nSigma=np.int(sys.argv[8])
#flex,noise,ampl,cs,counts=fsc.fit_file(fname,ncounters,dr,smin,smax,ff,aa)

flex,noise,ampl,cs,counts=fsc.load_scurve_fit_file(calFname)

head, data=my3.read_my3_file(fname,ncounters,dr)




if (data.shape[0]>1):
    sstep=(smax-smin)/(data.shape[0]-1)

vtrim = np.arange(smin, smax+sstep, sstep)

inds=np.arange(0, vtrim.shape[0])
if sstep>0:
    inds=np.flip(inds,0)


for ich in  np.arange(0, data.shape[1]):
    flex[ich]=0
    val=data[:,ich]
    for itrim in inds:  
        if val[itrim]>counts[ich]:
            flex[ich]=vtrim[itrim]
            #print(ich,val[itrim],counts[ich],vtrim[itrim])
            break
        

np.savetxt(outFname, flex,  encoding=None)
meanf=np.mean(flex[np.where(counts>0)])
sigmaf=np.sqrt(np.var(flex[(flex > meanf-300) & (flex < meanf+300)]))

meanf=np.mean(flex[(flex > meanf-300) & (flex < meanf+300)])
#sigmaf=np.sqrt(np.var(flex[np.where(counts>0)]))


vtrim0=meanf-nSigma*sigmaf

if vtrim0<0:
    vtrim0=0

print(np.int(vtrim0))

exit()

