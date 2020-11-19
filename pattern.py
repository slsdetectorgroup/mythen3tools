class loop:
#this is a "local style" class
    def __init__(self, start=0x400, stop=0x400, n=0):
        self.start = start
        self.stop = stop
        self.n = n


class wait:
    def __init__(self, addr=0x400, wtime=0):
        self.addr = addr
        self.wtime = wtime
    
class pat:
#this is a "local style" class
    def __init__(self,Nbits=64):
        self.start=0
        self.end=0
        self.Nbits=self.Nbits
        self.Val=0 
        self.maskNbits=pow(2,Nbits)-1
        self.LineN=0
        self.addrs=[]
        self.words=[]
        self.loops=[loop(),loop(),loop()]
        self.waits=[wait(),wait(),wait()]


    ####FORMATTING FUNCTIONS########################################
    def hexFormat_nox(val,fill):
        v=hex(val)  #hexadecimal value
        v=(v.lstrip('-0x')).rstrip('L')  #remove leading 0x and - if there and trailing L
        v=v.zfill(fill) #inserts zeros at the beginning
        return v

    def hexFormat(val,fill):
        v=hex(val)  #hexadecimal value
        v=(v.lstrip('-0x')).rstrip('L')  #remove leading 0x and - if there and trailing L
        v=v.zfill(fill) #inserts zeros at the beginning
        v='0x'+v #puts back 0x
        return v

    def binFormat_nob(val,fill):
        v=bin(val)  #binary value
        v=(v.lstrip('-0b')).rstrip('L')   #remove leading 0x and - if there and trailing L
        v=v.zfill(fill) #inserts zeros at the beginning
        return v

    def binFormat(val,fill):
        v=bin(val)  #binary value
        v=(v.lstrip('-0b')).rstrip('L')   #remove leading 0x and - if there and trailing L
        v=v.zfill(fill) #inserts zeros at the beginning
        v='0b'+v #puts back 0b
        return v

    def decFormat(val,fill):
        v=str(val)  #decimal value
        v=v.zfill(fill) #inserts zeros at the beginning
        return v
    ################################################################
  
    ################################################################
    ##PAERN CONTROL FUNCTIONS##

    def setbit(bit,word):
        maskBit=1<<bit
        word=word|maskBit
        return(word)

    #THIS FUNCTION IS REDUNDANT, you can use setbit instead
    def SBREG(x,reg):
        #print(reg)
        reg=reg|(1<<x)
        print("Setting register to:"+str(reg))
        return reg

    def clearbit(bit,word):
        maskBit=1<<bit
        maskBitN=self.maskNbits-maskBit
        word=word&maskBitN
        return(word)
        
    def SB(bit,prN=0):
        self.Val=setbit(bit,self.Val)
        if prN:
            print("SB executed at line:",self.LineN)    
        return self.Val
 
    def CB(bit,prN=0):
        self.Val=clearbit(bit,self.Val)
        if prN:
            print("CB executed at line:",self.LineN,"on bit:",bit)
        return self.Val

    def CBs(*args):
        for i in args:
            self.Val=clearbit(i,self.Val)
        return self.Val

    def SBs(*args):
        for i in args:
            self.Val=setbit(i,self.Val)
        return self.Val

    def pw(verbose=0):
        address=self.LineN
        value=self.Val
        w=self.words
        a=self.addrs
        a.append(address)
        w.append(value)
        self.LineN+=1
        if verbose==1:
            print(hexFormat(address,4)+' '+hexFormat(value,16))

    def PW(verbose=0):
        pw(verbose)

    def PW2(verbose=0):
        pw(verbose)
        pw(verbose)


    def REPEAT(x):
        for i in range(x):
            pw()

    def CLOCKS(bit,times):
        for i in range(0,times):
            SB(bit);pw()
            CB(bit);pw()

    #NOT DEBUGGED!!!
    def serializer(value,serInBit,clkBit,nbits,msbfirst=1):
        """serializer(value,serInBit,clkBit,nbits,msbfirst=1)
        Produces the .pat file needed to serialize a word into a shift register.
        value: value to be serialized
        serInBit: control bit corresponding to serial in 
        clkBit: control bit corresponding to the clock 
        nbits: number of bits of the target register to load
        msbfirst: if 1 pushes in the MSB first (default), 
        if 0 pushes in the LSB first
        It produces no output because it modifies directly the members of the class pat via SB and CB"""
        c=value
        CBs(serInBit,clkBit)
        pw() #generate intial line with clk and serIn to 0
        start=0;stop=nbits;step=1
        if msbfirst:
            start=nbits-1;stop=-1;step=-1 #reverts loop if msb has to be pushed in first
            for i in range(start,stop,step):
                if c & (1<<i): 
                    SB(serInBit)
                    pw()
                else:
                    CB(serInBit)
                    pw()
                SB(clkBit)
                pw()
                CB(clkBit)
                pw() 
            CBs(serInBit,clkBit)
            pw() #generate final line with clk and serIn to 0     
            #NOT IMPLEMENTED YET
            #def setstop():    
            #
            #def setoutput(bit):
            #    self.ioctrl=setbit(bit,self.ioctrl)
            #
            #def setinput(bit):
            #    self.ioctrl=clearbit(bit,self.ioctrl)
        #
        #def setclk(bit):
        #    self.clkctrl=setbit(bit,self.clkctrl)

    def setinputs(*args):
        for i in args:
            setinput(i)

    def setoutputs(*args):
        for i in args:
            setoutput(i)
        
    def setclks(*args):
        for i in args:
            setclk(i)

    def setnloop(l,reps):
        self.loops[l].n=reps

    def setstartloop(l):
        self.loops[l].start=self.LineN

    def setstartloopbyaddr(l,addr):
        self.loops[l].start=addr
    
    def setstoploop(l):
        self.loops[l].stop=self.LineN
    
    def setstoploopbyaddr(l,addr):
        self.loops[l].stop=addr

    def setloop(l,addr1,addr2,reps):
        self.loops[l].start=addr1
        self.loops[l].stop=addr2
        self.loops[l].n=reps

    def setloopbyaddr(l,addr1,addr2,reps):
        self.loops[l].start=addr1
        self.loops[l].stop=addr2
        self.loops[l].n=reps


    def setwaitpointbyaddress(l,add):
        self.waits[l].addr=add

    def setwaitpoint(l):
        self.waits[l].addr=self.LineN

    def setwaittime(l,t):
        self.waits[l].wtime=t

    def setwait(l,t):
        self.waits[l].addr=self.LineN
        self.waits[l].wtime=t

    def setwaitbyaddress(l,add,t):
        self.waits[l].addr=add
        self.waits[l].wtime=t
    
    def patInfo():
        print("### SUMMARY OF PATTERN PARAMETERS ###")
        print("Pattern limits (patlimits):",self.start,self.LineN-1) 
        i=0
        for l in self.loops:
            print("Loop:",i)
            classItems(l)
            i=i+1
            i=0
        for l in self.waits:
            print("Wait:",i)
            classItems(l)
            i=i+1
        print("Next line to be written:",self.LineN)
        print("########################################")
          
    def saveToFile(fname):
        pwords=''
        paw='patword'
        for i in range(len(self.addrs)):
            patline=paw+' '+hexFormat(self.addrs[i],4)+' '+hexFormat(self.words[i],16)+'\n'
            pwords+=patline
            l0='patloop0 '+hexFormat(self.loops[0].start,4)+' '+hexFormat(self.loops[0].stop,4)+'\n'+'patnloop0 '+str(self.loops[0].n)+'\n'
            l1='patloop1 '+hexFormat(self.loops[1].start,4)+' '+hexFormat(self.loops[1].stop,4)+'\n'+'patnloop1 '+str(self.loops[1].n)+'\n'
            l2='patloop2 '+hexFormat(self.loops[2].start,4)+' '+hexFormat(self.loops[2].stop,4)+'\n'+'patnloop2 '+str(self.loops[2].n)+'\n'
            w0='patwait0 '+hexFormat(self.waits[0].addr,4)+'\n'+'patwaittime0 '+str(self.waits[0].wtime)+'\n'
            w1='patwait1 '+hexFormat(self.waits[1].addr,4)+'\n'+'patwaittime1 '+str(self.waits[1].wtime)+'\n'
            w2='patwait2 '+hexFormat(self.waits[2].addr,4)+'\n'+'patwaittime2 '+str(self.waits[2].wtime)+'\n'
            f=open(fname,'w')
            plims='patlimits '+hexFormat(self.start,4)+' '+hexFormat(self.LineN-1,4)+'\n'
        pF=pwords+plims+l0+l1+l2+w0+w1+w2
        f.write(pF)
        f.close()
        print("Pattern limits (patlimits):",self.start,self.LineN-1)

    def load():
        from slsdet import Detector
        d = Detector()
        for i in range(len(self.addrs)):
            d.setPatternWord(self.addrs[i],self.words[i])
            d.setPatternLoopAddresses(-1,self.start,self.LineN-1)
            for i in range(len(3)):
                d.setPatternLoopAddresses(i,self.loops[i].start,self.loops[i].stop)
                d.setPatternLoopCycles(i,self.loops[i].n)
                d.setPatternWaitAddr(i,self.waits[i].addr)
                d.setPatternWaitTime(i,self.waits[i].wtime)
    

######################################
#I/O functions
#####################################



##END PATTERN CONTROL FUNCTIONS##
##################################################################
def classItems(c):
    for a,b in c.__dict__.items():
        print(a,b)


#global testvar

#def test():
    #global testvar
    #print(testvar)
