# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .scene3d import Scene3d
from ..widgets import Cut3dTool

import scipp as sc
from copy import copy
import numpy as np
from ipywidgets import VBox, HBox


class CutScene(Scene3d):

    def __init__(self, *nodes, **kwargs):
        super().__init__(*nodes, **kwargs)
        limits = self.get_limits()
        self.cut_x = Cut3dTool(*nodes,
                               direction='x',
                               limits=limits,
                               description='X',
                               icon='cube')
        self.cut_y = Cut3dTool(*nodes,
                               direction='y',
                               limits=limits,
                               description='Y',
                               icon='cube')
        self.cut_z = Cut3dTool(*nodes,
                               direction='z',
                               limits=limits,
                               description='Z',
                               icon='cube')
        self.bottom_bar.children = list(
            self.bottom_bar.children) + [self.cut_x, self.cut_y, self.cut_z]
        self.scene.add([self.cut_x.outline, self.cut_y.outline, self.cut_z.outline])
