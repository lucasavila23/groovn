import matplotlib

matplotlib.use("Agg")
import numpy as np
import pandas as pd

import viz


def test_helpers_draw_without_error():
    viz.style()
    ax = viz.label(viz.new_ax(), "Title", "x", "y", logx=True, logy=True)
    assert ax.get_title(loc="left") == "Title" and ax.get_xscale() == "log"
    corr = pd.DataFrame(np.eye(3), index=list("abc"), columns=list("abc"))
    ax = viz.heatmap(corr, "Correlation")
    assert ax.get_title(loc="left") == "Correlation"
    assert len(viz.CATEGORICAL) == 8
