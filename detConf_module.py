#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Oct 04 2019

@author: Marie Andrä
DETECTOR CONFIGURATION FILE FOR MYTHEN 3.0 MODULE
"""
import sys

#sys.path.append('/afs/.psi.ch/project/sls_det_software/andrae/pythonScripts/includeBasics/')

from pattern import *
import numpy as np

print("IMPORTING DETECTOR CONFIGURATION FILE FOR MYTHEN 3.0 MODULE")


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
CSR_dpulse = 5


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
    p.SB(resStorage);
    p.REPEAT(10)
    p.CB(resStorage);
    p.REPEAT(10)
    p.SB(STO);
    p.REPEAT(10); #store counters in output registers
    p.CB(STO);
    p.REPEAT(10); #store counters in output registers

def _digitalPulsingPattern(n1,n2,n3):
    p=pat()

    csr=0 #content of chip status register #n (18 bits)
    print(csr)
    csr=csr|(1<<CSR_dpulse)
    #csr=p.setbit(CSR_dpulse,csr)    # enable pulsing of the counter
    print(csr)
    setChipStatusRegister(p,csr)
    resetChip(p)#RESET CHIP
    
    #DIGITAL PULSING SEQUENCE
    n=np.array([n1,n2,n3])
    nl=np.array([n1,n2,n3])
    for i in range(len(n)):
        mask= (n>0)
        nl[i]=min(n[n>0])
        print(i,"*",n,"*",nl[i])
        n=n-nl[i]
        
    nn=0
    for i in range(len(n)):
        if nl[i]>0:
            p.setnloop(i,nl[i]); #number of pulses 
            p.setstartloop(i);
            if n[0]-nn>0:
                p.SB(EN1);# select here which counters have to be pulsed 
            if n[1]-nn>0:
                p.SB(EN2);
            if n[2]-nn>0:
                p.SB(EN3);
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
    p.patInfo()
    return p

def digitalPulsingPattern(*args):
    if len(args) == 1:
        return _digitalPulsingPattern(args[0], args[0], args[0])
    elif len(args) == 3:
        return _digitalPulsingPattern(*args)
    else: 
        raise ValueError('func called with wrong number of args')

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
    p.CLOCKS(clk,24);
    p.CB(dbit_ena);
    p.PW();
    print(p.LineN)

    p.patInfo()
    return p










##########################################################################################
def testSerialIn(d,val):
    pp=testSerialInPattern(val)
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
            print("serout",i,"read",serout[i],"instead of",val)
            errorMask|=(1<<i)

    return errorMask
