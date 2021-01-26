import matplotlib.pyplot as plt
import numpy as np
import read_mythen as my3

#from numpy import exp, loadtxt, pi, sqrt
import math
from lmfit import Model,Parameters,Minimizer, report_fit
from lmfit.models import LinearModel
from scipy.signal import argrelextrema

#############################################################
####### Need to work on fitting range and start parameters
##############################################################

def scurve(th,pedestal, pedslope, flex, noise, amplitude, chargesharing):
 #print(x.shape) 
    sign=True
    if sign:
        s=1
    else:
        s=-1
    y=0.5*amplitude*(1+math.erf(s*(flex-th)/(noise*math.sqrt(2))))*(1+chargesharing*(flex-th))+pedestal-pedslope*th*s
    return y

def scurve_fit(x, pedestal, pedslope, flex, noise, amplitude, chargesharing):
    #print(x.shape) 
    y=np.zeros(x.shape, dtype = x.dtype)
    sign=True
    if sign:
        s=1
    else:
        s=-1
    for i,th in enumerate(x):
        y[i]=scurve(th, pedestal, pedslope, flex, noise, amplitude, chargesharing)
    return y

gmodel = Model(scurve_fit)



#find a good way to determine initial parameters
#flex0=1300 
#ampl0=3000 

def init_params(flex0, ampl0):
    global gmodel
    noise0=20 
    cs0=0.0005
    gmodel.set_param_hint('pedestal',value=0, vary=False )
    gmodel.set_param_hint('pedslope',value=0, vary=False )
    gmodel.set_param_hint('flex',value=flex0, min=800, max=2800)
    gmodel.set_param_hint('noise',value=noise0, min=5, max=200)
    if ampl0<100:
        ampl0=100
    gmodel.set_param_hint('amplitude',value=ampl0,min=0.1*ampl0,max=2*ampl0)
    gmodel.set_param_hint('chargesharing',value=cs0,min=0.0001,max=0.01)
    params = gmodel.make_params()
    return params

def init_fix_cs(val):
    global gmodel
    gmodel.set_param_hint('chargesharing',value=val,vary=False)
    params = gmodel.make_params()

def init_fix_ampl(val):
    global gmodel
    gmodel.set_param_hint('amplitude',value=val,min=val,max=1.5*val,vary=False)
    params = gmodel.make_params()





def fit_scurve(x, y, params=None, e=None):
    global gmodel
    
    
   # for pname, par in params.items():
    #    print(pname, par)
    """
    if e is None:
        w=np.where(y==0,1,y)
    else:
        w=np.where(e==0,1,e*e)
        #w[np.where(e==0,1,e)]=1 
    w=1/w
    """
    w=np.where(y==0,1,1)
#find a good way to determine fitting range!
    thresholds=x.astype(np.float64)
    data=y.astype(np.float64)
    imin=0
    imax=thresholds.shape[0]-1
    sstep=thresholds[1]-thresholds[0]

    imin=0
    imax=thresholds.shape[0]-1
    #mm=0
    #print(gmodel.param_hints["amplitude"]["max"])
    counts0=gmodel.param_hints["amplitude"]["value"]
    cmax=gmodel.param_hints["amplitude"]["max"]
    flex0=-1
    ##########################################################################################
    #########FINDING START PARAMETERS
    ##########################################################################################

    if (thresholds[imin]>thresholds[imax]):
        imax=0
        while data[imax]<=cmax and imax<thresholds.shape[0]-1:
            imax+=1
            if data[imax]<counts0:
                #if flex0<0:
                flex0=thresholds[imax]
        if data[imax]>=cmax:
            vv=np.where(thresholds>thresholds[imax]+10)
            if len(vv[0]>0):
                imax=vv[0][-1]
            else:
                imax=-1
                #imax=vv[-1]
            #print(imax,vv)
    else:
        imin=thresholds.shape[0]-1
        while data[imin]<=cmax and imin>0:
            imin-=1
            if data[imin]<counts0:
                #if flex0<0:
                flex0=thresholds[imin]
        if data[imin]>=cmax:
            vv=np.where(thresholds>thresholds[imin]+10)
            if len(vv[0])>0:
                imin=vv[0][0]
            else:
                imin=0
                #imin=vv[0]
            #print(imin,vv)
    #print("Fitting range:",thresholds[imin],thresholds[imax])
    
    if flex0>0:
        #print(flex0,thresholds[imin],thresholds[imax])
        fmi=min(thresholds[imin],thresholds[imax-1])-10
        fma=max(thresholds[imin],thresholds[imax-1])+10
        #print("--",flex0,thresholds[imin],thresholds[imax-1])
        gmodel.set_param_hint('flex',value=flex0, min=fmi, max=fma)
    #else:
        #print("--",flex0,thresholds[imin],thresholds[imax-1])
    ####################################################################################
   
    """
    #########
    ## Way to automatically find start parameters
    ########
    thrmin,flex0,counts0=find_start_param(data,thresholds[0],thresholds[-1],sstep)
    gmodel.set_param_hint('flex',value=flex0, min=flex0/2, max=flex0*2+1)
    gmodel.set_param_hint('amplitude',value=counts0, min=counts0/5., max=counts0+1)
    tt=np.where(thresholds>thrmin)
    if sstep>0:
        imin=tt[0][0]
    else:
        imax=tt[-1][-1]
    good=1
    if thrmin==0:
        #print("BAD")
        good=0
    """
    params = gmodel.make_params()
    #print(data[imin:imax].shape,thresholds[imin:imax].shape)
    
    while imax-imin<=len(params.valuesdict()):
        if imin>0:
            imin-=1
        if imax<thresholds.shape[0]-1:
            imax+=1
    result = gmodel.fit(data[imin:imax], params, x=thresholds[imin:imax], weights=w[imin:imax])#, method='nelder') 
    good=1
    if not result.success:
        #print("BAD1",thrmin,flex0,counts0)
        good=0
    """   else:
        for pname, par in result.params.items():
            if par.vary:
                if par.value<par.min+0.001*par.min:
                    #print("*m*",pname,par.value,par.min)
                    good=0
                elif par.value>par.max-0.001*par.max:
                    #print("*M*",pname,par.value,par.max)
                    good=0
    """
    if good==0:
        #print("---")
        #print("BAD1",thrmin,flex0,counts0)
        """for pname, par in result.params.items():
            if par.vary:
                print("*m*",pname,par.value,par.min,par.max)
        """

    return result
    #    print(result.fit_report())


