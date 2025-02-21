import numpy as np
from My3AngConvSlim import My3AngConvSlim

class SlimMain:
    def __init__(self):
        self.converter = My3AngConvSlim()
        self.converter.dtt0 = 0.0
        self.writeraw = False
        self.writeone = True
        
    def run(self):
        self.converter.check_unconnected()
        
        fn_bad = 'TDATA/bc2023_003_RING.chans'
        self.converter.read_bad(fn_bad)
        
        fn_acal = 'TDATA/Angcal_2E_Feb2023_P29.off'
        self.converter.read_acal(fn_acal)
        
        fn_ff = 'TDATA/Flatfield_E22p0keV_T11000eV_up_48M_a_LONG_Feb2023_open_WS_SUMC.raw'
        self.converter.read_ff(fn_ff)
        
        self.converter.prep_merge()
        
        kh5 = 0
        with open('TDATA/list_h5.txt', 'r') as f:
            for rl in f:
                rl = rl.strip()
                if not rl:
                    continue
                
                fn_h5 = 'TDATA/'+rl
                kh5 += 1
                I0, THdet, exptime = self.converter.read_h5raw(fn_h5)
                
                if self.writeraw:
                    with open(f"{fn_h5}.raw", 'w') as f_raw:
                        f_raw.write(f"# {I0} {THdet} {exptime}\n")
                        for i in range(self.converter.Dimdet1 + 1):
                            if self.converter.isbad[i] == 1:
                                continue
                            f_raw.write(f"{i} {self.converter.chread[i, :]}\n")
                
                self.converter.I0_mon = I0
                self.converter.exptime_s = exptime
                self.converter.tt_angle_det = THdet
                
                if kh5 == 1:
                    self.converter.mon_rate = self.converter.I0_mon / self.converter.exptime_s
                
                self.converter.bin_one(0)
            self.converter.merge_it()
            self.converter.output('TDATA/out.xye')

if __name__ == "__main__":
    app = SlimMain()
    app.run()
