
from slsdet import Detector, patternParameters
from mythen3tools.bits import setbit, clearbit
from mythen3tools.format import hexFormat, hexFormat_nox, binFormat, binFormat_nob, decFormat
import numpy as np


class pat:
#this is a "local style" class
    def __init__(self):
        self.pattern=patternParameters()
        self.iaddr=0

    ################################################################
  
    ################################################################
    ##PATTERN CONTROL FUNCTIONS##


    def SB(self,*args):
        for i in args:
            self.pattern.word[self.iaddr]=setbit(i,self.pattern.word[self.iaddr])
        return self.pattern.word[self.iaddr]
 
    def CB(self,*args):
        for i in args:
            self.pattern.word[self.iaddr]=clearbit(i,self.pattern.word[self.iaddr])
        return self.pattern.word[self.iaddr]
    

    def pw(self,verbose=0):
        if verbose==1:
            print(hexFormat(self.iaddr,4)+' '+hexFormat(self.pattern.word[self.iaddr],16))
        self.pattern.patlimits[1]=self.iaddr
        print("pw",self.iaddr,self.pattern.word[self.iaddr])
        self.iaddr+=1
        self.pattern.word[self.iaddr]=self.pattern.word[self.iaddr-1]

    def PW(self,verbose=0):
        self.pw(verbose)

    def REPEAT(self,x,verbose=0):
        for i in range(x):
            self.pw()

    def PW2(self,verbose=0):
        self.REPEAT(2,verbose)


    def CLOCKS(self,bit,times=1,verbose=0):
        for i in range(0,times):
            self.SB(bit); self.pw(verbose)
            self.CB(bit); self.pw(verbose)

    def CLOCK(self,bit,verbose=0):
        self.CLOCKS(bit,1)

    #NOT DEBUGGED!!!
    def serializer(self,value,serInBit,clkBit,nbits,msbfirst=1):
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
        self.CB(serInBit,clkBit)
        self.pw() #generate intial line with clk and serIn to 0
        start=0;stop=nbits;step=1
        if msbfirst:
            start=nbits-1;stop=-1;step=-1 #reverts loop if msb has to be pushed in first
            for i in range(start,stop,step):
                if c & (1<<i): 
                    self.SB(serInBit)
                    self.pw()
                else:
                    self.CB(serInBit)
                    self.pw()
                self.SB(clkBit)
                self.pw()
                self.CB(clkBit)
                self.pw() 
            self.CB(serInBit,clkBit)
            self.pw() #generate final line with clk and serIn to 0     
            #NOT IMPLEMENTED YET
            #def setstop():    
            #
            #def setoutput(bit):
            #    self.ioctrl=self.setbit(bit,self.ioctrl)
            #
            #def setinput(bit):
            #    self.ioctrl=self.clearbit(bit,self.ioctrl)
        #
        #def setclk(bit):
        #    self.clkctrl=self.setbit(bit,self.clkctrl)

   # def setinputs(self, *args):
    #    for i in args:
     #       self.setinput(i)

    #def setoutputs(self, *args):
     #   for i in args:
      #      self.setoutput(i)
        
    #def setclks(self, *args):
    #    for i in args:
    #        self.setclk(i)

    def setnloop(self,l,reps):
        self.pattern.patnloop[l]=reps
        print("patnloop",l,reps,self.pattern.patnloop[l])

    def setstartloop(self,l):
        self.pattern.patloop[l*2]=self.iaddr
        print("patstart",l,self.iaddr,self.pattern.patloop[l*2])

    def setstoploop(self,l):
        self.pattern.patloop[l*2+1]=self.iaddr
        print("patstop",l,self.iaddr,self.pattern.patloop[l*2+1])
        

    def setstart(self,l):
        self.pattern.patlimits[0]=self.iaddr
        print("start",self.iaddr,self.pattern.patlimits[0])

    def setstop(self,l):
        self.pattern.patlimits[1]=self.iaddr
        print("stop",self.iaddr,self.pattern.patlimits[1])
        
    def setwaitpoint(self,l):
        self.pattern.patwait[l]=self.iaddr
        print("wait",l,self.iaddr,self.pattern.patwait[l])

    def setwaittime(self,l,t):
        self.pattern.patwaittime[l]=t
        print("waittime",l,t,self.pattern.patwaittime[l])

    def setwait(self,l,t):
        self.setwait(l)
        self.setwaittime(l,t)

    
    def patInfo(self):
        print("### SUMMARY OF PATTERN PARAMETERS ###")
        print("Pattern limits (patlimits):",self.pattern.patlimits) 
        print("Loop:",self.pattern.patloop)
        print("Nloop:",self.pattern.patnloop)
        print("Wait:",self.pattern.patwait)
        print("Waittime",self.pattern.patwaittime)
        print("Words",self.pattern.word[self.pattern.word>0])
        print("########################################")
          
    def saveToFile(self,fname):
        pwords=''
        for i in range(len(self.pattern.patlimits[2])):
            l='patword '+hexFormat(i,4)+' '+hexFormat(self.pattern.word[i],16)+'\n'
            pwords+=l
        for i in range(3):
            l='patloop'+str(i)+' '++hexFormat(self.pattern.patloop[i*2],4)+' '+hexFormat(self.pattern.patloop[i*2+1],4)+'\n'+'patnloop'+str(i)+' '+str(self.pattern.patnloop[i])+'\n'
            pwords+=l
        for i in range(3):
            l='patwait'+str(i)+' '+hexFormat(self.pattern.patwait[i].addr,4)+'\n'+'patwaittime'+str(i)+' '+str(self.pattern.patwaittime[i].wtime)+'\n'
            pwords+=l
        
        l='patlimits '+hexFormat(self.pattern.patlimits[0],4)+' '+hexFormat(self.pattern.patlimits[1],4)+'\n'
        pwords+=l

        f=open(fname,'w')
        f.write(pwords)
        f.close()
        

    def load(self,d):
        from slsdet import Detector
        print("Loading pattern")
        d.setPattern(self.pattern)

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
