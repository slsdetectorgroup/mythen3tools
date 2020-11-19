from slsdet import Mythen3
from detConf_module import *
import pattern

d = Mythen3()
print(d.hostname)

print('runnign pattern')
pp=digitalPulsingPattern(8,3,2)
print('done')


