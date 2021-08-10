#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Oct 04 2019

@author: Marie Andrä
DETECTOR CONFIGURATION FILE FOR MYTHEN 3.0 MODULE
"""
import sys
import time
#sys.path.append('/afs/.psi.ch/project/sls_det_software/andrae/pythonScripts/includeBasics/')

from patterntools import pat
import numpy as np
from patterntools.zmqreceiver import to_dtype,ZmqReceiver
import slsdet



#print("IMPORTING DETECTOR CONFIGURATION FILE FOR MYTHEN 3.0 MODULE")


NCHIPS=10
NSEROUT=4

dacNames=[
 'vcassh',
 'vth2',
 'vrfsh',
 'vrfshnpol',
 'vipreout',
 'vth3',
 'vth1',
 'vicin',
 'vcas',
 'vpreamp',
 'vph',
 'vipre',
 'viinsh',
 'vpl',
 'vtrim',
 'vdcsh'
]

sigNames=[
'SerialOut1_1', 'SerialOut2_1', 'SerialOut3_1', 'SerialOut4_1',
'SerialOut1_2', 'SerialOut2_2', 'SerialOut3_2', 'SerialOut4_2',
'SerialOut1_3', 'SerialOut2_3', 'SerialOut3_3', 'SerialOut4_3',
'SerialOut1_4', 'SerialOut2_4', 'SerialOut3_4', 'SerialOut4_4',
'SerialOut1_5', 'SerialOut2_5', 'SerialOut3_5', 'SerialOut4_5',
'SerialOut1_6', 'SerialOut2_6', 'SerialOut3_6', 'SerialOut4_6',
'SerialOut1_7', 'SerialOut2_7', 'SerialOut3_7', 'SerialOut4_7',
'SerialOut1_8', 'SerialOut2_8', 'SerialOut3_8', 'SerialOut4_8',
'SerialOut1_9', 'SerialOut2_9', 'SerialOut3_9', 'SerialOut4_9',
'SerialOut1_10', 'SerialOut2_10', 'SerialOut3_10', 'SerialOut4_10',
'CHSerialOut31_1', 'CHSerialOut31_2', 'CHSerialOut31_3', 'CHSerialOut31_4', 'CHSerialOut31_5', 'CHSerialOut31_6', 'CHSerialOut31_7', 'CHSerialOut31_8', 'CHSerialOut31_9', 'CHSerialOut31_10',
'WordOut_1', 'WordOut_2', 'WordOut_3', 'WordOut_4', 'WordOut_5', 'WordOut_6', 'WordOut_7', 'WordOut_8', 'WordOut_9', 'WordOut_10', 
'ClkOut_1', 'ClkOut_2', 'ClkOut_3', 'ClkOut_4', 'ClkOut_5', 'ClkOut_6', 'ClkOut_7', 'ClkOut_8', 'ClkOut_9', 'ClkOut_10', 
'TBLoad_1', 'TBLoad_2', 'TBLoad_3', 'TBLoad_4', 'TBLoad_5', 'TBLoad_6', 'TBLoad_7', 'TBLoad_8', 'TBLoad_9', 'TBLoad_10',
'AnaMode',
'CHSserialIN',
'Readout',
'Pulse',
'EN1',
'EN2',
'EN3',
'clk',
'SRmode',
'SerialIN',
'Sto',
'StatLoad',
'ResStorage',
'ResCounter',
'CHSclk', 'exposing','dbit_ena'
]

#PSNames=['VddA','VddPre','VC','VD','VddD','VCHIP']

#chip IOs

TBLoad_1 = 0
TBLoad_2 = 1
TBLoad_3 = 2
TBLoad_4 = 3
TBLoad_5 = 4
TBLoad_6 = 5
TBLoad_7 = 6
TBLoad_8 = 7
TBLoad_9 = 8
TBLoad_10 = 9

AnaMode = 10
CHSserialIN = 11
READOUT = 12
pulse = 13
EN1 = 14
EN2 = 15
EN3 = 16
clk = 17
SRmode = 18
serialIN = 19
STO = 20
STATLOAD = 21
resStorage = 22
resCounter = 23
CHSclk = 24
exposing = 25
dbit_ena = 32
 
#CHIP STARTUS REGISTER BITS
CSR_spypads = 0
CSR_invpol = 4
CSR_dpulse = 5
CSR_interp = 6
CSR_C10pre = 7 #default
CSR_pumprobe = 8
CSR_apulse = 9
CSR_C15sh = 10 
CSR_C30sh = 11 #default
CSR_C50sh = 12
CSR_C225ACsh = 13 # Connects 225fF SHAPER AC cap (1: 225 to shaper, 225 to GND. 0: 450 to shaper) 
CSR_C15pre = 14 

CSR_default = (1<<CSR_C10pre ) | (1<< CSR_C30sh)



#SIGNAL ANALYZER REGISTERS
SA_NW0_REG=0x520
SA_NW1_REG=0x560
SA_DATA0_REG=0x510
SA_DATA1_REG=0x550
#BIT ORDER
saBits=['SerOut0','SerOut1','SerOut2','SerOut3','WordOut','CHSerOut']


def ALLCLK(pat,times):
    for i in range(0,times):
        pat.SB(CHSclk); pat.SB(clk); pat.REPEAT(4)
        pat.CB(CHSclk); pat.CB(clk); pat.REPEAT(4)

def PUSH1CHS(pat):
    #print("CHSserialIN",CHSserialIN)
    #print("CHSclk",CHSclk)
    pat.SB(CHSserialIN)
    pat.REPEAT(5);
    pat.SB(CHSclk)
    pat.REPEAT(5);
    pat.CB(CHSclk);
    pat.REPEAT(5); 
    pat.CB(CHSserialIN);
    pat.REPEAT(5); 

def PUSH1CSR(pat): 
    pat.SB(serialIN);
    pat.REPEAT(5);
    pat.SB(CHSclk);
    pat.REPEAT(5);
    pat.CB(CHSclk); 
    pat.PW();
    pat.CB(serialIN);
    pat.REPEAT(5);

def PUSH0CSR(pat):
    pat.CB(serialIN);
    pat.REPEAT(5);
    pat.SB(CHSclk);
    pat.REPEAT(5);
    pat.CB(CHSclk);
    pat.REPEAT(5); 

def SELSTRIP(pat,x):
    #print("Selecting Strip:",x)
    PUSH1CHS(pat); 
    pat.CLOCKS(CHSclk,2+3*x) #strip numbering starts form 0


def SELALLSTRIPS(pat, x=31):
    pat.SB(CHSserialIN);
    pat.CLOCKS(CHSclk,3+3*x) #strip numbering starts form 0
    pat.CB(CHSserialIN);
    pat.PW()



def CLEAR_TBs(pat):
    pat.CB(TBLoad_1);
    pat.CB(TBLoad_2);
    pat.CB(TBLoad_3);
    pat.CB(TBLoad_4);
    pat.CB(TBLoad_5);
    pat.CB(TBLoad_6);
    pat.CB(TBLoad_7);
    pat.CB(TBLoad_8);
    pat.CB(TBLoad_9);
    pat.CB(TBLoad_10);
    pat.PW;

def SET_TBs(pat):
    pat.SB(TBLoad_1);
    pat.SB(TBLoad_2);
    pat.SB(TBLoad_3);
    pat.SB(TBLoad_4);
    pat.SB(TBLoad_5);
    pat.SB(TBLoad_6);
    pat.SB(TBLoad_7);
    pat.SB(TBLoad_8);
    pat.SB(TBLoad_9);
    pat.SB(TBLoad_10);
    pat.PW;

def SET_TB(pat, i):
    
    pat.CB(TBLoad_1);
    pat.CB(TBLoad_2);
    pat.CB(TBLoad_3);
    pat.CB(TBLoad_4);
    pat.CB(TBLoad_5);
    pat.CB(TBLoad_6);
    pat.CB(TBLoad_7);
    pat.CB(TBLoad_8);
    pat.CB(TBLoad_9);
    pat.CB(TBLoad_10);    
    if i==0:
        pat.SB(TBLoad_1);
    if i==1:
        pat.SB(TBLoad_2);
    if i==2:
        pat.SB(TBLoad_3);
    if i==3:
        pat.SB(TBLoad_4);
    if i==4:
        pat.SB(TBLoad_5);
    if i==5:
        pat.SB(TBLoad_6);
    if i==6:
        pat.SB(TBLoad_7);
    if i==7:
        pat.SB(TBLoad_8);
    if i==8:
        pat.SB(TBLoad_9);
    if i==9:
        pat.SB(TBLoad_10);
    pat.PW;

def setChipStatusRegister(p,csr):
    nbits=18
    p.SB(STATLOAD);
    p.REPEAT(2); #chip goes in state load mode. If bit<17> was left loaded, you immediately see a one on CHSerialOut<31>
    p.SB(resStorage); #reset status register
    p.SB(resCounter); #reset input shift register
    p.REPEAT(8);
    p.CB(resStorage);
    p.CB(resCounter);
    p.REPEAT(8);
    #This version of the serializer pushes in the MSB first (compatible with the CSR bit numbering)
    for i in range(nbits-1, -1,-1):
        if csr&(1<<i):
            p.SB(serialIN);
        else:
            p.CB(serialIN);
        p.REPEAT(4);
        p.CLOCK(CHSclk);
    p.CB(serialIN);
    p.REPEAT(2)      
    p.SB(STO);
    p.REPEAT(5)
    p.CB(STO);
    p.REPEAT(5)
    #This STORES the content of the input shift register in the actual chip status register
    p.CB(STATLOAD) #Exit state load mode
    p.REPEAT(5)
        

def resetChip(p):
    p.CB(STATLOAD) #Exit state load mode
    p.REPEAT(5)
    p.REPEAT(2); #chip goes in state load mode. If bit<17> was left loaded, you immediately see a one on CHSerialOut<31>
    p.SB(resStorage); #reset status register
    p.SB(resCounter); #reset input shift register
    p.REPEAT(8);
    p.CB(resStorage);
    p.CB(resCounter);
    p.REPEAT(8);

def storeCounters(p):
    p.SB(resStorage); #clear output registers
    p.REPEAT(10)
    p.CB(resStorage);
    p.REPEAT(10)
    p.SB(STO);
    p.REPEAT(10); #store counters in output registers
    p.CB(STO);
    p.REPEAT(10); 

def digitalPulsingPattern(*args):
    #if len(args) == 1:
    if np.array(args).shape[1] == 1:
        #print("1arg",np.array(args).shape)
        n1=args[0][0] 
        n2=args[0][0]
        n3=args[0][0]
    #elif len(args) == 3:
    if np.array(args).shape[1] == 3:
        #print("3args",np.array(args).shape)
        n1=args[0][0]
        n2=args[0][1] 
        n3=args[0][2]
    else: 
        raise ValueError('func called with wrong number of args')
#def _digitalPulsingPattern(n1,n2,n3):
    p=pat()
    resetChip(p)#RESET CHIP
    csr=0 #content of chip status register #n (18 bits)
    csr=csr|(1<<CSR_dpulse)
    #csr=p.setbit(CSR_dpulse,csr)    # enable pulsing of the counter
    #print(csr)
    setChipStatusRegister(p,csr)
    
    #DIGITAL PULSING SEQUENCE
    n=np.array([n1,n2,n3])
    n1=np.array([n1,n2,n3])
    
    nl=np.array([n1,n2,n3])
    for i in range(len(n)):
        mask= (n>0)
        if n[n>0].size>0:
            nl[i]=min(n[n>0])
        else:
            nl[i]=0
        #print(i,"*",n,"*",nl[i])
        n=n-nl[i]
    n=n1    
    nn=0
    for i in range(len(n)):
        if nl[i]>0:
            p.setnloop(i,nl[i]); #number of pulses 
            p.setstartloop(i);
            #print(n,nn)
            if n[0]-nn>0:
                p.SB(EN1);# select here which counters have to be pulsed 
                #print(i,'en1')
            if n[1]-nn>0:
                p.SB(EN2);
                #print(i,'en2')
            if n[2]-nn>0:
                p.SB(EN3);
                #print(i,'en3')
            p.REPEAT(5)
            p.CB(EN1);
            p.CB(EN2);
            p.CB(EN3);
            p.REPEAT(5)
            p.setstoploop(i);
            p.REPEAT(2)
            nn+=nl[i]
    p.REPEAT(5)
    storeCounters(p)
    #.patInfo()
    return p

def analogPulsingPattern(*args):
    if len(args) == 1:
    #if np.array(args).shape[1] == 1:
        #print("1arg",np.array(args).shape)
        n1=args[0]
        n2=args[0]
        n3=args[0]
    elif len(args) == 3:
    #if np.array(args).shape[1] == 3:
        #print("3args",np.array(args).shape)
        n1=args[0]
        n2=args[1] 
        n3=args[2]
    else: 
        raise ValueError('func called with wrong number of args')
#def _digitalPulsingPattern(n1,n2,n3):
    p=pat()
    resetChip(p)#RESET CHIP
    csr= CSR_default #content of chip status register #n (18 bits)
    csr=csr|(1<<CSR_apulse)
    #csr=p.setbit(CSR_dpulse,csr)    # enable pulsing of the counter
    #print(csr)
    setChipStatusRegister(p,csr)
    
    #SELALLSTRIPS(p,31)
    if n3!=n2:
        if n2>0:
            n3=n2
            #print("forced pulses on counter3=pulses on counter2")

    #DIGITAL PULSING SEQUENCE
    n=np.array([n1,n2,n3])
    n1=np.array([n1,n2,n3])
    
    nl=np.array([n1,n2,n3])
    for i in range(len(n)):
        mask= (n>0)
        if n[n>0].size>0:
            nl[i]=min(n[n>0])
        else:
            nl[i]=0
        #print(i,"*",n,"*",nl[i])
        n=n-nl[i]
    n=n1    
    nn=0    

    PUSH1CHS(p);
    p.CLOCKS(CHSclk,2) #strip numbering starts form 0
    p.PW();
    p.setnloop(2,32); #number of pulses 
    p.setstartloop(2);
    p.PW();

    for i in range(len(n)-1):
        if nl[i]>0:
            #print(n,nn)
            p.setnloop(i,nl[i]); #number of pulses 
            p.setstartloop(i);
            if n[0]-nn>0:
                p.SB(EN1);# select here which counters have to be pulsed 
                #print(i,'en1')
            else:
                 p.CB(EN1);
            if n[1]-nn>0:
                p.SB(EN2);
                #print(i,'en2')
            else:
                p.CB(EN2);
            if n[2]-nn>0:
                p.SB(EN3);
                #print(i,'en3')
            else:
                p.CB(EN3);
            p.REPEAT(5)
            p.SB(pulse)
            p.PW()
            p.setwaittime(1,3000); #wait time - can be changed dynamically
            p.setwaitpoint(1); #set wait points
            p.PW()
            p.CB(EN1);
            p.CB(EN2);
            p.CB(EN3);
            p.REPEAT(5)
            p.CB(pulse)
            p.PW()
            p.setwaittime(2,1000); #wait time - can be changed dynamically
            p.setwaitpoint(2); #set wait points
            p.REPEAT(2)
            p.setstoploop(i);
            p.REPEAT(2)
            nn+=nl[i]


    p.CLOCKS(CHSclk,3) #strip numbering starts form 0
    p.PW()
    p.setstoploop(2)

    p.REPEAT(5)
    storeCounters(p)
    #.patInfo()
    return p

def exposePattern():
    #if len(args) == 1:
   
    p=pat()
    resetChip(p)#RESET CHIP
    csr= CSR_default #content of chip status register #n (18 bits)
    #csr=csr|(1<<CSR_apulse)
    #csr=p.setbit(CSR_dpulse,csr)    # enable pulsing of the counter
    #print(hex(csr))
    setChipStatusRegister(p,csr)
    
    resetChip(p)#RESET CHIP

    p.SB(EN1);
    p.SB(EN2);
    p.SB(EN3);
    p.REPEAT(5)
    p.setwaittime(1,300); #wait time - can be changed dynamically
    p.setwaitpoint(1); #set wait points
    p.PW()
    p.CB(EN1);
    p.CB(EN2);
    p.CB(EN3);
    p.REPEAT(5)
    storeCounters(p)
    #.patInfo()
    return p

def testSerialInPattern(val):
    p=pat()
    resetChip(p)#RESET CHIP
    p.SB(SRmode);
    p.REPEAT(4)
    p.CB(serialIN);
    p.PW();
    p.CLOCKS(clk,24);
    
    p.PW();
    for i in range(24):
        if val&(1<<i): # bitwise & -> if bit_c[i]==1: push 1
            p.SB(serialIN);
        else:
            p.CB(serialIN);
        p.PW()
        p.CLOCKS(clk,1)
        
    p.SB(dbit_ena);
    p.setnloop(0,24);
    p.setstartloop(0);
    p.SB(clk)
    p.PW()
    p.CB(clk)
    #p.PW()
    #p.CLOCK(clk);
    p.setstoploop(0);
    p.PW()
    p.CB(dbit_ena);
    p.PW();

    #.patInfo()
    return p


def readoutPattern():
    p=pat()
    p=appendReadoutPattern(p)
    return p



def appendReadoutPattern(p):
    p.SB(READOUT);
    #SB(SRmode);
    p.REPEAT(2)
    #selects first ch., first comp.
    PUSH1CHS(p)
    p.CLOCKS(clk,4);#starts the digital machinery, filling pipelines
    #p.PW() #->We have to execute SB(dbit_ena,1) on an ODD address to be active from the next word on
    p.SB(dbit_ena);
    #p.PW();#SWITCHES ON DATA TAKING and moves to even address
    #READOUT SEQUENCE
    p.setnloop(2,96);
    p.setstartloop(2);
    p.CB(SRmode);
    p.SB(clk);
    p.PW();
    p.CB(clk);
    p.PW();
    p.SB(SRmode);
    p.SB(clk);
    p.PW();
    p.CB(clk);
    p.PW();
    #Now that we have saved the content of the counter
    #we can already move to the next with CHSclk
    p.SB(clk);
    p.SB(CHSclk);
    p.PW();
    p.CB(clk);
    p.PW();
    p.SB(clk);
    p.CB(CHSclk);
    p.PW();
    p.CB(clk);
    p.PW();
    p.CLOCKS(clk,19);
    #The last clock cycle has to be written explicitly 
    #To properly place the setstoploop
    ###p.patInfo()
    p.SB(clk);
    p.PW();
    p.setstoploop(2);
    p.CB(clk);
    p.PW();
    p.CLOCKS(clk,3);#4 clks to push out pipeline
    p.SB(clk)
    p.PW()
    p.CB(clk)
    p.CB(dbit_ena);
    p.PW();
    #print(p.LineN)
    #p.patInfo()
    return p







##########################################################################################
def testSerialIn(d,val):
    pp=testSerialInPattern(val)

    v0=d.clkdiv[0]
    v2=d.clkdiv[2]

    d.clkdiv[0]=40
    d.clkdiv[2]=40
    pp.load(d)
    d.startPattern()

    #print("counters:",d.readRegister(SA_NW0_REG),  d.readRegister(SA_NW0_REG))
    nw=np.array([d.readRegister(SA_NW0_REG)[0],d.readRegister(SA_NW0_REG)[0]])
    
    serout=np.zeros((NCHIPS*NSEROUT),dtype=np.int64)
    ishift=0
    if nw[0]!=nw[1]:
        print("READOUT ERROR! Different number of words in the two fifos!")
    else:
        for i in range(nw[0]):
            v=np.int64(d.readRegister(SA_DATA0_REG)[0]) | (np.int64(d.readRegister(SA_DATA1_REG)[0])<<32)
            if i%2==0:
                #print(bin(v))
                for ichip in range(NCHIPS):
                    for ibit in range(NSEROUT):
                        #print(ichip,ibit,ishift)
                        mask=v >> (ichip*len(saBits)+ibit)
                        serout[ichip*NSEROUT+ibit] |= (mask & 0x1) << ishift
                ishift+=1
                        #print("counters:",d.readRegister(0x520),  d.readRegister(0x560))
    errorMask=0
    for i in range(NCHIPS*NSEROUT):
        if serout[i]!=val:
            print("serout",i,"read", hexFormat(serout[i],8),"instead of",hexFormat(val,8))
            errorMask|=(1<<i)

    d.clkdiv[0]=v0
    d.clkdiv[2]=v2
    return errorMask
    


def testDigitalPulsing(d, rx, n, verbose=0):  
    #print(len(n))
    if len(n) == 1:
        npu=[n,n,n]
    elif len(n) == 3:
        npu=n
    
    nodata=1
    while nodata>0:
        pp=digitalPulsingPattern(npu)
        pp.load(d)
        d.startPattern()
        time.sleep(0.1)
        d.startReceiver()
        d.readout()
        d.stopReceiver()
    
        for i in range(d.rx_framescaught+1):
            dd, header = rx.receive_one_frame()
            if dd is None:
                break
            data=dd
            nodata=0
        #print(header)
    errorMask=0
    chipMask=0
    nch=np.int(len(data)/3)
    for ich in range(nch):
        for ic in range(3):
            if data[ich*3+ic]!=npu[ic]:
                if verbose>0:
                    print("Channel",ich,"Counter",ic,"read",hex(data[ich*3+ic]),"instead of",hex(npu[ic]));
                errorMask+=1
                ichip=np.int(ich/128)
                chipMask|=(1<<ichip)
    return errorMask,chipMask


def analogPulsingScan(d, rx,  npu, threshold):  
    counters=d.counters
    ncol=1280*len(counters)
    nrow = len(threshold)
    npu0=0
    npu1=0
    npu2=0
    
    if 0 in counters:
        npu0=npu
    if 1 in counters:
        npu1=npu
    if 2 in counters:
        npu2=npu
        
    pp=analogPulsingPattern(npu0,npu1,npu2)
    pp.load(d)
    data = np.zeros((nrow,ncol), dtype =  to_dtype(d.dr))
    d.startReceiver()
    for i,th in enumerate(threshold):
        if 0 in counters:
            d.dacs.vth1=th
        if 1 in counters:
            d.dacs.vth2=th
        if 2 in counters:
            d.dacs.vth3=th
        d.startPattern()
        d.readout()
    d.stopReceiver()
    for i in range(d.rx_framescaught+1):
        dd, header = rx.receive_one_frame()
        if dd is None:
            break
        if header["frameIndex"]<len(threshold):
            data[header["frameIndex"]]=dd
        print(i,th,"ok")
    #rx.receive_stop_packet()
    #rx.receive_one_frame()
    return data
"""
CSR_spypads = 0
CSR_invpol = 4
CSR_dpulse = 5
CSR_interp = 6
CSR_C10pre = 7 #default
CSR_pumprobe = 8
CSR_apulse = 9
CSR_C15sh = 10 
CSR_C30sh = 11 #default
CSR_C50sh = 12
CSR_C225ACsh = 13 # Connects 225fF SHAPER AC cap (1: 225 to shaper, 225 to GND. 0: 450 to shaper) 
CSR_C15pre = 14 

