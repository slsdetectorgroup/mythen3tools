import read_mythen as my3
import matplotlib.pyplot as plt
import sys

hh,dd=my3.read_my3_file(sys.argv[1], 1, 24)
print(dd)
plt.plot(dd)
plt.show()