def fit_all(thresholds,data):
    global gmodel
  
    params = gmodel.make_params()


    flex = np.zeros(data.shape[1],dtype = np.float64)  
    noise = np.zeros(data.shape[1],dtype = np.float64) 
    ampl = np.zeros(data.shape[1],dtype = np.float64) 
    cs = np.zeros(data.shape[1],dtype = np.float64) 
    counts = np.zeros(data.shape[1],dtype = np.float64) 
    #print(flex.shape)
    #print(noise.shape)
    #print(ampl.shape)
    #print(cs.shape)
    #fig,ax=plt.subplots()
    #print(data.shape[1])
    ibad=0
    for i in range(data.shape[1]):
         result=fit_scurve(thresholds,data[:,i],params)
         if result.success:
             good=1
            # print("flex",params['flex'])

             for pname, par in result.params.items():
                 #print("***",result.params[pname]) 
                 # if 'bounds' in par:
                 #print(par.min)
                 if par.vary:
                     if par.value<par.min+0.001*par.min:
                         #print("*m*",pname,par.value,par.min)
                         good=0
                     elif par.value>par.max-0.001*par.max:
                         #print("*M*",pname,par.value,par.max)
                         good=0

             if good>0:
                 flex[i]=result.params['flex'].value
                 noise[i]=result.params['noise'].value
                 ampl[i]=result.params['amplitude'].value
                 cs[i]=result.params['chargesharing'].value
                 counts[i]=scurve(flex[i],0, 0, flex[i], noise[i], ampl[i], cs[i])
                 #print(i,flex[i],noise[i],ampl[i],cs[i],result.chisqr)
             else:
                 #plot_fit(thresholds,data[:,i],result,ax,fig)
                 ibad+=1
                 #if ibad>10:
                     #break;
                 #print(i,"Bad fit",result.params['flex'].value,result.params['noise'].value,result.params['amplitude'].value,result.params['chargesharing'].value,result.chisqr)
            
            
         #else:
             #print(i,"Could not fit ")
    #fig.show()
    print("Could not fit",ibad,"channels")
    return flex,noise,ampl,cs,counts

"""
def plot_fit(thresholds,data,result):
    fig2 = plt.figure(figsize=(6, 6))
    ax= fig2.add_subplot()
    ax.plot(thresholds, data, 'bo')
    plt.plot(thresholds[0:result.init_fit.shape[0]], result.init_fit, 'k--', label='initial fit')
    plt.plot(thresholds[0:result.init_fit.shape[0]], result.best_fit, 'r-', label='best fit')
    ax.legend(loc='best')  
    print(result.fit_report())
    #plt.show()
    return
"""



def fit_file(fname,ncounters,dr,smin,smax,ff,aa):
    head, data=my3.read_my3_file(fname,ncounters,dr)
    if (data.shape[0]>1):
        sstep=(smax-smin)/(data.shape[0]-1)
    else:
        return 0,0,0,0
    thr = np.arange(smin, smax+sstep, sstep)
    init_params(ff,aa)

    dd=np.sum(data,axis=1)/data.shape[1]
    result=fit_scurve(thr,dd)
    mod_flex=result.params['flex'].value
    mod_noise=result.params['noise'].value
    mod_ampl=result.params['amplitude'].value
    mod_cs=result.params['chargesharing'].value
    mod_counts=scurve(mod_flex,0, 0, mod_flex, mod_noise, mod_ampl, mod_cs)

    flex,noise,ampl,cs,counts=fit_all(thr,data)

    flex=np.append(flex,mod_flex)
    noise=np.append(noise,mod_noise)
    ampl=np.append(ampl,mod_ampl)
    cs=np.append(cs,mod_cs)
    counts=np.append(counts,mod_counts)
    

    return flex,noise,ampl,cs,counts

