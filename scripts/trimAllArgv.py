from slsdet import Mythen3,detectorSettings
from slsdet.lookup import view, find

from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from trimming import *
import sys


energy=sys.argv[1]#6400
#5400
exptime=0.1
findex=7
nph=[int(sys.argv[2])]
#[10000]
#nph=[4000, 4000]
#chanmask=[[],[]]
chanmask=[[]]
#chanmask[0]=range(128*9, 128*10)

d= Mythen3()
rx=makeReceiver(d)
d.exptime=exptime
d.findex=findex
fpath='/mnt/mythen_data/Mythen3_module/moduleSuperXAS20220429New/'
d.fwrite=1


d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1


for igain in [0,1,2]:#range(1):
    if igain==0:
        #minthr=1200
        setDefaultMode(d)
        gain="defaultGain"
        d.settings=detectorSettings.STANDARD
        sett="standard"

    if igain==1:
        #minthr=1200
        setHighestGainMode(d)
        gain="highestGain"
        d.settings=detectorSettings.HIGHGAIN
        sett="highgain"
   
    if igain==2:
        setHighestGainMode(d)
        gain="highestGain"
        d.settings=detectorSettings.STANDARD
        sett="standard"
    """
    if igain==3:
        #d.setGainCaps(0)
        setSuperHighGainMode(d)
        gain="superHighGain"
    
    if igain==4:
        setLowestGainMode(d)
        gain="lowestGain"
    """
    
    """
    M3_C10pre

    M3_C15sh

    M3_C30sh
    
    M3_C50sh
    
    M3_C225ACsh

    M3_C15pre    
    """
   
            

    d.fpath=fpath+sett+'/'+gain+'/'
    ff=sett+'_'+gain+'_'+str(energy)+'_200V_'+str(int(1000*exptime))+'ms'

    print(d.fpath, ff)
    d.fname=ff
    #print(d.hostname)

    d.fwrite=1


        
    d.counters=[0,1,2]
    maxthr=800
    minthr=2000
    thrstep=-2
    nsigma=5

    ind=d.findex

        #if igain==0:
    vth,vtrim,trimbits=trim(ff, d,rx,minthr, maxthr, thrstep,nph, nsigma, chanmask, 1)
    """
        else:
            d.trimval=0
            for ic in range(1):
                d.findex=ind
                d.fname=ff+'_TB0_c'+str(ic)
                d.counters=[ic]
                d.dacs.vth1=2800
                d.dacs.vth2=2800
                d.dacs.vth3=2800    
                if ic==0:
                    dac=dacIndex.VTH1
                elif ic==1:
                    dac=dacIndex.VTH2
                elif ic==2:
                    dac=dacIndex.VTH3
                print("*** Threshold scan counter",ic)
                data_thr= scan(d,rx,dac, minthr, maxthr, thrstep)
    """

setDefaultMode(d)
#d.setGainCaps(int(slsdet.M3_GainCaps.M3_C30sh)|int(slsdet.M3_GainCaps.M3_C15pre))
d.settings=detectorSettings.STANDARD

