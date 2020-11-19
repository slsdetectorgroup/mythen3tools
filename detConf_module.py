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

print("IMPORTING DETECTOR CONFIGURATION FILE FOR MYTHEN 3.0 MODULE")

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

PSNames=['VddA','VddPre','VC','VD','VddD','VCHIP']

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

def digitalPulsingPattern(n1,n2,n3):
    p=pattern()

    csr=0#content of chip status register #n (18 bits)
    csr=p.SBREG(5,csr);# enable pulsing of the counter
    setChipStatusRegister(p,csr)
    resetChip()#RESET CHIP
    
    #DIGITAL PULSING SEQUENCE
    nn=min(n1,n2,n3)
    mm=max(min(n1-nn,n2-nn,n3-nn),0)
    mm=max(min(n1-nn,n2-nn,n3-nn),0)
    ll=max(min(n1-nn-mm,n2-nn-mm,n3-nn-mm),0)
    setnloop(0,nn); #number of pulses 
    setstartloop(0);
    if n1>0:
        p.SB(EN1);# select here which counters have to be pulsed 
    if n2>0:
        p.SB(EN2);
    if n3>0:
        p.SB(EN3);
    p.REPEAT(5)
    p.CB(EN1);
    p.CB(EN2);
    p.CB(EN3);
    p.REPEAT(5)
    setstoploop(0);
    p.REPEAT(2)
    setnloop(1,nn); #number of pulses s
    if mm>0:
        setstartloop(1);
        if n1-nn>0:
            p.SB(EN1);# select here which counters have to be pulsed 
        if n2-nn>0:
            p.SB(EN2);
        if n3-nn>0:
            p.SB(EN3);       
        p.REPEAT(5)
        p.CB(EN1);
        p.CB(EN2);
        p.CB(EN3);
        p.REPEAT(5)
        setstoploop(1);
        p.REPEAT(2)
    if ll>0:
        p.setnloop(2,ll); #number of pulses s
        p.setstartloop(1);
        if n1-nn-mm>0:
            p.SB(EN1);# select here which counters have to be pulsed 
        if n2-nn-mm>0:
            p.SB(EN2);
        if n3-nn-mm>0:
            p.SB(EN3);
        p.REPEAT(5)
        p.CB(EN1);
        p.CB(EN2);
        p.CB(EN3);
        p.REPEAT(5)
        p.setstoploop(2);
        p.REPEAT(2)
    p.REPEAT(5)
    storeCounters(p)
    patInfo()
    return p

def digitalPulsingPattern(n1):
    return digitalPulsingPattern(n1,n1,n1)


