from slsdet import Mythen3,scanParameters, dacIndex
#from slsdet.lookup import view, find
from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from thrScan import *
import numpy as np
import plot_scan as psc 
import fit_scurve as fsc
import matplotlib.pyplot as plt
import sys
import read_mythen as my3
import time
import multiprocessing as mp

def find_target_threshold(data, smin, smax, initNPh, initFlex, chanmask, nSigma=5, outFname=None):

    if (data.shape[0]>1):
        sstep=(smax-smin)/(data.shape[0]-1)
    else:
        return 0,0,0,0

    thresholds = np.arange(smin, smax+sstep, sstep)

    #plt.contourf(np.arange(0,data.shape[1]), thresholds, data, 100, cmap=plt.cm.jet)
    #plt.show()

    fsc.init_params(initFlex,initNPh)
    
    flex,noise,ampl,cs,counts=fsc.fit_all(thresholds,data)

    if outFname!=None:
        fsc.save_scurve_fit_file(outFname,flex,noise,ampl,cs,counts)

    thr0=0
    for ich in chanmask:
        flex[ich]=0
        counts[ich]=0


    vv=flex[np.where(flex>0)]
    a=nSigma
    if a==0:
        a=3

    a=3

    if len(vv)>0:
        #meanf=np.median(vv)
        #sigmaf=np.sqrt(np.var(vv))
        #print("Max ",max(vv),"Min ",min(vv))
        #if sigmaf>50:
        #    sigmaf=50
        #vv=flex[(flex > meanf-a*sigmaf) & (flex < meanf+a*sigmaf)]
        if len(vv):
            sigmaf=np.sqrt(np.var(vv))
            meanf=np.median(vv)
            print("Max ",max(vv),"Min ",min(vv))
        thr0=meanf+nSigma*sigmaf
        print("MEAN",meanf,"RMS",sigmaf)
        thr0=min(thr0,max(vv))

    if thr0>2500:
        thr0=2500
    if len(counts[counts==0])>0:
        counts[counts==0]=np.median(counts[counts>0])

    return thr0,counts


def find_target_threshold_pool(arg):
    data=arg[0] 
    smin=arg[1] 
    smax=arg[2] 
    initNPh=arg[3] 
    initFlex=arg[4] 
    nSigma=arg[5] 
    outFname=arg[6]
    chanmask=arg[7]
    return find_target_threshold(data, smin, smax, initNPh, initFlex, chanmask, nSigma, outFname)

def find_target_vtrim(data, smin, smax, counts,chanmask, nSigma=5):
    if (data.shape[0]>1):
        sstep=(smax-smin)/(data.shape[0]-1)
    else:
        sstep=1
        print("NO SCAN!")
    vtrim = np.arange(smin, smax+sstep, sstep)
    inds=np.arange(0, vtrim.shape[0])
    if sstep>0:
        inds=np.flip(inds,0)
    flex=np.ndarray(data.shape[1], dtype=np.float)

    for ich in  np.arange(0, data.shape[1]):
        flex[ich]=0
        val=data[:,ich]
        for i, itrim in enumerate(inds,start=-0):
        #for itrim in inds:  
            flex[ich]=vtrim[itrim]
            if val[itrim]>counts[ich]:
                #if itrim==0 or itrim==63:
                #flex[ich]=vtrim[itrim]
                #print(ich,vtrim[itrim],val[itrim],counts[ich])
                #else:
                #    #(counts-val[itrim])=(val[itrim-val[itrim-1])/(vtrim[itrim]-vtrim[itrim-1])*(vt-vtrim[itrim])
                #    flex[ich]=(vtrim[itrim]-vtrim[inds[i-1]])/(val[itrim]-val[inds[i-1]])*(counts[ich]-val[itrim])+vtrim[itrim]
                #    print(ich,"**",counts[ich],flex[ich],vtrim[itrim],vtrim[itrim-1],val[itrim],val[itrim-1])
                #if counts[ich]>0:
                #    print(ich,val[itrim],counts[ich],vtrim[itrim])
                break

        if flex[ich]==vtrim[0]:
            print(ich,flex[ich],counts[ich],val)
        if flex[ich]==vtrim[-1]:
            print(ich,flex[ich],counts[ich],val)
    #print("flex\n",flex)
    #print("counts\n",counts)
    #vtrim0=600
    vtrim0=800

    for ich in chanmask:
        counts[ich]=0

    vv=flex[np.where(counts>0)]
    a=nSigma
    if a==0:
        a=3

    #a=2

    if len(vv)>0:
        meanf=np.median(vv)
        sigmaf=np.sqrt(np.var(vv))
        print("Median vtrim ",meanf," Sigma vtrim ",sigmaf)
        print(vv)
        #vv=flex[(flex > meanf-a*sigmaf) and (flex < meanf+a*sigmaf)]
        #if len(vv)>0:
        #    meanf=np.median(vv)
        #    sigmaf=np.sqrt(np.var(vv))
        vtrim0=meanf-nSigma*sigmaf
        #print(np.median(counts),np.median(vv),"MEAN",meanf,"RMS",sigmaf)
    else:
        print("all counts are 0!")

    vtrim0=max(vtrim0,min(vv))
    
    if len(counts[counts==0])>0:
        counts[counts==0]=np.median(counts[counts>0])

    #if vtrim0<600:
    #    vtrim0=600   
    #if vtrim0<600:
    #    vtrim0=600     
    return vtrim0

