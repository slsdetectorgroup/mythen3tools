import numpy as np
import h5py
import matplotlib.pyplot as plt


class My3AngConvSlim:
    def __init__(self):
        self.NModMax = 48
        self.NModMax1 = self.NModMax - 1
        self.fn_unconn = 'TDATA/ModOut.txt'
        
        self.pi = np.pi
        self.deg_to_rad = self.pi / 180.0
        self.rad_to_deg = 180.0 / self.pi
        self.BLOFFSET = 1.532
        
        self.Dimmod = 1280
        self.Dimmod1 = self.Dimmod - 1
        self.Dimdet = self.NModMax * self.Dimmod
        self.Dimdet1 = self.Dimdet - 1
        
        self.isbad = np.zeros(self.Dimdet, dtype=int)
        self.mod_enabled = np.ones(self.NModMax, dtype=int)
        
        self.pitch = 0.05
        self.hwmc = self.Dimmod1 * 0.5
        self.hwm = self.hwmc * self.pitch
        
        self.angcal_DG = np.zeros((3, self.NModMax))
        self.angcal_EE = np.zeros((3, self.NModMax))
        self.angcal_BC = np.zeros((3, self.NModMax))
        self.angcal_SIGN = np.ones(self.NModMax, dtype=int)
        self.ff_corr = np.zeros(self.Dimdet)
        
        self.I0_mon = 0
        self.exptime_s = 0
        self.tt_angle_det = 0
        self.mon_rate = 1.
        
        self.ttmin = -180.0
        self.ttmax = 180.0
        self.ttstep = 0.0036
        self.ntt1 = 0
        self.ntt2 = 0
        self.dtt0 = 0.0
        self.dzmm = 0.0
        self.dymm = 0.0
        self.bin_ready = False

    def check_unconnected(self):
        with open(self.fn_unconn, 'r') as f:
            self.N_Mod_unconn = int(f.readline().strip())
            if self.N_Mod_unconn > 0:
                self.IMod_unconn = np.array([int(x) for x in f.readline().split()])
                for mod in self.IMod_unconn:
                    self.mod_enabled[mod] = 0
                    k1 = mod * self.Dimmod
                    k2 = k1 + self.Dimmod1
                    self.isbad[k1:k2 + 1] = 1
        
        self.neffmod = self.NModMax - self.N_Mod_unconn
        self.neffmod1 = self.neffmod - 1
        self.neffchan = self.neffmod * self.Dimmod
        self.neffchan1 = self.neffchan - 1

    def read_h5raw(self, fn_h5):
        datasetI0mon = "/entry/instrument/NDAttributes/Izero"
        datasetExpTime = "/entry/instrument/NDAttributes/AcquireTime"
        datasetTH2Angle = "/entry/instrument/NDAttributes/DetectorAngle"
        datasetCMask = "/entry/instrument/NDAttributes/CounterMask"
        datasetDRange = "/entry/instrument/NDAttributes/DynamicRange"
        datasetCounts = "/entry/instrument/detector/data"
        with h5py.File(fn_h5, 'r') as f:
            self.I0_mon = f[datasetI0mon][()]  # Read intensity
            self.tt_angle_det = f[ datasetTH2Angle][()]  # Read angle
            self.exptime_s = f[datasetExpTime][()]  # Read exposure time
            image_out = f[datasetCounts][()]  # Read image array
            
            #self.dim_chans = data.shape[0]
            nimg_h5 = 1 if len(image_out.shape) == 1 else image_out.shape[1]
            #self.image_out = np.expand_dims(data, axis=-1) if len(data.shape) == 1 else data
        
        self.nimg_read = nimg_h5
        self.nchan_read = self.neffchan
        self.chread = np.zeros((self.Dimdet, nimg_h5))
        #print(self.chread.shape,self.Dimdet, nimg_h5 )
        if self.N_Mod_unconn <= 0:
            self.chread = np.where(image_out > 0, image_out + 1.0, 0.0).reshape((self.Dimdet, nimg_h5))
        else:
            kx = 0
            for m in range(self.NModMax):
                if m in self.IMod_unconn:
                    continue
                kx += 1
                i1, i2 = m * self.Dimmod, m * self.Dimmod + self.Dimmod1
                j1, j2 = (kx - 1) * self.Dimmod, (kx - 1) * self.Dimmod + self.Dimmod1
                self.chread[i1:i2 + 1, :] = np.where(image_out[j1:j2 + 1, :] > 0, image_out[j1:j2 + 1, :] + 1.0, 0.0)
        return self.I0_mon, self.tt_angle_det, self.exptime_s

    def read_ff(self, fn_ff):
        tol = 0.001
        self.ff_corr.fill(-1)
        
        with open(fn_ff, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2:
                    continue
                ic, cou = int(parts[0]), float(parts[1])
                if self.isbad[ic] == 1 or cou < tol:
                    continue
                self.ff_corr[ic] = cou
        
        valid_indices = self.ff_corr > tol
        nact = np.count_nonzero(valid_indices)
        avcou = np.sum(self.ff_corr[valid_indices]) / nact
        fak = 1.0 / avcou
        
        self.ff_corr = np.where(valid_indices, 1.0 / (self.ff_corr * fak), -1)
        self.isbad = np.where(self.ff_corr < tol, 1, self.isbad)

    def prep_merge(self):
        self.ntt1 = int(self.ttmin / self.ttstep)
        self.ntt2 = int(self.ttmax / self.ttstep)
        self.bin_ready = True
        
        self.binone_acc = np.zeros((self.ntt2 - self.ntt1 + 1, 4))
        self.mergall_acc = np.zeros((self.ntt2 - self.ntt1 + 1, 4))
        self.out_one = np.zeros((self.ntt2 - self.ntt1 + 1, 3))
        self.out_all = np.zeros((self.ntt2 - self.ntt1 + 1, 3))

    def merge_it(self):
        self.mergall_acc += self.binone_acc
        plt.plot(np.arange(self.ntt1, self.ntt2 + 1)[self.mergall_acc[:, 1]>0] * self.ttstep, self.mergall_acc[self.mergall_acc[:, 1]>0, 2]/self.mergall_acc[self.mergall_acc[:, 1]>0, 1])
        plt.show()

    def output(self, fn_xye):
        with open(fn_xye, 'w') as f:
            for i in range(self.ntt1, self.ntt2 + 1):
                if self.mergall_acc[i, 0] < 0.1:
                    continue
                val = self.mergall_acc[i, 2] / self.mergall_acc[i, 1]
                err = 1.0 / np.sqrt(self.mergall_acc[i, 1])
                f.write(f"{i * self.ttstep:.6f} {val:.6f} {err:.6f}\n")
            
    def read_acal(self,fn_acal):
        
        with open(fn_acal, 'r') as file:
            for line in file:
                rl = line.strip()
                if not rl:
                    continue
            
                parts = rl.split()
                a1, jm, a2, cen, a3, xx, a4, kon, a5, xxx, a6, off, a7, xxxx = parts[:14]
            
                jm = int(jm)
                cen, xx, kon, xxx, off, xxxx = map(float, [cen, xx, kon, xxx, off, xxxx])
            
                skon = np.sign(kon)
                self.angcal_SIGN[jm] = int(np.round(skon))
                kon = abs(kon)
                koni = 1.0 / kon
                ceko = cen * kon
            
                self.angcal_DG[:, jm] = [cen, kon, off]
                self.angcal_EE[:, jm] = [cen * self.pitch, self.pitch * koni, off + self.rad_to_deg * ceko]
                self.angcal_BC[:, jm] = [
                    np.arctan(ceko),
                    self.pitch * np.sqrt(1.0 + ceko**2) * koni,
                    off + self.rad_to_deg * (ceko - np.arctan(ceko - kon * self.hwmc))
                ]
    
        
  
    def read_bad(self,fn_bad):
        
        with open(fn_bad, 'r') as file:
            for line in file:
                rl = line.strip()
                if not rl:
                    continue
                if '-' in rl:
                    i1, i2 = map(int, rl.split('-'))
                    self.isbad[i1:i2+1] = 1
                else:
                    i1 = int(rl)
                    self.isbad[i1] = 1
    
    def bin_one(self,i_img):
        i_img=0
        dowrite=0
        fnwr='dummy.dat'
        position_det=self.tt_angle_det

        print(position_det)
        scalmon_1s = self.mon_rate / self.I0_mon
        add_angle = self.BLOFFSET + position_det + self.dtt0
        for jpx in range(self.Dimdet):
            if self.isbad[jpx] == 1:
                continue
            mm = jpx //self. Dimmod
            if self.mod_enabled[mm] == 0:
                continue
            smm = self.angcal_SIGN[mm]
            jj = jpx - mm * self.Dimmod
            j = Dimmod1 - jj if smm == -1 else jj
            #print(self.chread.shape)
            Yval = self.chread[jpx, i_img]
            Sval = np.sqrt(Yval) * self.ff_corr[jpx] * scalmon_1s
            Yval *= self.ff_corr[jpx] * scalmon_1s
        
            pr1 = self.angcal_DG[0, mm] * self.angcal_DG[1, mm]
            pr2 = j * self.angcal_DG[1, mm]
            dpr2 = 0.5 * self.angcal_DG[1, mm]
            ang0 = self.angcal_DG[2, mm] + self.rad_to_deg * (pr1 - np.arctan(pr1 - pr2)) + add_angle
        
            if ang0 < self.ttmin or ang0 > self.ttmax:
                continue
        
            angw = self.rad_to_deg * abs(np.arctan(pr1 + dpr2 - pr2) - np.arctan(pr1 - dpr2 - pr2))
            exa = ang0 + 0.5 * np.array([-angw, angw])
            crate = self.ttstep * Yval / angw
            e_crate = self.ttstep * Sval / angw
            w_crate = 1.0 / (e_crate ** 2)
        
            nx1 = max(self.ntt1, int(np.floor(exa[0] / self.ttstep) - 1))
            nx2 = min(self.ntt2, int(np.ceil(exa[1] / self.ttstep) + 1))
            #print(nx1,nx2)
            if nx1 > nx2:
                continue
            #print(position_det, ang0, nx1,nx2,exa[0]/ self.ttstep,exa[1]/ self.ttstep)
            for nx in range(nx1, nx2 + 1):
                ovl = [max(exa[0], (nx - 0.5) * self.ttstep), min(exa[1], (nx + 0.5) * self.ttstep)]
                delt = ovl[1] - ovl[0]
                if delt < 0.0001:
                    continue
                beta = delt / self.ttstep
            
                self.binone_acc[nx-self.ntt1, 0] += 1
                self.binone_acc[nx-self.ntt1, 1] += w_crate * beta
                self.binone_acc[nx-self.ntt1, 2] += w_crate * crate * beta
                self.binone_acc[nx-self.ntt1, 3] += w_crate * crate**2 * beta
    
            mask = self.binone_acc[:, 0] > 0.1
            self.out_one[mask, 0] = self.binone_acc[mask, 2] / self.binone_acc[mask, 1]
            self.out_one[mask, 1] = 1.0 / np.sqrt(self.binone_acc[mask, 2])
    
            if dowrite:
                np.savetxt(fnwr, np.column_stack((np.arange(self.ntt1-self.ntt1, self.ntt2 + 1-self.ntt1) * self.ttstep, self.out_one[ntt1-self.ntt1:ntt2+1-self.ntt1])))
