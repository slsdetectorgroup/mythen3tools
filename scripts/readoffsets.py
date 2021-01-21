import numpy as np
import matplotlib.pyplot as plt

f=open('/mnt/myData/offsetsNoCable.txt',"r")
lines=f.readlines()
f.close()

clkdiv=[]
off=[]
phase=[]
for line in lines:
    line=line.rstrip("\n")
    vals=line.split(" ")
    if vals[0]=="DIGITAL":
        print(line)
    elif vals[0]=="IMPORTING":
        print(line)
    elif vals[0]=="no":
        print(line)
    else:
        clkdiv=np.append(clkdiv,int(vals[1],0))
        off=np.append(off,int(vals[2],0))
        phase=np.append(phase,int(vals[3],0))
        #print("!!!",int(vals[1],0),int(vals[2],0),int(vals[3],0))
        

f=open('/mnt/myData/offsetsNoCable2.txt',"r")
lines=f.readlines()
f.close()

for line in lines:
    line=line.rstrip("\n")
    vals=line.split(" ")
    if vals[0]=="DIGITAL":
        print(line)
    elif vals[0]=="IMPORTING":
        print(line)
    elif vals[0]=="no":
        print(line)
    else:
        clkdiv=np.append(clkdiv,int(vals[1],0))
        off=np.append(off,int(vals[2],0))
        phase=np.append(phase,int(vals[3],0))
        #print("!!!",int(vals[1],0),int(vals[2],0),int(vals[3],0))
vv=[]
oo=[]
for i in range(9,40):
    a=off[clkdiv==i]
    vv=np.append(vv,len(a))
    if len(a)>0:
        oo=np.append(oo,a[0])
        print(hex(int(a[0])))
    else:
        oo=np.append(oo,0)

plt.plot(range(9,40),vv)
#plt.plot(range(9,40),oo)
#plt.show()

f=open('/mnt/myData/offsetsNoCable4.txt',"r")
lines=f.readlines()
f.close()

clkdiv1=[]
off1=[]
phase1=[]
vv1=[]
oo1=[]
for line in lines:
    line=line.rstrip("\n")
    vals=line.split(" ")
    if vals[0]=="DIGITAL":
        print(line)
    elif vals[0]=="IMPORTING":
        print(line)
    elif vals[0]=="no":
        print(line)
    else:
        clkdiv1=np.append(clkdiv1,int(vals[1],0))
        off1=np.append(off1,int(vals[2],0))
        phase1=np.append(phase1,int(vals[3],0))
        #print("!!!",int(vals[1],0),int(vals[2],0),int(vals[3],0))

for i in range(9,40):
    a=off1[clkdiv1==i]
    vv1=np.append(vv1,len(a))
    if len(a)>0:
        oo1=np.append(oo1,a[0])
        print(hex(int(a[0])))
    else:
        oo1=np.append(oo1,0)

#plt.plot(range(9,40),oo1)
plt.plot(range(9,40),vv1)
plt.show()
