import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent, MouseButton, MouseEvent
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plotting"))
import plot_scan as psc  # noqa: E402

SMIN, SMAX, SSTEP = 800, 1300, 10
NROW = (SMAX - SMIN) // SSTEP + 1
NCOL = 2 * 1280


@pytest.fixture
def data():
    rng = np.random.default_rng(0)
    thr = np.arange(SMIN, SMAX + SSTEP, SSTEP, dtype=float)
    mid = rng.normal(1050, 30, NCOL)
    d = 5000 * 0.5 * (1 - np.tanh((thr[:, None] - mid[None, :]) / 20.0))
    return rng.poisson(d).astype(np.int32)


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def click(viewer, ax, xd, yd):
    cv = viewer.fig.canvas
    x, y = ax.transData.transform((xd, yd))
    cv.callbacks.process("button_press_event",
                         MouseEvent("button_press_event", cv, x, y, button=MouseButton.LEFT))


def scroll(viewer, ax, xd, yd, step):
    cv = viewer.fig.canvas
    x, y = ax.transData.transform((xd, yd))
    cv.callbacks.process("scroll_event", MouseEvent("scroll_event", cv, x, y, step=step))


def key(viewer, k):
    cv = viewer.fig.canvas
    cv.callbacks.process("key_press_event", KeyEvent("key_press_event", cv, k))