CSR_default = (1<<CSR_C10pre ) | (1<< CSR_C30sh)
"""

def setDefaultMode(d):
    p=pat()
    setChipStatusRegister(p,CSR_default)
    p.load(d)
    d.startPattern()

def setSuperHighGainMode(d):
    p=pat()
    setChipStatusRegister(p,0)#CSR_C225ACsh
    p.load(d)
    d.startPattern()


def setHighestGainMode(d):
    p=pat()
    setChipStatusRegister(p,(1<<CSR_C10pre ) | (1<< CSR_C15sh) )
    p.load(d)
    d.startPattern()

def setLowestGainMode(d):
    p=pat()
    setChipStatusRegister(p,(1<<CSR_C10pre ) | (1<< CSR_C15pre) |(1<<CSR_C15sh )|(1<<CSR_C30sh )| (1<< CSR_C50sh) |  (1<< CSR_C225ACsh) )#CSR_C225ACsh
    p.load(d)
    d.startPattern()

def setPumpProbeMode(d):
    p=pat()
    setChipStatusRegister(p,CSR_default| (1<<CSR_pumprobe))
    p.load(d)
    d.startPattern()
    
def setInterpolationMode(d):
    p=pat()
    setChipStatusRegister(p,CSR_default| (1<<CSR_interp))
    p.load(d)
    d.startPattern()
    

def changeClkdDiv(d,val,off=0):
    d.clkdiv[0]=val
    d.clkdiv[1]=val
    d.clkdiv[2]=val
    d.writeRegister(0x110,off)


def gain_bits_to_string(val1):
    val= val1 ^((1 << CSR_C10pre) | (1 << CSR_C15pre))
    #print(hex(val),hex(val1))
    gains = [g for g in slsdet.M3_GainCaps.__members__ if int(getattr(slsdet.M3_GainCaps, g)) & val]
    if len(gains)==0:
        return "M3_C0"
    return '_'.join([g for g in gains])


#print(bits_to_string(d.getChipStatusRegister()[0]))
def index_to_gain(ind):
    r=2
    gains=slsdet.M3_GainCaps.__members__
    gg=[0]
    for n in range(len(gains)):
        for i in gg:
            gsh1=[]
            for j in gains:
                gsh1.append(i | int(getattr(slsdet.M3_GainCaps, j)))
                gg=gg+gsh1
            gg=list( dict.fromkeys(gg) ) 
    return gg[ind]

#print("DETCONFMODULE LOADED")
