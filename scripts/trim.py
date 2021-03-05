from slsdet import Mythen3,detectorSettings
from slsdet.lookup import view, find

from patterntools.zmqreceiver import ZmqReceiver
from detConf_module import *
from trimming import *

ff='ChromiumHighgain'


ff='standard_9000eV_200V_500ms'

d = Mythen3()

#d.loadConfig('/afs/psi.ch/user/b/bergamaschi/project/Anna/slsDetectorPackageDeveloper/examples/my30module_standard.config')

d.fpath='/sls/X04SA/Data1/ES2/now/Mythen3_20200122/'
d.fname=ff
#print(d.hostname)

d.stopReceiver()
d.rx_zmqstream=1
d.rx_zmqfreq=1
d.exptime=0.5

d.fwrite=1



rx=makeReceiver(d)
d.settings=detectorSettings.STANDARD
d.counters=[0,1,2]
minthr=1500
maxthr=800
thrstep=-2
nph=2500
nsigma=5




vth,vtrim,trimbits=trim(ff, d,rx,minthr, maxthr, thrstep,nph, nsigma, 1)


