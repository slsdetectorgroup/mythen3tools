"""Interactive viewer for Mythen3 threshold scans.

A scan is a 2D array with one row per scan step (threshold, vtrim, trimbit
value, ...) and one column per channel. Channels come in blocks of 1280, one
block per counter and module, which is how ``thrScan.scan`` and
``read_mythen`` return them.

    v = plot_thrscan(data, smin, smax, sstep)

Mouse and keyboard on the figure:

    click             select the channel and step under the cursor (any panel)
    arrow keys        move the selection by one channel or one step
    shift + arrows    move by ten
    scroll on image   change the upper colour limit (up: more contrast)
    scroll on panel   zoom the channel or threshold range about the cursor
    a / A             fit the side panels to the selected curves / back to the colour limits
    l or checkbox     counts on a log scale (image, side panels and colour bar)
    toolbar           pan and zoom as usual, all panels follow

The arrow keys and l, k, L are taken away from matplotlib's default key
bindings when the first viewer is created (c, v and backspace still step
through the zoom history).

The viewer can be filled while a scan is running::

    v = ThrScanViewer(np.zeros((nsteps, nchan)), smin, smax, sstep)
    for i, row in enumerate(acquire()):
        v.update_row(i, row)
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.colors import Normalize, SymLogNorm
from matplotlib.widgets import CheckButtons

BLOCK = 1280  # channels per counter and module

_CURSOR = dict(color="C3", lw=0.8, alpha=0.9)
_CURVE = dict(color="C0", lw=1.0)


class _BlitManager:
    """Redraw only the animated artists on top of a cached background."""

    def __init__(self, canvas, artists):
        self.canvas = canvas
        self.artists = list(artists)
        self._bg = None
        for a in self.artists:
            a.set_animated(True)
        canvas.mpl_connect("draw_event", self._on_draw)

    def _on_draw(self, event):
        # A full draw just finished without the animated artists. Cache the
        # result and paint them on top so they show in the final image.
        self._bg = self.canvas.copy_from_bbox(self.canvas.figure.bbox)
        self._draw_artists()

    def _draw_artists(self):
        fig = self.canvas.figure
        for a in self.artists:
            fig.draw_artist(a)

    def update(self):
        canvas = self.canvas
        if self._bg is None or not canvas.supports_blit:
            canvas.draw_idle()
            return
        canvas.restore_region(self._bg)
        self._draw_artists()
        canvas.blit(canvas.figure.bbox)
        canvas.flush_events()


def _ascending(data, thr):
    """Return data and thresholds ordered by increasing threshold."""
    if len(thr) > 1 and thr[1] < thr[0]:
        return data[::-1], thr[::-1], True
    return data, thr, False


_TAKEN_KEYS = (("left", "keymap.back"), ("right", "keymap.forward"),
               ("l", "keymap.yscale"), ("k", "keymap.xscale"), ("L", "keymap.xscale"))


def _free_keys():
    """Unbind the keys the viewer uses from matplotlib's defaults."""
    for key, name in _TAKEN_KEYS:
        keys = matplotlib.rcParams[name]
        if key in keys:
            matplotlib.rcParams[name] = [k for k in keys if k != key]