def find_trimbits(data, counts, smin=0, smax=63):
    print(data.shape,smin,smax)
    if (data.shape[0]>1):
        sstep=(smax-smin)/(data.shape[0]-1)

    trims = np.arange(smin, smax+sstep, sstep)

    inds=np.arange(0, trims.shape[0])


    tb = np.empty(data.shape[1],dtype=np.int32)
    for ich in  np.arange(0, data.shape[1]):
        tb[ich]=0
        val=data[:,ich]
        for itrim in inds:
            tb[ich]=trims[itrim]
            if val[itrim]>counts[ich]-np.sqrt(counts[ich]):
                #print(ich,counts[ich],val[itrim],itrim)
                #if itrim>0:
                #    tb[ich]=int((trims[itrim]-trims[itrim-1])/(val[itrim]-val[itrim-1])*(counts[ich]-val[itrim])+trims[itrim])
                if itrim<trims.shape[0]-1:
                    #print(ich,counts[ich],val[itrim],val[itrim+1])
                    if val[itrim+1]>counts[ich]-np.sqrt(counts[ich]):
                        break
                else:
                    break

        if tb[ich]<0:
            tb[ich]=0
        if tb[ich]>63:
            tb[ich]=63
        if tb[ich]==63:
            print(ich,counts[ich],data[:,ich])

    return tb

