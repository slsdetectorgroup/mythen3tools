"""S-curve fits of Mythen3 threshold scans with aare.

The model is the one used before with lmfit,

    y(th) = A/2 * (1 + erf(s*(flex - th) / (noise*sqrt(2)))) * (1 + s*cs*(flex - th))

with s = +1 (``sign`` True, counts fall with rising threshold) or -1. It is
aare's FallingScurve / RisingScurve with the baseline p0, p1 fixed at zero,
mu = flex, sigma = noise, A = amplitude and C = -s*A*cs.

All channels of a scan are fitted in one multi-threaded call with aare's
variable-projection solver (about 30 ms for 1280 channels, 100 steps). The
fit range of each channel is chosen as before: from the baseline end of the
scan up to 10 DAC before the counts exceed twice the expected plateau, which
cuts off the noise. A channel is rejected when the fit fails or a parameter
ends on a limit, which is what the lmfit version did.

Module state set by ``init_params`` and ``init_fix_*`` is used by
``fit_all`` and ``fit_scurve`` exactly as before.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
from scipy.signal import argrelextrema
import aare
import read_mythen as my3

sign = True
n_threads = min(8, os.cpu_count() or 1)
minimizer = aare.Minimizer.VarPro
max_calls = 100

# fit configuration set by init_params / init_fix_cs / init_fix_ampl
_cfg = {"flex0": 1300.0, "ampl0": 3000.0, "noise0": 20.0, "cs0": 0.0005,
        "fix_cs": None, "fix_ampl": None}

NOISE_LIMITS = (5.0, 200.0)
FLEX_LIMITS = (200.0, 2800.0)


def scurve(th, pedestal, pedslope, flex, noise, amplitude, chargesharing):
    s = 1 if sign else -1
    return (0.5 * amplitude * (1 + erf(s * (flex - th) / (noise * np.sqrt(2))))
            * (1 + s * chargesharing * (flex - th)) + pedestal - pedslope * th * s)


def scurve_fit(x, pedestal, pedslope, flex, noise, amplitude, chargesharing):
    return scurve(np.asarray(x, dtype=float), pedestal, pedslope, flex, noise, amplitude, chargesharing)


def init_params(flex0, ampl0):
    """Expected inflection point and plateau; the plateau sets the amplitude
    limits (0.1 to 2 times) and the noise cut (2 times)."""
    _cfg["flex0"] = float(flex0)
    _cfg["ampl0"] = float(max(ampl0, 100))
    _cfg["fix_cs"] = None
    _cfg["fix_ampl"] = None
    return dict(_cfg)


def init_fix_cs(val):
    _cfg["fix_cs"] = float(val)


def init_fix_ampl(val):
    _cfg["fix_ampl"] = float(val)


class FitResult:
    """Result of a single-channel fit, with the attributes the scripts use:
    ``success``, ``params[name].value`` (flex, noise, amplitude,
    chargesharing, pedestal, pedslope), ``best_fit`` and ``init_fit``
    evaluated on the scan thresholds in their original order."""

    class _Par:
        def __init__(self, value):
            self.value = value

    def __init__(self, thresholds, flex, noise, ampl, cs, success):
        self.success = bool(success)
        self.params = {"pedestal": self._Par(0.0), "pedslope": self._Par(0.0),
                       "flex": self._Par(flex), "noise": self._Par(noise),
                       "amplitude": self._Par(ampl), "chargesharing": self._Par(cs)}
        th = np.asarray(thresholds, dtype=float)
        self.best_fit = scurve(th, 0, 0, flex, noise, ampl, cs) if self.success else np.zeros_like(th)
        self.init_fit = self.best_fit


def fit_range(thresholds, data, cmax):
    """Boolean mask (nsteps, nchan) of the points fitted per channel.

    Walking from the baseline end of the scan (high threshold for
    ``sign`` True, low for False) the range ends 10 DAC before the first
    point whose counts exceed ``cmax``; the point at the end of the walk is
    left out as well. This reproduces the range of the lmfit version."""
    thr = np.asarray(thresholds, dtype=float)
    data = np.asarray(data)
    n, nch = data.shape
    descending = thr[0] > thr[-1]
    from_start = (sign and descending) or (not sign and not descending)
    exceed = data > cmax
    valid = np.zeros((n, nch), dtype=bool)
    if from_start:
        stop = np.where(exceed.any(0), exceed.argmax(0), n - 1)
        for ich in range(nch):
            i = stop[ich]
            if data[i, ich] >= cmax:
                keep = (thr > thr[i] + 10) if sign else (thr < thr[i] - 10)
                idx = np.flatnonzero(keep)
                i = idx[-1] if len(idx) else -1
            else:
                i = n - 1
            while i <= 6 and i < n - 1:        # too few points: extend
                i += 1
            valid[:i, ich] = True
    else:
        rev = exceed[::-1]
        stop = np.where(rev.any(0), n - 1 - rev.argmax(0), 0)
        for ich in range(nch):
            i = stop[ich]
            if data[i, ich] >= cmax:
                keep = (thr > thr[i] + 10) if sign else (thr < thr[i] - 10)
                idx = np.flatnonzero(keep)
                i = idx[0] if len(idx) else 0
            else:
                i = 0
            while (n - 1) - i <= 6 and i > 0:
                i -= 1
            valid[i:n - 1, ich] = True
    return valid


def _model():
    cfg = _cfg
    ampl0 = cfg["ampl0"]
    m = (aare.FallingScurve if sign else aare.RisingScurve)(
        minimizer=minimizer, max_calls=max_calls, compute_errors=True)
    m.FixParameter("p0", 0.0)
    m.FixParameter("p1", 0.0)
    m.SetParLimits("sigma", *NOISE_LIMITS)
    m.SetParameter("sigma", cfg["noise0"])
    if cfg["fix_ampl"] is not None:
        m.FixParameter("A", cfg["fix_ampl"])
    else:
        m.SetParLimits("A", 0.1 * ampl0, 2 * ampl0)
    if cfg["fix_cs"] is not None:
        # C = -s*A*cs; only cs = 0 is exact for a free amplitude
        aref = cfg["fix_ampl"] if cfg["fix_ampl"] is not None else ampl0
        m.FixParameter("C", -aref * cfg["fix_cs"] if sign else aref * cfg["fix_cs"])
    elif sign:
        m.SetParLimits("C", -2 * ampl0, 0.0)
    else:
        m.SetParLimits("C", 0.0, 2 * ampl0)
    return m


def fit_all(thresholds, data, chanmask=[]):
    """Fit every channel of ``data`` (nsteps, nchan).

    Returns flex, noise, ampl, cs, counts per channel, zero for channels in
    ``chanmask`` and for channels whose fit failed or ended on a limit.
    ``counts`` is the model value at the inflection point, A/2."""
    thr = np.asarray(thresholds, dtype=float)
    data = np.asarray(data)
    if data.ndim != 2 or data.shape[0] != len(thr):
        raise ValueError(f"data shape {data.shape} does not match {len(thr)} thresholds")
    n, nch = data.shape
    cfg = _cfg
    cmax = 2 * cfg["ampl0"]

    valid = fit_range(thr, data, cmax)
    order = np.argsort(thr)
    x = thr[order]
    y = np.ascontiguousarray(data[order].T, dtype=np.float64)        # (nchan, nsteps)
    y_err = np.ascontiguousarray(valid[order].T, dtype=np.float64)   # 1 fitted, 0 left out
    # The excluded points (the noise region) still feed aare's start-value
    # estimate, so clamp them to the nearest fitted value.
    for ich in range(nch):
        bad = y_err[ich] == 0
        if bad.any() and not bad.all():
            good = np.flatnonzero(~bad)
            y[ich, :good[0]] = y[ich, good[0]]
            y[ich, good[-1] + 1:] = y[ich, good[-1]]

    m = _model()
    m.SetParLimits("mu", max(x[0] - 10, FLEX_LIMITS[0]), min(x[-1] + 10, FLEX_LIMITS[1]))
    r = m.fit(x, y[None], y_err[None], n_threads=n_threads)
    par, err, chi2 = r["par"][0], r["par_err"][0], r["chi2"][0]
    mu, sigma, A, C = par[:, 2], par[:, 3], par[:, 4], par[:, 5]

    free = [i for i, name in enumerate(m.GetParNames()) if name not in ("p0", "p1")
            and not (name == "A" and cfg["fix_ampl"] is not None)
            and not (name == "C" and cfg["fix_cs"] is not None)]
    good = (chi2 > 0) & (A > 0) & ~(err[:, free] == 0).any(axis=1)
    if len(chanmask):
        good[np.asarray(list(chanmask), dtype=int)] = False

    flex = np.where(good, mu, 0.0)
    noise = np.where(good, sigma, 0.0)
    ampl = np.where(good, A, 0.0)
    cs = np.where(good, (-C if sign else C) / np.where(A != 0, A, 1), 0.0)
    counts = np.where(good, 0.5 * A, 0.0)
    print("Could not fit", int((~good).sum() - len(set(chanmask))), "channels")
    return flex, noise, ampl, cs, counts


def fit_scurve(x, y, params=None, e=None):
    """Fit one channel; returns a FitResult."""
    flex, noise, ampl, cs, counts = fit_all(x, np.asarray(y)[:, None])
    return FitResult(x, flex[0], noise[0], ampl[0], cs[0], flex[0] > 0)


def fit_file(fname, ncounters, dr, smin, smax, ff, aa):
    head, data = my3.read_my3_file(fname, ncounters, dr)
    if data.shape[0] > 1:
        sstep = (smax - smin) / (data.shape[0] - 1)
    else:
        return 0, 0, 0, 0
    thr = np.arange(smin, smax + sstep, sstep)
    init_params(ff, aa)

    dd = np.sum(data, axis=1) / data.shape[1]
    result = fit_scurve(thr, dd)
    mod_flex = result.params['flex'].value
    mod_noise = result.params['noise'].value
    mod_ampl = result.params['amplitude'].value
    mod_cs = result.params['chargesharing'].value
    mod_counts = scurve(mod_flex, 0, 0, mod_flex, mod_noise, mod_ampl, mod_cs)

    flex, noise, ampl, cs, counts = fit_all(thr, data)

    flex = np.append(flex, mod_flex)
    noise = np.append(noise, mod_noise)
    ampl = np.append(ampl, mod_ampl)
    cs = np.append(cs, mod_cs)
    counts = np.append(counts, mod_counts)
    return flex, noise, ampl, cs, counts


def save_scurve_fit_file(outFname, flex, noise, ampl, cs, counts):
    chans = np.arange(flex.shape[0])
    xxx = np.column_stack((chans, flex, noise, ampl, cs, counts))
    np.savetxt(outFname, xxx, fmt='%s', delimiter='\t', header='chan\t flex\t noise\t ampl\t cs\t counts', encoding=None)


def load_scurve_fit_file(inFname):
    chans, flex, noise, ampl, cs, counts = np.loadtxt(inFname, unpack=True, delimiter='\t')
    print(flex.shape)
    return flex, noise, ampl, cs, counts


def save_encal(outFname, gain, offset):
    chans = np.arange(gain.shape[0])
    xxx = np.column_stack((chans, gain, offset))
    np.savetxt(outFname, xxx, fmt='%s', delimiter='\t', header='chan\t gain\t offset', encoding=None)


def load_encal(inFname):
    gain, offset = np.loadtxt(inFname, unpack=True, delimiter='\t')
    return gain, offset


def plot_fit(thresholds, data, result, ax=None, fig=None):
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(thresholds[0:result.init_fit.shape[0]], result.best_fit, '-', label='best fit')
    ax.plot(thresholds, data, 'o')
    return fig, ax


class LinearResult:
    def __init__(self, intercept, slope):
        self.params = {"intercept": FitResult._Par(intercept), "slope": FitResult._Par(slope)}


def linear_fit(x, y):
    """Straight line through (x, y) with aare's Pol1; params slope and intercept."""
    m = aare.Pol1(minimizer=aare.Minimizer.VarPro)
    r = m.fit(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64))
    p0, p1 = r["par"]
    return LinearResult(p0, p1)


