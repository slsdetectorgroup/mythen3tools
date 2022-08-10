from patterntools import pat
from detConf_module import *

p=pat()
setChipStatusRegister(p,(1<<CSR_C10pre ) | (1<< CSR_C15sh) )
p.saveToFile("highestgain.pat")

p=pat()
setChipStatusRegister(p,CSR_default)
p.saveToFile("deafultgain.pat")
