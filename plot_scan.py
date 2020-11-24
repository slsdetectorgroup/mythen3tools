import numpy as np
import matplotlib.pyplot as plt




def plot_thrscan(adata, smin, smax, sstep):
    #plt.ion()
    global data
    data=adata
    #head, data=read_my3_file(fname)
    
    global x_hist, y_hist, z_hist
    global fig
    global threshold
    global chans
    global mmm
    global im_main
    global chanmin
    global chanmax
    global thrmin
    global thrmax
    global main_ax
    global x_hist
    global y_hist
    global z_hist
    fig = plt.figure(figsize=(6, 6))
    #print("+")
    grid = plt.GridSpec(8, 8, hspace=0, wspace=0)
    #print("+")
    main_ax = fig.add_subplot(grid[:-3, 3:])
    #print("+")
    y_hist = fig.add_subplot(grid[:-3, :3], xticklabels=[], sharey=main_ax)
    #print("+")
    x_hist = fig.add_subplot(grid[-3:, 3:], yticklabels=[], sharex=main_ax)
    #print("+")
    z_hist = fig.add_subplot(grid[-2:, 0:1], xmargin=0.2, ymargin=0.2)#, yticklabels=[], sharex=main_ax)
    imx=None
    imy=None

    x_hist.set_xlabel("Channel number")
    y_hist.set_ylabel("Threshold")

    thrmin=0
    thrmax=2400
    chanmin=0
    chanmax=1280*3

    #mmm=1.6E7

    threshold = np.arange(smin, smax+sstep, sstep)
    chans = np.arange(0, data.shape[1])  
    #print(threshold.shape, chans.shape,data.shape)
    chanmin=0
    chanmax=data.shape[1]
    thrmin=smin
    thrmax=smax
    mmm=20000
    #pdata=data
    pdata=np.where(data< mmm, data, mmm)
    im_main = main_ax.contourf(chans, threshold, pdata, 100, cmap=plt.cm.jet)

    #main_ax.xaxis.set_ticklabels([])
    #main_ax.yaxis.set_ticklabels([])

    main_ax.set_yticklabels([])
    main_ax.set_xticklabels([])
    fig.colorbar(im_main, ax=main_ax,cax=z_hist)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    cid2=fig.canvas.mpl_connect('scroll_event', onscroll)
    mmm=np.amax(pdata)
    im_main.set_clim(0, mmm) # or whatever color limits you want
    fig.show()
    return fig,main_ax

def plot_simple_thrscan(adata, threshold):
    fig, ax = plt.subplots()
    chans = np.arange(0, adata.shape[1])  
    ax.contourf(chans, threshold, adata, 100, cmap=plt.cm.jet)
    return fig,ax

def plot_channel(ch):
    global x_hist
    global threshold
    global data
    global imy
    y_hist.clear()
    imy=y_hist.plot(data[:,ch],threshold )
    #print(type(im))
    return 

def plot_threshold(thr):
    global y_hist
    global chans
    global data
    global threshold
    global imx

    ith=np.digitize(thr, threshold)#np.where(threshold == thr)
    #print(thr,threshold,ith)
    dd=data[ith,:]
    #print(chans.shape,dd.shape)
    x_hist.clear()
    imx=x_hist.plot(chans,dd)
    #print(type(im))
    return 



def onclick(event):
    global main_ax
    global fig
    axes = event.inaxes
    global threshold
    if (axes==main_ax):
        ix, iy = event.xdata, event.ydata
        print ("x = ", ix, " y = ",iy)
        #print(type(ix),type(iy))
        if type(ix) is np.float64 and type(iy) is np.float64:
            #print("main")
            plot_channel(ix.astype(int))
            plot_threshold(iy.astype(int))
            #imy.update()
            #imx.update()
            iy=threshold[np.digitize(iy, threshold)]
            tit="Channel"+str(ix.astype(int))+" Threshold "+str(iy.astype(int))
            fig.suptitle(tit, fontsize=12)
            fig.canvas.draw()
            #plt.draw()
            #plt.clf()
    return ix,iy


def onscroll(event):
    global mmm
    global im_main
    global x_hist
    global y_hist
    global chanmin
    global chanmax
    global thrmin
    global thrmax
    global data
    axes = event.inaxes
    #  print("%s %s" % (event.button, event.step))  
    if (axes==main_ax or axes==z_hist):
        mmm=(1-event.step*0.5)*mmm
        if (mmm<100): 
            mmm=100
        print(mmm)
        #im_main.set_clim(0, mmm) # or whatever color limits you want
        #pdata=data
        #pdata[np.where(data>mmm)]=mmm
        pdata=np.where(data< mmm, data, mmm)
        im_main = main_ax.contourf(chans, threshold, pdata, 100, cmap=plt.cm.jet)
        x_hist.set_ylim(0, mmm) 
        y_hist.set_xlim(0, mmm) 
    if (axes==x_hist):
        ix, iy = event.xdata, event.ydata
        nch=chanmax-chanmin+1
        nch1=nch+event.step*0.5*nch
        #cent=(chanmax-chanmin)/2
        chanmin=ix-nch1/2
        chanmax=ix+nch1/2
        if chanmin>chanmax:
            ch=chanmax
            chanmax=chanmin
            chanmin=ch
        if chanmin<0:
            chanmin=0
        if chanmax<0:
            chanmax=0
        if chanmax>data.shape[1]:
            chanmax=data.shape[1]
        if chanmin>data.shape[1]:
            chanmin=data.shape[1]
        print(chanmin,chanmax)
        x_hist.set_xlim(chanmin, chanmax) # or whatever color limits you want 
    #do the same for the thresholds    
    if (axes==y_hist):
        ix, iy = event.xdata, event.ydata
        nthr=thrmax-thrmin+1
        nthr1=nthr+event.step*0.5*nthr
        #cent=(chanmax-chanmin)/2
        thrmin=iy-nthr1/2
        thrmax=iy+nthr1/2
        if thrmin>thrmax:
            ch=thrmax
            thrmax=thrmin
            thrmin=ch
        if thrmin<0:
            thrmin=0
        if thrmax<0:
            thrmax=0
        if thrmax>threshold[-1]:
            thrmax=threshold[-1]
        if thrmax>threshold[-1]:
            thrmin=threshold[-1]
        if thrmin<threshold[0]:
            thrmin=threshold[0]
        if thrmax<threshold[0]:
            thrmax=threshold[0]
        print(thrmin,thrmax)
        y_hist.set_ylim(thrmin, thrmax) # or whatever color limits you want 
    fig.canvas.draw()
    return
