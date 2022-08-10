import read_mythen as my3
import matplotlib.pyplot as plt
import sys

nmod=int(sys.argv[2])
fformat=sys.argv[1]
for imod in range(0,nmod):
    fname=fformat.format(imod)
    print(imod,fname)
    hh,dd=my3.read_my3_file(fname, 1, 24)
    print(dd[0])
    plt.plot(dd[0])

plt.show()

