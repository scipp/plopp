# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg


class Figure(pg.GraphicsLayoutWidget):
    def __init__(self, View, *args, **kwargs):
        super().__init__()
        self.view = View(*args, **kwargs)
        self.setWindowTitle("Figure")
        self.setBackground("#ffffff")

        # self.viewport = self.addViewBox(None, col=0)
        # self.viewport.setAspectLocked(True)
        # cmap = plt.colormaps["viridis"]
        # self._image = pg.ImageItem(image=cmap(np.random.random((1000, 1000))))
        # self.viewport.addItem(self._image)
        canvas = self.view.canvas
        self.addItem(canvas.axes)