def test_axes_follow_the_scan(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    assert v.thr[0] == SMIN and v.thr[-1] == SMAX and len(v.thr) == NROW
    assert v.ax.get_xlim() == (-0.5, NCOL - 0.5)
    assert v.ax.get_ylim() == (SMIN - SSTEP / 2, SMAX + SSTEP / 2)
    assert v.axc.get_xlim() == (0, v.vmax) and v.axt.get_ylim() == (0, v.vmax)
    assert v.im.get_clim() == (0, v.vmax)


def test_viewer_keeps_its_own_copy(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    v.update_row(0, np.zeros(NCOL), draw=False)
    assert data[0].any()


def test_click_on_image_selects_channel_and_step(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    click(v, v.ax, 1234.4, 1104)
    assert (v.channel, v.row) == (1234, 30)
    assert v.thr[v.row] == 1100
    assert v._readout.get_text() == f"channel 1234    threshold 1100    counts {data[30, 1234]}"
    np.testing.assert_array_equal(v._line_c.get_xdata(), data[:, 1234])
    ys = v._line_t.get_ydata()   # envelope: the panel is narrower than 2560 channels
    assert ys.min() == data[30].min() and ys.max() == data[30].max()
    v.ax.set_xlim(1200, 1300)
    np.testing.assert_array_equal(v._line_t.get_ydata(), data[30])


def test_click_on_side_panels_changes_one_coordinate(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    ch, row = v.channel, v.row
    click(v, v.axt, 77, 100)
    assert (v.channel, v.row) == (77, row)
    click(v, v.axc, 100, 996)
    assert (v.channel, v.row) == (77, 20)


def test_click_is_ignored_while_toolbar_zooms(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    ch, row = v.channel, v.row
    v.fig.canvas.widgetlock(object())
    click(v, v.ax, 10, 900)
    assert (v.channel, v.row) == (ch, row)


def test_arrow_keys_move_and_clip(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    v.select(channel=5, row=3, draw=False)
    key(v, "right")
    key(v, "shift+up")
    assert (v.channel, v.row) == (6, 13)
    for _ in range(3):
        key(v, "shift+left")
    key(v, "down")
    assert (v.channel, v.row) == (0, 12)
    v.select(channel=NCOL - 1, row=NROW - 1, draw=False)
    key(v, "right")
    key(v, "up")
    assert (v.channel, v.row) == (NCOL - 1, NROW - 1)


def test_viewer_keys_are_removed_from_default_bindings(data):
    psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    assert "left" not in matplotlib.rcParams["keymap.back"]
    assert "right" not in matplotlib.rcParams["keymap.forward"]
    assert "l" not in matplotlib.rcParams["keymap.yscale"]
    assert "c" in matplotlib.rcParams["keymap.back"]


def test_log_scale_applies_everywhere(data):
    from matplotlib.colors import Normalize, SymLogNorm
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP, vmax=3000)
    assert not v.log and not v._check.get_status()[0]
    v._check.set_active(0)          # click the checkbox
    assert v.log and isinstance(v.im.norm, SymLogNorm)
    assert v.axc.get_xscale() == "symlog" and v.axt.get_yscale() == "symlog"
    assert v.axc.get_xlim() == (0, 3000) and v.axt.get_ylim() == (0, 3000)
    assert v.im.get_clim() == (0, 3000)
    scroll(v, v.ax, 100, 1000, +1)   # colour limits still follow
    assert v.im.get_clim() == (0, pytest.approx(2000))
    key(v, "l")                      # toggle back, checkbox follows
    assert not v.log and isinstance(v.im.norm, Normalize) and not v._check.get_status()[0]
    assert v.axc.get_xscale() == "linear"
    assert psc.ThrScanViewer(data, SMIN, SMAX, SSTEP, log=True)._check.get_status()[0]


def test_scroll_on_image_changes_colour_limits_and_panels(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP, vmax=3000)
    scroll(v, v.ax, 100, 1000, +1)
    assert v.vmax == pytest.approx(2000)
    assert v.im.get_clim() == (0, v.vmax)
    assert v.axc.get_xlim() == (0, v.vmax) and v.axt.get_ylim() == (0, v.vmax)
    scroll(v, v.cax, 0.5, 0.5, -1)
    assert v.vmax == pytest.approx(3000)


def test_scroll_on_panels_zooms_shared_axes(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    scroll(v, v.axt, 1000, 100, +1)
    lo, hi = v.ax.get_xlim()
    assert -0.5 < lo < 1000 < hi < NCOL - 0.5
    assert v.axt.get_xlim() == (lo, hi)
    scroll(v, v.axc, 100, 1000, +1)
    lo, hi = v.ax.get_ylim()
    assert SMIN < lo < 1000 < hi < SMAX
    assert v.axc.get_ylim() == (lo, hi)
    for _ in range(10):
        scroll(v, v.axt, 1000, 100, -1)
    assert v.ax.get_xlim() == (-0.5, NCOL - 0.5)


def test_fit_panels_and_reset(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP, vmax=100)
    v.select(row=0, draw=False)
    key(v, "a")
    assert v.axt.get_ylim()[1] > 4000
    key(v, "A")
    assert v.axt.get_ylim() == (0, 100)


def test_descending_scan_is_shown_ascending(data):
    v = psc.ThrScanViewer(data, SMAX, SMIN, -SSTEP)
    assert v.thr[0] == SMIN and v.thr[-1] == SMAX
    np.testing.assert_array_equal(v.data[-1], data[0])
    v.update_row(0, np.full(NCOL, 7), draw=False)
    assert (v.data[-1] == 7).all() and not (v.data[0] == 7).any()
    v.select(threshold=SMAX, draw=False)
    assert v.row == NROW - 1


def test_float_step(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, (SMAX - SMIN) / (NROW - 1))
    assert v.thr[-1] == pytest.approx(SMAX)


def test_wide_scan_curve_is_reduced_to_an_envelope():
    rng = np.random.default_rng(1)
    wide = rng.integers(0, 5000, (5, 40000)).astype(np.int32)
    wide[2, 12345] = 60000
    v = psc.ThrScanViewer(wide, 0, 4, 1)
    v.select(row=2, draw=False)
    xs, ys = v._line_t.get_data()
    assert len(xs) < 4000
    assert ys.max() == 60000 and ys.min() == wide[2].min()
    v.ax.set_xlim(12000, 12700)
    xs, ys = v._line_t.get_data()
    np.testing.assert_array_equal(ys, wide[2])


def test_update_row_and_set_data(data):
    v = psc.ThrScanViewer(data, SMIN, SMAX, SSTEP)
    v.select(channel=3, row=4, draw=False)
    v.update_row(4, np.full(NCOL, 42), draw=False)
    assert v._readout.get_text().endswith("counts 42")
    assert v.im.get_array()[4, 0] == 42
    v.set_data(np.zeros_like(data))
    assert not v.im.get_array().any()
    with pytest.raises(ValueError):
        v.set_data(np.zeros((2, 2)))


def test_bad_input():
    with pytest.raises(ValueError):
        psc.ThrScanViewer(np.zeros(10), 0, 9, 1)
    with pytest.raises(ValueError):
        psc.ThrScanViewer(np.zeros((3, 4)), 0, 2, 0)


def test_wrappers_keep_their_signatures(data):
    v = psc.plot_thrscan(data, SMIN, SMAX, SSTEP)
    assert isinstance(v, psc.ThrScanViewer)
    fig, ax = psc.plot_simple_thrscan(data, np.arange(SMIN, SMAX + SSTEP, SSTEP))
    assert ax.get_ylim() == (SMIN - SSTEP / 2, SMAX + SSTEP / 2)
    fig, ax = psc.plot_simple_thrscan(data, np.arange(SMAX, SMIN - SSTEP, -SSTEP))
    assert ax.get_ylim() == (SMIN - SSTEP / 2, SMAX + SSTEP / 2)


def test_threshold_dispersion_histograms():
    rng = np.random.default_rng(0)
    before = rng.normal(1190, 40, 1280)
    after = rng.normal(1250, 4, 1280)
    before[:20] = 0                       # unfitted channels are skipped
    fig, ax = psc.plot_threshold_dispersion(before, after)
    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert labels[0].startswith("before trimming") and "1260 ch" in labels[0]
    assert labels[1].startswith("after trimming") and "1280 ch" in labels[1]
    steps = [p.get_data() for p in ax.patches]
    assert len(steps) == 2
    assert all(np.allclose(s.edges % 2, 0) for s in steps)          # 2 DAC bins on a common grid
    assert [int(s.values.sum()) for s in steps] == [1260, 1280]      # every fitted channel is in a bin
    assert np.array_equal(steps[0].edges, steps[1].edges)
    fig, ax = psc.plot_threshold_dispersion(np.zeros(10), after)   # nothing fitted before
    assert "no fitted channels" in ax.get_legend().get_texts()[0].get_text()


def test_histogram_helper():
    h = psc.histogram([0.5, 1.5, 1.7, 10.0], 0, 4, 1)
    np.testing.assert_array_equal(h.values(), [1, 2, 0, 0])
    np.testing.assert_array_equal(h.axes[0].edges, [0, 1, 2, 3, 4])
    h = psc.histogram([3.0], 0, 7, 2)                       # range rounded up to whole bins
    np.testing.assert_array_equal(h.axes[0].edges, [0, 2, 4, 6, 8])
    fig, ax = plt.subplots()
    patch = psc.plot_histogram(ax, h, label="x")
    assert ax.get_legend_handles_labels()[1] == ["x"] and patch.get_data().values.sum() == 1
