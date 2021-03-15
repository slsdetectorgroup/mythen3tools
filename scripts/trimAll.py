from slsdet import Mythen3,detectorSettings
from slsdet.lookup import view, find

from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from trimming import *


energy=9400
exptime=0.5
findex=0

nph=[7500,7000,5000,4000,3800,3500,3200,2800,2600,2400,2300,2200,2100,2000]
chanmask=[[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

d= Mythen3()
rx=makeReceiver(d)
d.exptime=exptime
d.findex=findex
fpath='/sls/X04SA/Data1/ES2/now/Mythen3_20210305/'+str(energy)+'eV/'
d.fwrite=1


d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1


for igain in range(1):
    if igain==0:
        setDefaultMode(d)
        gain="defaultGain"
    if igain==1:
        setHighestGainMode(d)
        gain="highestGain"
    if igain==3:
        setLowestGainMode(d)
        gain="lowestGain"
    if igain==2:
        setSuperHighGainMode(d)
        gain="superHighGain"
        

    for isett in range(2):
        if isett==0:
            d.settings=detectorSettings.STANDARD
            sett="standard"
            if igain==0:
                minthr=1500
            """
            if igain==1:
                minthr=1500
            if igain==2:
                minthr=2400
            """
        if isett==1:
            d.settings=detectorSettings.HIGHGAIN
            d.dacs.vrpreamp=1350
            d.dacs.vrshaper=1100
            sett="highgain"
            if igain==0:
                minthr=1800
            """
            if igain==1:
                minthr=2000
            if igain==2:
                minthr=2400
            """
        if isett==2:
            d.settings=detectorSettings.FAST
            sett="fast"
            if igain==0:
                minthr=1400
            """
            if igain==1:
                minthr=1500
            if igain==2:
                minthr=2400
            """
            

        d.fpath=fpath+sett+'/'+gain+'/'
        ff=sett+'_'+gain+'_'+str(energy)+'eV_200V_'+str(int(1000*exptime))+'ms'

        print(d.fpath, ff)
        d.fname=ff
        #print(d.hostname)

        d.fwrite=1


        
        d.counters=[0,1,2]
        #minthr=1500
        maxthr=900
        thrstep=-2
        nsigma=5

        ind=d.findex

        if igain==0:
            vth,vtrim,trimbits=trim(ff, d,rx,minthr, maxthr, thrstep,nph, nsigma, chanmask, 1)
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

setDefaultMode(d)