def save_scurve_fit_file(outFname,flex,noise,ampl,cs,counts):
    chans=np.array(range(0,flex.shape[0]),dtype=int)
    xxx=np.concatenate((chans.reshape(chans.shape[0],1),flex.reshape(chans.shape[0],1),noise.reshape(chans.shape[0],1),ampl.reshape(chans.shape[0],1),cs.reshape(chans.shape[0],1),counts.reshape(chans.shape[0],1)), axis=1)
    np.savetxt(outFname, xxx, fmt='%s', delimiter='\t', header='chan\t flex\t noise\t ampl\t cs\t counts',  encoding=None)

def load_scurve_fit_file(inFname):
    chans,flex,noise,ampl,cs,counts= np.loadtxt(inFname,unpack=True, delimiter='\t')
    print(flex.shape)
    return flex,noise,ampl,cs,counts

def save_encal(outFname,gain,offset):
    chans=np.array(range(0,gain.shape[0]),dtype=int)
    xxx=np.concatenate((chans.reshape(chans.shape[0],1),gain.reshape(chans.shape[0],1),offset.reshape(chans.shape[0],1)), axis=1)
    np.savetxt(outFname, xxx, fmt='%s', delimiter='\t', header='chan\t gain\t offset',  encoding=None)

def load_encal(inFname):
    gain,offset= np.loadtxt(outFname,unpack=True, delimiter='\t')
    return gain,offset


def plot_fit(thresholds,data,result,ax=None, fig=None):
    if ax is None:
        fig,ax=plt.subplots()
    #print(thresholds.shape,data.shape)
    result.plot_fit(ax)
    ax.plot(thresholds, data, 'bo')
    #plt.plot(thresholds[0:result.init_fit.shape[0]], result.init_fit, 'k--', label='initial fit')
    #ax.plot(thresholds[0:result.init_fit.shape[0]], result.best_fit, 'r-', label='best fit')
    #ax.legend(loc='best')  
    #print(result.fit_report())
    #plt.show()
    #fig.show()
    return fig,ax

def linear_fit(x,y):
    mod = LinearModel()
    pars = mod.guess(y, x=x)
    #pars['gamma'].set(value=0.7, vary=True, expr='')
    result = mod.fit(y, pars, x=x)#, weights=w[imin:imax])#, method='nelder')
    return result

def encal_all(ens,flex):
    print("**",flex[0].shape)
    
    nch=flex[0].shape[0]
    nenergies=ens.shape[0]
    fl = np.zeros(shape=(nch,nenergies))
    for i in range(0,nenergies):
        d1=flex[i]
        for ich in range(0,fl.shape[0]):
            fl[ich,i]=d1[ich]
    gain = np.empty(nch)
    offset = np.empty(nch)
    for ich in range(0,nch):
        result=linear_fit(ens,fl[ich])
        gain[ich]=result.params['slope'].value
        offset[ich]=result.params['intercept'].value
    return gain,offset

def find_start_param(data,smin,smax,sstep):

    if data.ndim>1:
        dd=np.median(data, axis=1)
        #dd=np.sum(data,axis=1)/data.shape[1]
    else:
        dd=data
    thr=np.arange(smin,smax+sstep,sstep)
    thr1=thr[1:]
    ns=int(len(thr1)/20)
    nn=len(thr1)
    lmax=[]
    lmin=[]
    sp=smooth(np.diff(dd),ns)
    #sp=np.diff(dd)
    ll=[]
    LL=[]
    nn=sp.shape[0]
    lmax=argrelextrema(sp, np.greater)
    lmin=argrelextrema(sp, np.less)
    ll=lmin[0]
    LL=lmax[0]
    nn=len(LL)
    nn1=len(ll)
    ii=0
    #print(ii,"---",nn,nn1)

    if nn>0 and nn1>0:
        while nn>3:
            #print(ii,"***",sp[LL],np.max(sp[LL]))
            lmax=argrelextrema(sp[LL], np.greater)
            nn=len(lmax[0])
            if nn>0:
                LL=LL[lmax[0]]
            else:
                nn=len(LL)
                break
            ii=ii+1
        #print(ii,"---",nn)
        ii=0
        
        while nn1>50:
            #print(ii,"***",sp[ll],sp[ll[-1]])
            lmin=argrelextrema(sp[ll], np.less)
            nn1=len(lmin[0])
            if nn1>0:
                ll=ll[lmin[0]]
            else:
                nn1=len(ll)
                break
            ii=ii+1
        #print(ii,"===",nn1)

        if thr1[0]<thr1[1]:
            mm=ll[0]
            LL1=LL[LL>mm]
        else:
            mm=ll[-1]
            LL1=LL[LL<mm]

        if len(LL1)==0:
            LL1=LL

        vv=np.max(sp[LL1])
        aa=np.where(sp==vv)

        if thr1[0]<thr1[1]:
            MM=aa[0][-1]
        else:
            MM=aa[0][0]
        return thr1[mm],thr1[MM],dd[mm]
    
    return 0,0,0


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
