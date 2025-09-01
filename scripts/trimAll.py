from slsdet import Mythen3,detectorSettings
from slsdet.lookup import view, find

from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from trimming import *


energy=5400
#5400
exptime=0.1
findex=100
nph=[3000,2500]#,4000, 4000, 3000]
#nph=[4000, 4000]
#chanmask=[[],[]]
chanmask=[[],[]]#,[],[],[]]
#chanmask[0]=list(range(512,578))+list(range(630,680))+list(range(128*6,128*7))+list(range(128*9, 128*10))
#chanmask[2]=range(128*2, 128*3)

d= Mythen3()
rx=makeReceiver(d)
d.exptime=exptime
d.findex=findex
d.dacs.vicin=1500
fpath='/mnt/mythen_data/Mythen3_module/trimI0ADDAMS_20250618/'
d.fwrite=1

d.highvoltage=200

d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1


for igain in range(0,1):
    if igain==0:
        minthr=1600
        setDefaultMode(d)
        gain="defaultGain"
        d.settings=detectorSettings.STANDARD
        sett="standard"

    if igain==1:
        minthr=2400
        setHighestGainMode(d)
        gain="highestGain"
        d.settings=detectorSettings.HIGHGAIN
        sett="highgain"
   
    if igain==2:
        minthr=1800
        setLowGainMode(d)
        gain="lowGain"
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
    ff=sett+'_'+gain+'_'+str(energy)+'eV_200V_'+str(int(1000*exptime))+'ms'

    print(d.fpath, ff)
    d.fname=ff
    #print(d.hostname)

    d.fwrite=1


        
    d.counters=[0,1,2]
    maxthr=900
    thrstep=-2
    nsigma=3

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


d.counters=[0]

#d.highvoltage=0
