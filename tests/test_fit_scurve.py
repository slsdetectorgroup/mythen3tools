import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.special import erf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
import fit_scurve as fsc  # noqa: E402

THR_DESC = np.arange(1400, 900 - 5, -5)
THR_ASC = THR_DESC[::-1]


def model(thr, flex, noise, A, cs, sgn):
    s = 1 if sgn else -1
    th = thr[:, None]
    return 0.5 * A * (1 + erf(s * (flex - th) / (noise * np.sqrt(2)))) * (1 + s * cs * (flex - th))


def synthetic(thr, sgn, nch=60, seed=0, poisson=False):
    """Scan with a noise explosion at the plateau end, five dead channels and
    one hot channel in front of nch good ones."""
    rng = np.random.default_rng(seed)
    flex = rng.normal(1180, 40, nch)
    noise = rng.normal(40, 5, nch)
    A = rng.normal(2500, 300, nch)
    cs = rng.normal(0.004, 0.001, nch).clip(0.0005)
    y = model(thr, flex, noise, A, cs, sgn)
    edge = 920 if sgn else 1380
    y = y + 3e5 * np.exp(-np.abs(thr[:, None] - edge) / 1.5)   # steep, so the fitted range is clean
    if poisson:
        y = rng.poisson(np.clip(y, 0, None))
    y = np.rint(y).astype(np.int32)
    dead = np.zeros((len(thr), 5), np.int32)
    hot = np.full((len(thr), 1), 50000, np.int32)
    return np.hstack([dead, hot, y]), flex, noise, A, cs


@pytest.fixture(autouse=True)
def reset_sign():
    fsc.sign = True
    yield
    fsc.sign = True


@pytest.mark.parametrize("thr,sgn", [(THR_DESC, True), (THR_ASC, True), (THR_DESC, False), (THR_ASC, False)])
def test_recovers_parameters_and_rejects_bad_channels(thr, sgn):
    data, flex, noise, A, cs = synthetic(thr, sgn)
    fsc.sign = sgn
    fsc.init_params(1500, 3000)
    f, n, a, c, counts = fsc.fit_all(thr, data, [])
    assert not f[:6].any(), "dead and hot channels must be rejected"
    good = f[6:] > 0
    assert good.all()
    assert np.abs(f[6:] - flex).max() < 0.2
    assert np.abs(n[6:] - noise).max() < 0.2
    assert np.abs(a[6:] - A).max() / A.mean() < 5e-3
    assert np.abs(c[6:] - cs).max() < 5e-5
    np.testing.assert_allclose(counts[6:], a[6:] / 2)


def test_chanmask_zeroes_channels():
    data, flex, *_ = synthetic(THR_DESC, True)
    fsc.init_params(1500, 3000)
    f, *_ = fsc.fit_all(THR_DESC, data, [7, 8])
    assert f[7] == 0 and f[8] == 0 and f[9] > 0


def test_fit_range_cuts_before_the_noise():
    data, *_ = synthetic(THR_DESC, True)
    valid = fsc.fit_range(THR_DESC, data, 6000)
    ch = 10
    first_bad = np.flatnonzero(data[:, ch] > 6000)[0]
    assert valid[:first_bad - 3, ch].all()
    assert not valid[first_bad - 1:, ch].any()
    assert not valid[-1].any()


def test_single_channel_result_api():
    data, flex, *_ = synthetic(THR_DESC, True)
    params = fsc.init_params(1500, 3000)
    r = fsc.fit_scurve(THR_DESC, data[:, 6], params)
    assert r.success
    assert abs(r.params["flex"].value - flex[0]) < 0.1
    assert r.best_fit.shape == THR_DESC.shape and r.init_fit.shape == THR_DESC.shape
    bad = fsc.fit_scurve(THR_DESC, data[:, 0], params)
    assert not bad.success and bad.params["flex"].value == 0


def test_fixed_amplitude_and_chargesharing():
    thr = THR_DESC
    y = np.rint(model(thr, np.array([1150.0]), np.array([30.0]), np.array([2000.0]), np.array([0.0]), True)).astype(np.int32)
    fsc.init_params(1500, 2000)
    fsc.init_fix_cs(0)
    fsc.init_fix_ampl(2000)
    f, n, a, c, counts = fsc.fit_all(thr, y)
    assert abs(f[0] - 1150) < 0.1 and abs(n[0] - 30) < 0.1 and a[0] == 2000 and c[0] == 0


def test_linear_fit():
    x = np.array([5.0, 8.0, 12.0, 17.0])
    r = fsc.linear_fit(x, 3.0 + 2.5 * x)
    assert abs(r.params["slope"].value - 2.5) < 1e-9
    assert abs(r.params["intercept"].value - 3.0) < 1e-9


def test_matches_lmfit_on_a_real_scan():
    ref = np.load(ROOT / "tests" / "data" / "mythen3_thrscan_lmfit.npz")
    fsc.init_params(1500, 3000)
    flex, noise, ampl, cs, counts = fsc.fit_all(ref["thr"], ref["data"], [])
    rejected_old = ref["flex"] == 0
    np.testing.assert_array_equal(flex == 0, rejected_old)
    assert rejected_old.sum() == 34
    ok = ~rejected_old
    assert np.abs(flex - ref["flex"])[ok].max() < 0.01
    assert np.abs(noise - ref["noise"])[ok].max() < 0.01
    assert np.abs(ampl - ref["ampl"])[ok].max() < 0.5
    assert np.abs(cs - ref["cs"])[ok].max() < 1e-5
    assert np.abs(counts - ref["counts"])[ok].max() < 0.25