def trim_f(d,rx,minthr, maxthr, thrstep, nph, chanmask, nsigma=5, verbose=1):
    
    counters=d.counters
    nmod=len(d.hostname)
    #sp=scanParameters()
    pool = mp.Pool(processes=nmod)

    fn=d.fname
    ind=d.findex
    
    d.rx_zmqstream=1
    d.rx_zmqfreq=1

    ###########################################################
    # Threshold scan with trimbits=0 to find target threshold
    ###########################################################
    #sp.enable=1
    #sp.startOffset=minthr
    #sp.stopOffset=maxthr
    #sp.stepSize=thrstep
    #sp.dacSettleTime_ns = int(50e6)
    
    threshold=np.arange(minthr, maxthr+thrstep,thrstep)
    d.trimval=0
    d.dacs.vtrim=2800
    
    ncol=1280

    nrow = len(threshold)
    vth= np.zeros((len(counters),nmod), dtype = np.int)
    counts= np.zeros((3,nmod,1280), dtype = np.int)
    data_thr = np.zeros((3,nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    #ii=0
    outfname=None
    ff=1500
    dac=dacIndex.VTH1
    for ic in [0]:#counters:
        d.findex=ind
        d.fname=fn+'_TB0_c'+str(ic)
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
        data_thr[ic]= scan(d,rx,dac, minthr, maxthr, thrstep)
        psc.plot_thrscan(np.concatenate(data_thr[ic],axis=1), minthr, maxthr, thrstep)
        
        args=[]
        for imod in range(nmod):
            #if len(nph)==1:
            #    nph1=nph
            #else:
            #    nph1=nph[imod]
            if ic>0:
                ff=vth[0,imod]
                #v=np.median(counts[0,imod])
                #va=np.sqrt(np.var(counts[0,imod]))
                #if v>0.1*nph and v<2*nph:
                #    nph1=v
                """
                vth[ic,imod],counts[ic,imod]=find_target_threshold(data_thr[ic,imod], minthr, maxthr, nph, ff, nsigma, outfname)
                #ii=ii+1
                print("MODULE",imod,"THRESHOLD",ic,"IS",vth[ic,imod],"; MEAN COUNTS",np.mean(counts[ic,imod]))
                """
            arg=[]
            arg.append(data_thr[ic,imod])
            arg.append(minthr)
            arg.append(maxthr)
            arg.append(nph[imod])
            arg.append(ff) 
            arg.append(nsigma) 
            if verbose==1:
                outfname=str(d.fpath)+'/thrdisp_'+fn+'_TB0_c'+str(ic)+'_d'+str(imod)+'_'+str(ind)+'.dat'
            arg.append(outfname)
            arg.append(chanmask[imod])
            args.append(arg)
        #pool = mp.Pool(processes=nmod)
        #results = [pool.apply(find_target_threshold, args=(data_thr[ic,imod], minthr, maxthr, nph, ff, nsigma, outfname,)) for imod in range(nmod)]
        print("*** Fitting counter",ic)
        results = pool.map(find_target_threshold_pool, args)
        #print(results)
        for imod in range(nmod):
            vth[ic,imod],counts[ic,imod]=results[imod]
            print ("MODULE",imod,"COUNTER",ic,"THRESHOLD",vth[ic,imod]);
                   
        
        fig, ax = plt.subplots()
        ax.plot(np.concatenate(counts[ic]))
        fig.show()
        
    for ic in range(1,3):
        for imod in range(nmod):
            vth[ic,imod]= vth[0,imod]
            counts[ic,imod]=counts[0,imod]
        

    ###########################################################
    # Vtrim scan with trimbits=63 to find target vtrim
    ###########################################################


    vtrimMin=0
    #vtrimMin=600
    vtrimMax=2800
    vtrimStep=20

    dac=dacIndex.VTRIM
    vtrims=np.arange(vtrimMin, vtrimMax+vtrimStep,vtrimStep)

    d.trimval=63

    nrow = len(vtrims)
    vtrim= np.zeros((3,nmod), dtype = np.int)
    data_vtrim = np.zeros((3,nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    #ii=0
    outfname=None
    #######################
    # To speed up the process, I find Vtrim only for counter 0 assuming that the others are similar
    ######################

    for ic in [0]: #counters:

        d.findex=ind
        d.fname=fn+'_TB63_c'+str(ic)

        d.counters=[ic]

        ncol=1280

        d.dacs.vth1=2800
        d.dacs.vth2=2800
        d.dacs.vth3=2800
        
        if ic==0:
            print("counter",ic)
            print(vth[ic])
            for imod in range(nmod):
                d.dacs.vth1[imod]=vth[ic,imod]
            print(d.dacs.vth1)
        elif ic==1:
            print("counter",ic)
            print(vth[ic])
            for imod in range(nmod):
                d.dacs.vth2[imod]=vth[ic,imod]
            print(d.dacs.vth2)
        elif ic==2:
            print("counter",ic)
            print(vth[ic])
            for imod in range(nmod):
                d.dacs.vth3[imod]=vth[ic,imod]
            print(d.dacs.vth3)
        
        
        
        nodata=1
        Vtrim= np.zeros(nmod, dtype = np.int)
        if verbose==1:
            outfname=str(d.fpath)+'/vtrimdisp_'+fn+'_TB63_c'+str(ic)+'_'+str(ind)+'.dat'

        #results = [pool.apply(find_target_threshold, args=(data_thr[ic,imod], minthr, maxthr, nph, ff, nsigma, outfname,)) for imod in range(nmod)]
        print("*** Vtrim scan counter",ic)
        data_vtrim[ic]= scan(d,rx,dac,  vtrimMin, vtrimMax,vtrimStep)
        
        #psc.plot_thrscan(np.concatenate(data_vtrim[ic],axis=1), vtrimMin, vtrimMax, vtrimStep)
        for imod in range(nmod):
            print("*** Finding Vtrim module",imod,"counter",ic)
            vtrim[ic,imod]=find_target_vtrim(data_vtrim[ic,imod], vtrimMin, vtrimMax, counts[ic,imod],chanmask[imod],3)
            print("MODULE",imod,"VTRIM",ic,"IS",vtrim[ic,imod])

    for imod in range(nmod):
        aa=np.where(vtrim[:,imod]>0)
        Vtrim[imod]=vtrim[0,imod] #np.mean(vtrim[aa,imod])
        print("MODULE",imod,"AVERAGE VTRIM","IS",Vtrim[imod])

    """
        
    for imod in range(nmod):
        Vtrim[imod]=600

    
    """

    ###########################################################
    # Trimbit scan  to find target trimbits
    ###########################################################

    for imod in range(nmod):
        d.dacs.vtrim[imod]=int(Vtrim[imod])

    tbMin=0
    tbMax=63
    tbStep=1

    dac=dacIndex.TRIMBIT_SCAN
    
    trims=np.arange(tbMin, tbMax+tbStep,tbStep)

    nrow = len(trims)
    trimbits= np.zeros((3*1280,nmod), dtype = np.int)
    data_trim = np.zeros((3,nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    outfname=None
    for ic in [0]: #counters:

        d.findex=ind
        d.fname=fn+'_TBscan_c'+str(ic)

        d.counters=[ic]

        ncol=1280

        d.dacs.vth1=2800
        d.dacs.vth2=2800
        d.dacs.vth3=2800
        
        if ic==0:
            for imod in range(nmod):
                d.dacs.vth1[imod]=vth[ic,imod]
        elif ic==1:
            for imod in range(nmod):
                d.dacs.vth2[imod]=vth[ic,imod]
        elif ic==2:
            for imod in range(nmod):
                d.dacs.vth3[imod]=vth[ic,imod]

        if verbose==1:
            outfname=str(d.fpath)+'/trimdisp_'+fn+'_TB63_c'+str(ic)+'_'+str(ind)+'.dat'
        print("*** Trimbit scan counter",ic)
        print("vtrim is ",d.dacs.vtrim)

        data_trim[ic]= scan(d,rx,dac, tbMin, tbMax, tbStep)

        #psc.plot_thrscan(np.concatenate(data_trim[ic],axis=1), tbMin, tbMax, tbStep)
        for imod in range(nmod):
            print("*** Finding trimbits module",imod,"counter",ic)
            trimbits[ic::3,imod]=find_trimbits(data_trim[ic,imod], counts[ic,imod], tbMin, tbMax)
            print("MODULE",imod,"MEAN TRIMBITS COUNTER",ic,"IS",np.median(trimbits[ic::3,imod]),"RMS",np.sqrt(np.var(trimbits[ic::3,imod])))
        

    for ic in range(1,3):
        for imod in range(nmod):
            trimbits[ic::3,imod]=trimbits[0::3,imod]
        
    print(Vtrim)
    return vth,Vtrim,trimbits
        

    ###########################################################
    # Test trimming
    ###########################################################

def test_trimming(d,rx,minthr, maxthr, thrstep, nph, chanmask, verbose=1):
    
    counters=d.counters
    nmod=len(d.hostname)
    fn=d.fname
    ind=d.findex

    d.rx_zmqstream=1
    d.rx_zmqfreq=1

###########################################################
# Threshold scan with trimbits=0 to find target threshold
###########################################################

    
    threshold=np.arange(minthr, maxthr+thrstep,thrstep)

    
    ncol=1280

    nrow = len(threshold)
    vth= np.zeros((len(counters),nmod), dtype = np.int)
    counts= np.zeros((3,nmod,ncol), dtype = np.int)
    data_thr = np.zeros((3,nmod,nrow,ncol), dtype =  to_dtype(d.dr))
    #ii=0
    outfname=None

    ff=1500
    for ic in [0]:#counters:
        d.findex=ind
        d.fname=fn+'_trimmed_c'+str(ic)
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
        if verbose==1:
            outfname=str(d.fpath)+'/thrdisp_'+fn+'_trimmed_c'+str(ic)+'_'+str(ind)+'.dat'
        data_thr[ic]= scan(d,rx,dac, minthr, maxthr, thrstep)
        """       
        flex,noise,ampl,cs,cc=fsc.fit_all(threshold,data_thr[ic])

        if outfname!=None:
            fsc.save_scurve_fit_file(outfname,flex,noise,ampl,cs,counts)
    print("THRESHOLD",ic,"MEAN",np.mean(flex[flex>0]),"RMS",np.sqrt(np.var(flex[flex>0]))," MEAN COUNTS",np.mean(cc))
        """

        """
        nsigma=0  
        pool = mp.Pool(processes=nmod)
        args=[]
        for imod in range(nmod):
            #if len(nph)==1:
            #    nph1=nph
            #else:
            #    nph1=nph[imod]
            arg=[]
            arg.append(data_thr[ic,imod])
            arg.append(minthr)
            arg.append(maxthr)
            arg.append(nph[imod])
            arg.append(ff) 
            arg.append(nsigma) 
            if verbose==1:
                outfname=str(d.fpath)+'/thrdisp_'+fn+'_trimmed_c'+str(ic)+'_d'+str(imod)+'_'+str(ind)+'.dat'
            arg.append(outfname)
            arg.append(chanmask[imod])
            args.append(arg)
        #pool = mp.Pool(processes=nmod)
        #results = [pool.apply(find_target_threshold, args=(data_thr[ic,imod], minthr, maxthr, nph, ff, nsigma, outfname,)) for imod in range(nmod)]
        print("*** Fitting counter",ic)
        results = pool.map(find_target_threshold_pool, args)
        #print(results)
        for imod in range(nmod):
            vth[ic,imod],counts[ic,imod]=results[imod]
            print ("MODULE",imod,"COUNTER",ic,"THRESHOLD",vth[ic,imod]);

        
    for ic in range(1,3):
        for imod in range(nmod):
            vth[ic,imod]= vth[0,imod]
            counts[ic,imod]=counts[0,imod]

        #for imod in range(nmod):
         #   vth[ic,imod],counts[ic,imod]=find_target_threshold(data_thr[ic,imod], minthr, maxthr, nph, ff, nsigma, outfname)
    """

    return data_thr,vth
        

        
        

def trim(ff, d,rx,minthr, maxthr, thrstep,nph, nsigma, chanmask, verbose=1):
    
    sn=d.getModuleId()
    #sn=d.getSerialNumber()
    print(sn)

    

    nmod=len(d.hostname)

    print("starting trimming", d.settings, minthr, maxthr, thrstep)
    start = time.time()
    vth,vtrim,trimbits=trim_f(d,rx,minthr, maxthr, thrstep,nph, chanmask, nsigma, verbose)

    end = time.time()
    d.counters=[0,1,2]
    print("*** AFTER TRIMMING ***")
    for imod in range(nmod):
        d.dacs.vth1[imod]=vth[0,imod]
        d.dacs.vth2[imod]=vth[1,imod]
        d.dacs.vth3[imod]=vth[2,imod]
        d.dacs.vtrim[imod]=vtrim[imod]
        print("MODULE", imod, "THRESHOLDS ARE",vth[:,imod])
        print("VTRIM IS",vtrim[imod])

    print('Trimming required:',end - start,'seconds')
    dacs= d.dacs.to_array()

    gain=d.getGainCaps()[0]

    #print("DACS BEFORE:",dacs)
    #print("TBs:",trimbits)
    for imod in range(nmod):
        fname=str(d.fpath)+'/'+ff+'_'+str(d.findex)+'.sn'+str(sn[imod]).zfill(4)
        my3.write_my3_trimbits_new(fname,np.int32(gain),np.int32(dacs[:,imod]),np.int32(trimbits[:,imod]))
        #my3.write_my3_trimbits(fname,np.int32(dacs[:,imod]),np.int32(trimbits[:,imod]))
        
        print('Wrote to trimbit file',fname)

    fname=str(d.fpath)+'/'+ff+'_'+str(d.findex)
    d.trimbits=fname

    tdata,vth=test_trimming(d,rx,minthr+100, maxthr+100, thrstep,nph,  chanmask, verbose)
 
    end = time.time()
    print('Including testing:',end - start,'seconds')



    d.counters=[0,1,2]
    """
    print("*** AFTER CALIBRATION ***")
    for imod in range(nmod):
        d.dacs.vth1[imod]=vth[0,imod]
        d.dacs.vth2[imod]=vth[1,imod]
        d.dacs.vth3[imod]=vth[2,imod]
        d.dacs.vtrim[imod]=vtrim[imod]
        print("MODULE",imod,"THRESHOLDS ARE",vth[:,imod])
        print("VTRIM IS",vtrim[imod])

        dacs= d.dacs.to_array()

        #a=d.getSerialNumber()
        gain=d.getGainCaps()

        #for imod in range(nmod):
        fname=str(d.fpath)+'/'+ff+'_recal_'+str(d.findex)+'.sn'+str(sn[imod]).zfill(4)
        my3.write_my3_trimbits_new(fname,np.int32(gain),np.int32(dacs[:,imod]),np.int32(trimbits[:,imod]))
        print('Wrote to trimbit file',fname)
        
    """
    fname=str(d.fpath)+'/'+ff+'_'+str(d.findex)
    d.trimbits=fname

    for ic in range(1):#range(0,3):
        data=tdata[ic]
        sstep=(maxthr-minthr)/(data.shape[1]-1)
        #print(data.shape,np.concatenate(data,axis=1).shape,np.arange(minthr,maxthr+sstep,sstep).shape )
        psc.plot_thrscan(np.concatenate(data,axis=1), minthr+100, maxthr+100, sstep)


    fig, ax = plt.subplots()
    ax.plot(np.concatenate(trimbits))
    fig.show()

    fig1, ax1 = plt.subplots()
    for imod in range(nmod):
        for ic in range(3):
            ax1.hist(trimbits[ic::3,imod], bins=64,range=(0,64))
    fig1.show()

                
    return vth,vtrim,trimbits

        
