import read_mythen as my3
import matplotlib.pyplot as plt
import sys

hh,dd=my3.read_my3_file(sys.argv[1], 1, 24)
print(dd[0])
plt.plot(dd[0])
plt.show()
