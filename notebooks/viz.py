"""Chart styling for the lessons: cosmetics only, no analysis. Palette: colorblind-validated 8-hue order."""
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Categorical hues in fixed order: series 1 is always blue, 2 orange, ... Never cycle past 8; fold into "Other".
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
BLUE = CATEGORICAL[0]
SEQUENTIAL = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#6da7ec", "#2a78d6", "#184f95", "#0d366b"])
DIVERGING = LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])  # -1 red, 0 gray, +1 blue


def style() -> None:
    sns.set_theme(style="whitegrid", context="notebook", palette=CATEGORICAL)
    plt.rcParams.update({
        "figure.figsize": (9, 4.5), "figure.dpi": 110, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False, "grid.color": "#e6e5e0", "lines.linewidth": 2,
    })


def new_ax(**fig_kw):
    """A fresh figure with one axes: `ax = viz.new_ax()` then plot onto `ax`."""
    return plt.subplots(**fig_kw)[1]


def label(ax, title: str, xlabel: str = "", ylabel: str = "", logx: bool = False, logy: bool = False):
    """Title, axis labels and optional log scales in one call. Returns ax."""
    ax.set_title(title, loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if logx:
        ax.set_xscale("log")
    if logy:
        ax.set_yscale("log")
    return ax


def heatmap(matrix, title: str, diverging: bool = True, fmt: str = ".2f", ax=None):
    """Annotated heatmap. diverging=True for correlations/loadings (centered on 0, range -1..1);
    False for magnitudes in 0..1 such as missing-value shares."""
    ax = ax or new_ax(figsize=(1 + 0.8 * matrix.shape[1], 0.8 + 0.55 * matrix.shape[0]))
    kw = dict(cmap=DIVERGING, vmin=-1, vmax=1, center=0) if diverging else dict(cmap=SEQUENTIAL, vmin=0, vmax=1)
    sns.heatmap(matrix, annot=True, fmt=fmt, linewidths=2, linecolor="white", square=False,
                cbar_kws={"shrink": 0.7}, ax=ax, annot_kws={"size": 9}, **kw)
    ax.set_title(title, loc="left")
    return ax
