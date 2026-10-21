"""find_target_vtrim and find_trimbits: the vectorised versions must give
the results of the original per-channel loops, which are kept here as the
reference."""
import io
import contextlib
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("slsdet")
ROOT = Path(__file__).resolve().parents[1]
for sub in ("", "patterntools", "analysis", "detector", "plotting", "trimming"):
    sys.path.insert(0, str(ROOT / sub))
import trimming  # noqa: E402


def quiet(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*a, **k)


def loop_find_target_vtrim(data, smin, smax, counts, chanmask, nSigma=5):
    """Original implementation (loops), returning flex per channel as well."""
    sstep = (smax - smin) / (data.shape[0] - 1)
    vtrim = np.arange(smin, smax + sstep, sstep)
    inds = np.arange(0, vtrim.shape[0])
    if sstep > 0 and trimming.get_sign():
        inds = np.flip(inds, 0)
    if sstep < 0 and trimming.get_sign() is False:
        inds = np.flip(inds, 0)
    flex = np.ndarray(data.shape[1], dtype=np.float64)
    for ich in np.arange(0, data.shape[1]):
        flex[ich] = 0
        val = data[:, ich]
        for itrim in inds:
            flex[ich] = vtrim[itrim]
            if val[itrim] > counts[ich]:
                break
    vtrim0 = 800 if trimming.get_sign() else 1500
    for ich in chanmask:
        counts[ich] = 0
    vv = flex[np.where(counts > 0)]
    if len(vv) > 0:
        meanf = np.median(vv)
        sigmaf = np.sqrt(np.var(vv))
        vtrim0 = meanf - nSigma * sigmaf
    try:
        vtrim0 = max(vtrim0, min(vv))
    except Exception:
        pass
    if len(counts[counts == 0]) > 0:
        counts[counts == 0] = np.median(counts[counts > 0])
    return vtrim0


def loop_find_trimbits(data, counts, smin=0, smax=63):
    sstep = (smax - smin) / (data.shape[0] - 1)
    trims = np.arange(smin, smax + sstep, sstep)
    inds = np.arange(0, trims.shape[0])
    if trimming.get_sign() is False:
        inds = np.flip(inds, 0)
    tb = np.empty(data.shape[1], dtype=np.int32)
    for ich in np.arange(0, data.shape[1]):
        tb[ich] = 0
        val = data[:, ich]
        for itrim in inds:
            tb[ich] = trims[itrim]
            if val[itrim] > counts[ich] - np.sqrt(counts[ich]):
                if itrim < trims.shape[0] - 1:
                    if val[itrim + 1] > counts[ich] - np.sqrt(counts[ich]):
                        break
                else:
                    break
        tb[ich] = min(max(tb[ich], 0), 63)
    return tb


@pytest.fixture(autouse=True)
def reset_sign():
    trimming.set_sign(True)
    yield
    trimming.set_sign(True)


def synthetic_scan(nrow, nch, seed):
    """Noisy S-curves with a few pathological channels: never crossing,
    crossing only at the last step, crossing at the first step, flat."""
    rng = np.random.default_rng(seed)
    x = np.arange(nrow)[:, None]
    mid = rng.uniform(0.2, 0.8, nch) * nrow
    data = rng.poisson(1500 / (1 + np.exp(-(x - mid) / 3.0)) + 20).astype(np.int32)
    counts = np.full(nch, 750, dtype=np.int32)
    data[:, 0] = 10                      # never crosses
    data[:, 1] = 10; data[-1, 1] = 5000  # crosses at the last index only
    data[:, 2] = 5000                    # crosses immediately
    data[:, 3] = 760                     # hovers just above the target
    counts[4] = 0                        # zero target
    return data, counts


@pytest.mark.parametrize("sign", [True, False])
@pytest.mark.parametrize("smin,smax", [(0, 2800), (2800, 0)])
def test_find_target_vtrim_matches_loop(sign, smin, smax):
    trimming.set_sign(sign)
    data, counts = synthetic_scan(141, 50, 1)
    c_loop, c_new = counts.copy(), counts.copy()
    ref = loop_find_target_vtrim(data, smin, smax, c_loop, [7, 8], 3)
    new = quiet(trimming.find_target_vtrim, data, smin, smax, c_new, [7, 8], 3)
    assert new == ref
    np.testing.assert_array_equal(c_new, c_loop)   # masked channels zeroed, then filled with the median


@pytest.mark.parametrize("sign", [True, False])
def test_find_trimbits_matches_loop(sign):
    trimming.set_sign(sign)
    data, counts = synthetic_scan(64, 50, 2)
    ref = loop_find_trimbits(data, counts, 0, 63)
    new = quiet(trimming.find_trimbits, data, counts, 0, 63)
    np.testing.assert_array_equal(new, ref)
    assert new.dtype == np.int32 and new.min() >= 0 and new.max() <= 63


def test_real_scans_match_stored_loop_results():
    ref = np.load(ROOT / "tests" / "data" / "mythen3_trim_scans.npz")
    counts = ref["counts"].copy()
    vtrim0 = quiet(trimming.find_target_vtrim, ref["vt_scan"], 0, 2800, counts, list(ref["chanmask"]), 3)
    assert vtrim0 == pytest.approx(float(ref["vtrim0"]), abs=1e-9)
    np.testing.assert_array_equal(counts, ref["counts_after_vtrim"])
    tb = quiet(trimming.find_trimbits, ref["tb_scan"], counts, 0, 63)
    np.testing.assert_array_equal(tb, ref["tb"])


def test_pool_helper_still_available():
    assert callable(trimming.find_target_threshold_pool)


def test_find_target_threshold_returns_inflection_points():
    ref = np.load(ROOT / "tests" / "data" / "mythen3_thrscan_lmfit.npz")
    thr0, counts, fit = quiet(trimming.find_target_threshold, ref["data"], 1400, 900, 3000, 1500, [3], 3, None)
    flex = fit["flex"]
    assert fit.dtype == trimming.fsc.FIT_DTYPE
    assert flex.shape == (1280,) and flex[3] == 0 and (flex[ref["flex"] > 0] > 0).sum() >= 1245
    assert (fit["hi"][flex > 0] == 1400).all() and (fit["lo"][flex > 0] >= 900).all()
    assert 1200 < thr0 < 1300
    assert len(quiet(trimming.find_target_threshold_pool, [ref["data"], 1400, 900, 3000, 1500, 3, None, []])) == 2