def encal_all(ens, flex):
    print("**", flex[0].shape)
    nch = flex[0].shape[0]
    nenergies = ens.shape[0]
    fl = np.zeros(shape=(nch, nenergies))
    for i in range(0, nenergies):
        d1 = flex[i]
        for ich in range(0, fl.shape[0]):
            fl[ich, i] = d1[ich]
    gain = np.empty(nch)
    offset = np.empty(nch)
    for ich in range(0, nch):
        result = linear_fit(ens, fl[ich])
        gain[ich] = result.params['slope'].value
        offset[ich] = result.params['intercept'].value
    return gain, offset


def find_start_param(data, smin, smax, sstep):

    if data.ndim > 1:
        dd = np.median(data, axis=1)
    else:
        dd = data
    thr = np.arange(smin, smax + sstep, sstep)
    thr1 = thr[1:]
    ns = int(len(thr1) / 20)
    sp = smooth(np.diff(dd), ns)
    lmax = argrelextrema(sp, np.greater)
    lmin = argrelextrema(sp, np.less)
    ll = lmin[0]
    LL = lmax[0]
    nn = len(LL)
    nn1 = len(ll)

    if nn > 0 and nn1 > 0:
        while nn > 3:
            lmax = argrelextrema(sp[LL], np.greater)
            nn = len(lmax[0])
            if nn > 0:
                LL = LL[lmax[0]]
            else:
                nn = len(LL)
                break

        while nn1 > 50:
            lmin = argrelextrema(sp[ll], np.less)
            nn1 = len(lmin[0])
            if nn1 > 0:
                ll = ll[lmin[0]]
            else:
                nn1 = len(ll)
                break

        if thr1[0] < thr1[1]:
            mm = ll[0]
            LL1 = LL[LL > mm]
        else:
            mm = ll[-1]
            LL1 = LL[LL < mm]

        if len(LL1) == 0:
            LL1 = LL

        vv = np.max(sp[LL1])
        aa = np.where(sp == vv)

        if thr1[0] < thr1[1]:
            MM = aa[0][-1]
        else:
            MM = aa[0][0]
        return thr1[mm], thr1[MM], dd[mm]

    return 0, 0, 0


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
