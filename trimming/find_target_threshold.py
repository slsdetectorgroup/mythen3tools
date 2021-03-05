import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
argc=len(sys.argv)

ncounters=1
dr = 24
if argc<5:
    print("required: Input file,  scan min, scanmax, output file\n Optional: nph, flex, ncounters, dr")
    exit()

fname=sys.argv[1]

smin=np.int(sys.argv[2])
#print("Scan minimum ",smin)

smax=np.int(sys.argv[3])
#print("Scan maximum ",smax)

outFname=sys.argv[4]

aa = 1000
if argc>5:
    aa=np.int(sys.argv[5])

ff = 1500

if argc>6:
    ff=np.int(sys.argv[6])

if argc>7:
    ncounters=np.int(sys.argv[7])
#print("The files contain ",ncounters," counters")

if argc>8:
    dr=np.int(sys.argv[8])
#print("Dynamic range is ",dr)
3

if argc>9:
    nSigma=np.int(sys.argv[9])

flex,noise,ampl,cs,counts=fsc.fit_file(fname,ncounters,dr,smin,smax,ff,aa)

fsc.save_scurve_fit_file(outFname,flex,noise,ampl,cs,counts)


nSigma=3

meanf=np.mean(flex[np.where(flex>0)])

sigmaf=np.sqrt(np.var(flex[(flex > meanf-300) & (flex < meanf+300)]))

meanf=np.mean(flex[(flex > meanf-300) & (flex < meanf+300)])
thr0=meanf+nSigma*sigmaf

if thr0>2800:
    thr0=2800


print(np.int(thr0))

exit()

