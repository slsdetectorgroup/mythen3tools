import read_mythen as my3
import plot_scan as psc
import fit_scurve as fsc
import matplotlib.pyplot as plt
import numpy as np
import sys
argc=len(sys.argv)

ncounters=1
dr = 24
if argc<2:
    print("required: Input file,  scan min, scanmax, calibration file\n Optional: ncounters, dr")
    exit()

fname=sys.argv[1]

calFname=sys.argv[2]

trimFile=sys.argv[3]

if argc>4:
    ncounters=np.int(sys.argv[4])
#print("The files contain ",ncounters," counters")

if argc>5:
    dr=np.int(sys.argv[5])
#print("DR ",dr)


dacs=np.array([1200,2800,1280,2800,1220,2800,800,1708,1800,1100,1100,2624,1708,1712,2000,800],dtype=np.int32)
for idac in range(0,16):
    if argc>6+idac:
        dacs[idac]=np.int32(sys.argv[6+idac])

#dacvalues [vcassh 1200, vrshaper 2800, vrshaper_n 1280, vipre_out 2800, vth3 1220, vth1 2800, vicin 2800, vcas 1708, vrpreamp 1800, vcal_n 1100, vipre 1100, vishaper 2624, vcal_p 1708, vtrim 1712, vdcsh 2800, vthreshold 800, dac 0 2800]

#print(calFname)
flex,noise,ampl,cs,counts=fsc.load_scurve_fit_file(calFname)

#print(fname)
head, data=my3.read_my3_file(fname,ncounters,dr)


#print(trimFile)


inds=np.arange(0, 64)

#inds=np.flip(inds,0)

tb = np.empty(data.shape[1],dtype=np.int32)


for ich in  np.arange(0, data.shape[1]):
    tb[ich]=0
    val=data[:,ich]
    for itrim in inds:
        if val[itrim]>counts[ich]:
            #print(ich,counts[ich],val[itrim],itrim)
            tb[ich]=itrim
            break
    if tb[ich]<0:
        tb[ich]=0
    if tb[ich]>63:
        tb[ich]=63



trimbits3=np.repeat(tb,3)
my3.write_my3_trimbits(trimFile,dacs,trimbits3)

print(tb)


exit()

