from slsdet import Mythen3
from detConf_module import *
import pattern
import numpy as np




d = Mythen3()
print(d.hostname)



print('TEST SERIAL IN')
val=0xbbbbbb
serInErrorMask1=testSerialIn(d,val)
val=0xaaaaaa
serInErrorMask2=testSerialIn(d,val)

if serInErrorMask2|serInErrorMask1==0:
    print("serial IN test succeeded")
else:
    print("serial IN test failed")








"""

print('DIGITAL PULSING')
pp=digitalPulsingPattern(8,3,2)
print('done')

pp.load(d)
d.startReceiver()

d.stopReceiver()
"""