class ThrScanViewer:
    """Scan image with a per-channel and a per-step panel.

    Parameters
    ----------
    data : (nsteps, nchannels) array
        One row per scan step. The viewer keeps its own copy.
    smin, smax, sstep : number
        Scan range as passed to ``scan``. The step values are derived from
        ``smin``, ``sstep`` and the number of rows, so ``smax`` only documents
        the call. A negative ``sstep`` is shown with the axis ascending.
    vmax : number, optional
        Upper colour limit. Default: the 99th percentile of the data.
    cmap : str
        Colour map, a sequential one. Default ``viridis``.
    block : int
        Channels per block; thin separators are drawn between blocks.
    ylabel : str
        Name of the scanned quantity for the axis and readout.
    title : str, optional
        Figure title.
    log : bool
        Start with counts on a log scale.
    """

    def __init__(self, data, smin, smax, sstep, *, vmax=None, cmap="viridis",
                 block=BLOCK, figsize=(8, 7), ylabel="Threshold", title=None,
                 log=False):
        data = np.asarray(data)
        if data.ndim != 2:
            raise ValueError(f"expected a 2D array (steps, channels), got shape {data.shape}")
        if sstep == 0:
            raise ValueError("sstep must be non-zero")
        nrow, ncol = data.shape
        thr = float(smin) + float(sstep) * np.arange(nrow)
        data, thr, self._flip = _ascending(data, thr)
        self.data = np.array(data)
        self.thr = thr
        self.step = abs(float(sstep))
        self.nrow, self.ncol = nrow, ncol
        self.chans = np.arange(ncol)
        self.ylabel = ylabel
        self.channel = ncol // 2
        self.row = nrow // 2
        self.vmin = 0.0
        self.vmax = float(vmax) if vmax is not None else self._default_vmax()
        if self.vmax <= self.vmin:
            raise ValueError("vmax must be positive")

        _free_keys()
        self._build(cmap, block, figsize, title)
        self.log = False
        if log:
            self.set_log(True)
        self._refresh_selection()
        self.fig.canvas.draw()

    # ------------------------------------------------------------ building
    def _default_vmax(self):
        if self.data.size == 0:
            return 1.0
        v = float(np.percentile(self.data, 99))
        if v <= 0:
            v = float(self.data.max())
        return max(v, 1.0)

    def _build(self, cmap, block, figsize, title):
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(8, 8, hspace=0, wspace=0,
                              left=0.09, right=0.90, bottom=0.08, top=0.92)
        ax = fig.add_subplot(gs[:5, 3:])
        axc = fig.add_subplot(gs[:5, :3], sharey=ax)   # counts vs step, one channel
        axt = fig.add_subplot(gs[5:, 3:], sharex=ax)   # counts vs channel, one step
        cax = fig.add_subplot(gs[5:, 1])
        self.fig, self.ax, self.axc, self.axt, self.cax = fig, ax, axc, axt, cax

        half = self.step / 2
        self._xfull = (-0.5, self.ncol - 0.5)
        self._yfull = (self.thr[0] - half, self.thr[-1] + half)
        self.im = ax.imshow(self.data, aspect="auto", origin="lower", cmap=cmap,
                            extent=self._xfull + self._yfull,
                            vmin=self.vmin, vmax=self.vmax)
        ax.tick_params(labelbottom=False, labelleft=False)
        for b in range(block, self.ncol, block):
            ax.axvline(b - 0.5, color="w", lw=0.5, alpha=0.4)

        axc.xaxis.tick_top()
        axc.xaxis.set_label_position("top")
        axc.set_xlabel("Counts")
        axc.set_ylabel(self.ylabel)
        axt.yaxis.tick_right()
        axt.yaxis.set_label_position("right")
        axt.set_xlabel("Channel")
        axt.set_ylabel("Counts")

        self.cbar = fig.colorbar(self.im, cax=cax)
        self.cbar.set_label("Counts")
        cax.set_box_aspect(8)
        self._check_ax = fig.add_subplot(gs[5, 0])
        for spine in self._check_ax.spines.values():
            spine.set_visible(False)
        self._check = CheckButtons(self._check_ax, ["log"], [False])
        self._check.on_clicked(lambda label: self.set_log(self._check.get_status()[0]))
        if title:
            fig.suptitle(title)

        y0 = self.thr[self.row]
        (self._line_c,) = axc.plot([], [], **_CURVE)
        (self._line_t,) = axt.plot([], [], **_CURVE)
        self._vline = ax.axvline(self.channel, **_CURSOR)
        self._hline = ax.axhline(y0, **_CURSOR)
        self._mark_c = axc.axhline(y0, **_CURSOR)
        self._mark_t = axt.axvline(self.channel, **_CURSOR)
        self._readout = ax.set_title("")

        ax.set_xlim(*self._xfull)
        ax.set_ylim(*self._yfull)
        axc.set_xlim(self.vmin, self.vmax)
        axt.set_ylim(self.vmin, self.vmax)

        self._blit = _BlitManager(fig.canvas, [
            self._line_c, self._line_t, self._vline, self._hline,
            self._mark_c, self._mark_t, self._readout])
        fig.canvas.mpl_connect("button_press_event", self._on_click)
        fig.canvas.mpl_connect("scroll_event", self._on_scroll)
        fig.canvas.mpl_connect("key_press_event", self._on_key)
        # The channel curve is reduced to the visible pixels, so rebuild it
        # when the view or the panel size changes.
        ax.callbacks.connect("xlim_changed", lambda ax: self._refresh_selection())
        fig.canvas.mpl_connect("resize_event", lambda event: self._refresh_selection())

    # ------------------------------------------------------------ public API
    def show(self):
        """Show the window and let the GUI paint it before returning."""
        self.fig.show()
        self.fig.canvas.start_event_loop(0.05)

    def select(self, channel=None, row=None, threshold=None, draw=True):
        """Move the crosshair. ``threshold`` is a value on the scan axis."""
        if threshold is not None:
            row = self._row_of(threshold)
        if channel is not None:
            self.channel = int(np.clip(channel, 0, self.ncol - 1))
        if row is not None:
            self.row = int(np.clip(row, 0, self.nrow - 1))
        self._refresh_selection()
        if draw:
            self._blit.update()

    def set_clim(self, vmin=None, vmax=None):
        """Set the colour limits; the side panels use the same count range."""
        if vmin is not None:
            self.vmin = float(vmin)
        if vmax is not None:
            self.vmax = float(vmax)
        self.vmax = max(self.vmax, self.vmin + 1.0)
        self.im.set_clim(self.vmin, self.vmax)
        self.axc.set_xlim(self.vmin, self.vmax)
        self.axt.set_ylim(self.vmin, self.vmax)
        self.fig.canvas.draw_idle()

    def set_log(self, on=True):
        """Counts on a symlog scale (linear below one count) everywhere."""
        self.log = bool(on)
        if self.log:
            self.im.set_norm(SymLogNorm(linthresh=1, vmin=self.vmin, vmax=self.vmax))
            self.axc.set_xscale("symlog", linthresh=1)
            self.axt.set_yscale("symlog", linthresh=1)
        else:
            self.im.set_norm(Normalize(vmin=self.vmin, vmax=self.vmax))
            self.axc.set_xscale("linear")
            self.axt.set_yscale("linear")
        self.axc.set_xlim(self.vmin, self.vmax)
        self.axt.set_ylim(self.vmin, self.vmax)
        if self._check.get_status()[0] != self.log:
            self._check.eventson = False
            self._check.set_active(0)
            self._check.eventson = True
        self.fig.canvas.draw_idle()

    def fit_panels(self):
        """Scale the side panels to the selected curves."""
        top = max(self.data[:, self.channel].max(), self.data[self.row].max(), 1) * 1.05
        self.axc.set_xlim(self.vmin, top)
        self.axt.set_ylim(self.vmin, top)
        self.fig.canvas.draw_idle()

    def update_row(self, i, values, draw=True):
        """Replace scan step ``i`` (index in acquisition order) and redraw."""
        r = self.nrow - 1 - i if self._flip else i
        self.data[r] = values
        self._data_changed(draw)

    def set_data(self, data):
        """Replace the whole scan with an array of the same shape."""
        data = np.asarray(data)
        if data.shape != self.data.shape:
            raise ValueError(f"shape {data.shape} does not match {self.data.shape}")
        self.data[...] = data[::-1] if self._flip else data
        self._data_changed(True)

    # ------------------------------------------------------------ internals
    def _data_changed(self, draw):
        self.im.set_data(self.data)
        self._refresh_selection()
        if draw:
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def _row_of(self, y):
        return int(np.clip(round((y - self.thr[0]) / self.step), 0, self.nrow - 1))

    def _channel_curve(self):
        """Counts vs channel at the selected step, reduced to a min/max
        envelope with two points per screen pixel when the visible range has
        more channels than that. Drawing 50k zigzag segments costs over
        100 ms; the envelope looks the same and draws in under 1 ms."""
        y = self.data[self.row]
        lo, hi = self.ax.get_xlim()
        i0 = max(int(np.floor(lo)), 0)
        i1 = min(int(np.ceil(hi)) + 1, self.ncol)
        npix = max(int(self.ax.bbox.width), 1)
        if i1 - i0 <= 2 * npix:
            return self.chans, y
        edges = np.linspace(i0, i1, npix + 1).astype(int)
        seg = y[i0:i1]
        ymin = np.minimum.reduceat(seg, edges[:-1] - i0)
        ymax = np.maximum.reduceat(seg, edges[:-1] - i0)
        xs = np.repeat((edges[:-1] + edges[1:] - 1) / 2, 2)
        ys = np.empty(2 * npix, dtype=seg.dtype)
        ys[0::2] = ymin
        ys[1::2] = ymax
        return xs, ys

    def _refresh_selection(self):
        ch, r = self.channel, self.row
        y = self.thr[r]
        self._line_c.set_data(self.data[:, ch], self.thr)
        self._line_t.set_data(*self._channel_curve())
        self._vline.set_xdata([ch, ch])
        self._mark_t.set_xdata([ch, ch])
        self._hline.set_ydata([y, y])
        self._mark_c.set_ydata([y, y])
        self._readout.set_text(
            f"channel {ch}    {self.ylabel.lower()} {y:g}    counts {self.data[r, ch]}")

    def _on_click(self, event):
        if event.button != MouseButton.LEFT or event.inaxes is None:
            return
        if self.fig.canvas.widgetlock.locked():   # toolbar pan or zoom active
            return
        channel = row = None
        if event.inaxes in (self.ax, self.axt):
            channel = round(event.xdata)
        if event.inaxes in (self.ax, self.axc):
            row = self._row_of(event.ydata)
        if channel is not None or row is not None:
            self.select(channel=channel, row=row)

    def _on_scroll(self, event):
        if event.inaxes is None or event.step == 0:
            return
        zoom_in = event.step > 0
        if event.inaxes in (self.ax, self.cax):
            self.set_clim(vmax=self.vmax / 1.5 if zoom_in else self.vmax * 1.5)
        elif event.inaxes is self.axt:
            self.ax.set_xlim(*self._zoomed(self.ax.get_xlim(), event.xdata, zoom_in, self._xfull))
            self.fig.canvas.draw_idle()
        elif event.inaxes is self.axc:
            self.ax.set_ylim(*self._zoomed(self.ax.get_ylim(), event.ydata, zoom_in, self._yfull))
            self.fig.canvas.draw_idle()

    @staticmethod
    def _zoomed(lim, center, zoom_in, full):
        f = 1 / 1.5 if zoom_in else 1.5
        lo = max(center - (center - lim[0]) * f, full[0])
        hi = min(center + (lim[1] - center) * f, full[1])
        return lo, hi

    def _on_key(self, event):
        key = event.key or ""
        n = 10 if key.startswith("shift+") else 1
        key = key.removeprefix("shift+")
        if key == "left":
            self.select(channel=self.channel - n)
        elif key == "right":
            self.select(channel=self.channel + n)
        elif key == "up":
            self.select(row=self.row + n)
        elif key == "down":
            self.select(row=self.row - n)
        elif key == "a":
            self.fit_panels()
        elif key == "A":
            self.set_clim()
        elif key == "l":
            self.set_log(not self.log)


def plot_thrscan(adata, smin, smax, sstep, **kwargs):
    """Open an interactive viewer for a scan; returns the ThrScanViewer."""
    viewer = ThrScanViewer(adata, smin, smax, sstep, **kwargs)
    viewer.show()
    return viewer


def plot_simple_thrscan(adata, threshold, cmap="viridis", **kwargs):
    """Static scan image with a colour bar; returns (fig, ax)."""
    data = np.asarray(adata)
    thr = np.asarray(threshold, dtype=float)
    if data.ndim != 2 or len(thr) != data.shape[0]:
        raise ValueError(f"data shape {data.shape} does not match {len(thr)} thresholds")
    data, thr, _ = _ascending(data, thr)
    half = abs(thr[1] - thr[0]) / 2 if len(thr) > 1 else 0.5
    fig, ax = plt.subplots()
    im = ax.imshow(data, aspect="auto", origin="lower", cmap=cmap,
                   extent=(-0.5, data.shape[1] - 0.5, thr[0] - half, thr[-1] + half),
                   **kwargs)
    fig.colorbar(im, ax=ax, label="Counts")
    ax.set_xlabel("Channel")
    ax.set_ylabel("Threshold")
    return fig, ax
