import numpy as np

header_dt = [('frameNumber',np.uint64),
             ('expLength',np.uint32),
             ('packetNumber', np.uint32),
             ('bunchId', np.uint64),
             ('timestamp', np.uint64),
             ('modId', np.uint16),
             ('row', np.uint16),
             ('col', np.uint16),
             ('reserved', np.uint16),
             ('debug', np.uint32),
             ('roundRNumber', np.uint16),
             ('detType', np.uint8),
             ('version', np.uint8)]

bitfield_size = 64
#bytes_per_counter = 3
bits_per_byte = 8


dacnames=["vcassh", "vth2", "vrshaper", "vrshaper_n", "vipre_out", "vth3", "vth1", "vicin", "vcas", "vrpreamp", "vcal_n", "vipre", "vishaper", "vcal_p", "vtrim", "vdcsh", "vthreshold"]

def get_dac_index(dacname):
    global dacnames
    for i in range(len(dacnames)):
        if dacnames[i]==dacname:
            return i
    

def get_dac(dacs,dacname):
    global dacnames
    return dacs[get_dac_index(dacname)]
"""
    dict = {}
    for A, B in zip(dacnames, dacs):
        dict[A] = B
    vv=dict[dacname]
    return vv
"""

#fname must be in the format "/path/fname_{}_suffix.raw"
def read_my3_files(fformat, smin, smax, sstep, n_counters=3, dr = 24):

    n_frames=1

    threshold = np.arange(smin, smax+sstep, sstep)
    nrow = int((smax-smin)/sstep)+1
    ncol=1280*n_counters
    ddata = np.zeros((nrow,ncol), dtype = np.int32)
    hheader = np.zeros(nrow, header_dt)
    
    for i,th in enumerate(threshold):
        fname=fformat.format(th)
        #print(fname)
        try:
            hheader[i], ddata[i] = read_my3_file(fname,n_counters,dr)
        except:
            ddata[i]=ddata[i-1]
    return threshold, ddata




def read_my3_file(fname, n_counters=3, dr = 24):
   

    #24bits behaves like 32 bits
    if dr==24:
        dr=32;
    bytes_per_frame = n_counters*1280*dr//8+112

    i=0
    try:
        f=open(fname, 'rb') 
        n_frames=f.seek(0,2)//bytes_per_frame
        #print("The file contains ",n_frames," frames")
        f.seek(0,0) #go back to the begin
        #print(f.tell())
        
    except:
        print ("Could not open file:", fname)
        return 0,0
        
    if n_frames==0:
        raise Exception('File empty')
        print ("File empty")
        return 0,0
        

    data = np.zeros((n_frames, n_counters*1280), dtype = np.int32)
    header = np.zeros(n_frames, header_dt)
 
    try:
        for i in range(n_frames):
            header[i], data[i] = _read_my3_frame(f, n_counters, dr)

    except:
        print ("Could not read frame:", i)
        #        return 0,0 
    f.close()

    return header, data

def _read_my3_frame(f, n_counters, dr):

    try:
        header = np.fromfile(f, dtype = header_dt, count = 1)
    except:
        print ("Could not read header")

    try:
        f.seek(bitfield_size, 1) #skip bitfield
    except:
        print ("Could not skip packet mask")
        
    bytes_per_counter = dr//bits_per_byte
    bytes_to_read = n_counters*1280*dr//bits_per_byte

    try:
        data = np.fromfile(f, dtype = np.uint8, count = bytes_to_read)
    except:
        print ("Could not read data")
    
    #print(
    try:
        data = data.reshape(data.size//bytes_per_counter, bytes_per_counter).astype(np.int32)
        for i in range(bytes_per_counter):
            data[:,i] = np.left_shift(data[:,i], bits_per_byte*i) 
        data = data.sum(axis = 1)
    except:
      print ("Could not reformat data")

    return header, data

def read_my3_trimbits(fname):  
    try:
        f=open(fname, 'rb') 
    except:
        print ("Could not open file:", fname)
        return 0,0

    try:
        dacs = np.fromfile(f, dtype = np.uint32, count = 16)
    except:
        print ("Could not read dacs")
        return 0,0
    try:
        trimbits = np.fromfile(f, dtype = np.uint32, count = 1280*3)
    except:
        print ("Could not read trimbits")
        return 0,0
    f.close()
    return dacs,trimbits


def read_my3_trimbits_new(fname):  
    try:
        f=open(fname, 'rb') 
    except:
        print ("Could not open file:", fname)
        return 0,0,0

    try:
        gain = np.fromfile(f, dtype = np.uint32, count = 1)
    except:
        print ("Could not read dacs")
        return 0,0,0
    try:
        dacs = np.fromfile(f, dtype = np.uint32, count = 16)
    except:
        print ("Could not read dacs")
        return 0,0,0
    try:
        trimbits = np.fromfile(f, dtype = np.uint32, count = 1280*3)
    except:
        print ("Could not read trimbits")
        return 0,0,0
    f.close()
    return gain,dacs,trimbits



def write_my3_trimbits(fname,dacs,trimbits):  
    try:
        f=open(fname, 'wb') 
    except:
        print ("Could not open file:", fname)
    try:
        dacs.tofile(f)
    except:
        print ("Could not write dacs")
    try:
        trimbits.tofile(f)
    except:
        print ("Could not write trimbits")
    f.close()


def write_my3_trimbits_new(fname,gain,dacs,trimbits):  
    try:
        f=open(fname, 'wb') 
    except:
        print ("Could not open file:", fname)
    try:
        gain.tofile(f)
    except:
        print ("Could not write gain")
    try:
        dacs.tofile(f)
    except:
        print ("Could not write dacs")
    try:
        trimbits.tofile(f)
    except:
        print ("Could not write trimbits")
    f.close()

