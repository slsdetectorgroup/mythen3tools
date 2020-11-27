import read_mythen as my3
import matplotlib.pyplot as plt
import sys

hh,dd=my3.read_my3_file(sys.argv[1], 3, 24)
plt.plot(dd[0])
plt.show()
