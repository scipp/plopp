# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from .fig1d import Figure1d
from .fig2d import Figure2d
from .scatterfig3d import ScatterFig3d
from ..widgets import Toolbar, HBar, VBar, tools

from ipywidgets import VBox, HBox
from functools import partial


def _running_in_jupyter() -> bool:
    """
    Detect whether Python is running in Jupyter.

    Note that this includes not only Jupyter notebooks
    but also Jupyter console and qtconsole.
    """
    try:
        from IPython import get_ipython
        import ipykernel.zmqshell
    except ImportError:
        # Cannot be Jupyter if IPython is not installed.
        return False

    return isinstance(get_ipython(), ipykernel.zmqshell.ZMQInteractiveShell)


def _is_sphinx_build():
    """
    Returns `True` if we are running inside a sphinx documentation build.
    """
    if not _running_in_jupyter():
        return False
    from IPython import get_ipython
    ipy = get_ipython()
    cfg = ipy.config
    meta = cfg["Session"]["metadata"]
    if hasattr(meta, "to_dict"):
        meta = meta.to_dict()
    return meta.get("scipp_sphinx_build", False)


# def _make_toolbar(tools):
#     _tools = {}
#     for tool in tools:
#         if isinstance(tool, str):
#             _tools[tool] = getattr(self, tool)
#         else:
#             _tools[tool[0]] = tool[1]

#     return Toolbar(tools=_tools)

# def make_fig_1d(*args, **kwargs):
#     fig = Figure1d(*args, **kwargs)
#     fig.canvas.fig.canvas.toolbar_visible = False
#     fig.canvas.fig.canvas.header_visible = False
#     # fig.toolbar = _make_toolbar(tools=['home', 'pan', 'zoom', 'logx', 'logy', 'save'])

#     toolbar = Toolbar(
#         tools={
#             'home': partial(fig.autoscale, draw=True),
#             'pan': fig.canvas.pan,
#             'zoom': fig.canvas.zoom,
#             # 'logx': fig.canvas.logx,
#             # 'logy': fig.canvas.logy,
#             'save': fig.canvas.save
#         })


def _patch_object(obj, figure):

    left_bar = VBar([obj.toolbar])
    right_bar = VBar()
    bottom_bar = HBar()
    top_bar = HBar()

    # figure.canvas.fig.canvas.toolbar_visible = False
    # figure.canvas.fig.canvas.header_visible = False

    obj.canvas = figure.canvas
    obj.update = figure.update
    obj.graph_nodes = figure.graph_nodes
    obj.get_child = figure.get_child
    obj.dims = figure.dims
    obj.render = figure.render
    obj.notify_view = figure.notify_view

    obj.left_bar = left_bar
    obj.right_bar = right_bar
    obj.bottom_bar = bottom_bar
    obj.top_bar = top_bar


# def _pan_zoom(change, fig):
#     if change['new'] == 'zoom':
#         fig.canvas.zoom()
#     elif change['new'] == 'pan':
#         fig.canvas.pan()
#     elif change['new'] is None:
#         fig.canvas.reset_mode()

# def _populate_container(obj):
#     print('_populate_container')
#     out = [
#         obj.top_bar,
#         HBox([
#             obj.left_bar,
#             # self._to_image() if _is_sphinx_build() else self._fig.canvas,
#             obj.canvas.fig.canvas,
#             obj.right_bar
#         ]),
#         obj.bottom_bar
#     ]
#     print('_populate_container 2')
#     return out

# class InteractiveFig1d(VBox, Figure1d):

#     def __init__(self, *args, **kwargs):
#         Figure1d.__init__(self, *args, **kwargs)
#         self.canvas.fig.canvas.toolbar_visible = False
#         self.canvas.fig.canvas.header_visible = False
#         self.toolbar = Toolbar(
#             tools={
#                 'home': tools.HomeTool(self.canvas.autoscale),
#                 'panzoom': tools.PanZoomTool(canvas=self.canvas),
#                 # 'zoom': fig.canvas.zoom,
#                 'logx': tools.LogxTool(self.canvas.logx),
#                 'logy': tools.LogyTool(self.canvas.logy),
#                 'save': tools.SaveTool(self.canvas.save)
#             })

#         self.left_bar = VBar([self.toolbar])
#         self.right_bar = VBar()
#         self.bottom_bar = HBar()
#         self.top_bar = HBar()
#         VBox.__init__(self, _populate_container(self))

#         # self.figure.canvas.fig.canvas.toolbar_visible = False
#         # self.figure.canvas.fig.canvas.header_visible = False
#         # super().__init__(tools=['home', 'pan', 'zoom', 'logx', 'logy', 'save'])
#         # self.toolbar.logx.value = self.figure.canvas.xscale == 'log'
#         # self.toolbar.logy.value = self.figure.canvas.yscale == 'log'


class InteractiveFig1d(VBox):

    def __init__(self, *args, **kwargs):

        fig = Figure1d(*args, **kwargs)
        fig.canvas.fig.canvas.toolbar_visible = False
        fig.canvas.fig.canvas.header_visible = False
        self.toolbar = Toolbar(
            tools={
                'home': tools.HomeTool(fig.canvas.autoscale),
                'panzoom': tools.PanZoomTool(canvas=fig.canvas),
                'logx': tools.LogxTool(fig.canvas.logx),
                'logy': tools.LogyTool(fig.canvas.logy),
                'save': tools.SaveTool(fig.canvas.save)
            })

        _patch_object(self, figure=fig)

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                # self._to_image() if _is_sphinx_build() else self._fig.canvas,
                self.canvas.fig.canvas,
                self.right_bar
            ]),
            self.bottom_bar
        ])


class InteractiveFig2d(VBox):

    def __init__(self, *args, **kwargs):

        fig = Figure2d(*args, **kwargs)
        fig.canvas.fig.canvas.toolbar_visible = False
        fig.canvas.fig.canvas.header_visible = False
        self.toolbar = Toolbar(
            tools={
                'home': tools.HomeTool(fig.canvas.autoscale),
                'panzoom': tools.PanZoomTool(canvas=fig.canvas),
                'logx': tools.LogxTool(fig.canvas.logx),
                'logy': tools.LogyTool(fig.canvas.logy),
                'lognorm': tools.LogNormTool(fig.toggle_norm),
                'save': tools.SaveTool(fig.canvas.save)
            })

        _patch_object(self, figure=fig)

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                # self._to_image() if _is_sphinx_build() else self._fig.canvas,
                self.canvas.fig.canvas,
                self.right_bar
            ]),
            self.bottom_bar
        ])


class InteractiveScatterFig3d(VBox):

    def __init__(self, *args, **kwargs):

        fig = ScatterFig3d(*args, **kwargs)
        self.toolbar = Toolbar(
            tools={
                'home':
                tools.HomeTool(fig.canvas.home),
                'camerax':
                tools.CameraTool(
                    fig.canvas.camera_x_normal,
                    description='X',
                    tooltip='Camera to X normal. Click twice to flip the view direction.'
                ),
                'cameray':
                tools.CameraTool(
                    fig.canvas.camera_y_normal,
                    description='Y',
                    tooltip='Camera to Y normal. Click twice to flip the view direction.'
                ),
                'cameraz':
                tools.CameraTool(
                    fig.canvas.camera_y_normal,
                    description='Z',
                    tooltip='Camera to Z normal. Click twice to flip the view direction.'
                ),
                'lognorm':
                tools.LogNormTool(fig.colormapper.toggle_norm),
                'box':
                tools.OutlineTool(fig.canvas.toggle_outline),
                'axes':
                tools.AxesTool(fig.canvas.toggle_axes3d)
            })

        # self.left_bar = VBar([self.toolbar])
        # self.right_bar = VBar()
        # self.bottom_bar = HBar()
        # self.top_bar = HBar()

        # obj.canvas = figure.canvas
        # obj.update = figure.update
        # obj.graph_nodes = figure.graph_nodes
        # obj.get_child = figure.get_child
        # obj.dims = figure.dims
        # obj.render = figure.render
        # obj.notify_view = figure.notify_view

        # obj.left_bar = left_bar
        # obj.right_bar = right_bar
        # obj.bottom_bar = bottom_bar
        # obj.top_bar = top_bar

        _patch_object(self, figure=fig)

        super().__init__([
            self.top_bar,
            HBox([
                self.left_bar,
                # self._to_image() if _is_sphinx_build() else self._fig.canvas,
                self.canvas.renderer,
                self.right_bar
            ]),
            self.bottom_bar
        ])


# class InteractiveFig2d(VBox, Figure2d):

#     def __init__(self, *args, **kwargs):

#         print(args, kwargs)
#         Figure2d.__init__(self, *args, **kwargs)
#         print('got to here 1')
#         self.canvas.fig.canvas.toolbar_visible = False
#         print('got to here 2')
#         self.canvas.fig.canvas.header_visible = False
#         print('got to here 3')
#         self.toolbar = Toolbar(
#             tools={
#                 'home': tools.HomeTool(self.canvas.autoscale),
#                 'panzoom': tools.PanZoomTool(canvas=self.canvas),
#                 # 'zoom': fig.canvas.zoom,
#                 'logx': tools.LogxTool(self.canvas.logx),
#                 'logy': tools.LogyTool(self.canvas.logy),
#                 'lognorm': tools.LogNormTool(self.toggle_norm),
#                 'save': tools.SaveTool(self.canvas.save)
#             })
#         print('got to here 4')

#         self.left_bar = VBar([self.toolbar])
#         print('got to here 5')
#         self.right_bar = VBar()
#         print('got to here 6')
#         self.bottom_bar = HBar()
#         print('got to here 7')
#         self.top_bar = HBar()
#         print('got to here 8')

#         out = [
#             self.top_bar,
#             HBox([
#                 self.left_bar,
#                 # self._to_image() if _is_sphinx_build() else self._fig.canvas,
#                 self.canvas.fig.canvas,
#                 self.right_bar
#             ]),
#             self.bottom_bar
#         ]

#         # VBox.__init__(self, _populate_container(self))
#         # VBox.__init__(self, out)

# fig = Figure2d(*args, **kwargs)
# # fig.canvas.fig.canvas.toolbar_visible = False
# # fig.canvas.fig.canvas.header_visible = False
# self.colormapper = fig.colormapper
# # toolbar = Toolbar(
# #     tools={
# #         'home': partial(fig.autoscale, draw=True),
# #         'pan': fig.canvas.pan,
# #         'zoom': fig.canvas.zoom,
# #         # 'logx': fig.canvas.logx,
# #         # 'logy': fig.canvas.logy,
# #         'lognorm': fig.toggle_norm,
# #         'save': fig.canvas.save
# #     })
# toolbar = Toolbar(
#     tools={
#         'home': tools.HomeTool(fig.canvas.autoscale),
#         'panzoom': tools.PanZoomTool(fig=fig),
#         # 'zoom': fig.canvas.zoom,
#         'logx': tools.LogxTool(fig.canvas.logx),
#         'logy': tools.LogyTool(fig.canvas.logy),
#         'lognorm': tools.LogNormTool(fig.toggle_norm),
#         'save': tools.SaveTool(fig.canvas.save)
#     })
# _patch_object(self, figure=fig, toolbar=toolbar)

# super().__init__([
#     self.top_bar,
#     HBox([
#         self.left_bar,
#         # self._to_image() if _is_sphinx_build() else self._fig.canvas,
#         self.canvas.fig.canvas,
#         self.right_bar
#     ]),
#     self.bottom_bar
# ])

# class Interactive(VBox):

#     def __init__(self, tools):

#         # self.left_bar = VBox()
#         # self.right_bar = VBox()
#         # self.bottom_bar = HBox()
#         # self.top_bar = HBox()

#         _tools = {}
#         for tool in tools:
#             if isinstance(tool, str):
#                 _tools[tool] = getattr(self, tool)
#             else:
#                 _tools[tool[0]] = tool[1]

#         self.toolbar = Toolbar(tools=_tools)

#         # self._fig.canvas.toolbar_visible = False
#         # self._fig.canvas.header_visible = False

#         self.left_bar = VBar([self.toolbar])
#         self.right_bar = VBar()
#         self.bottom_bar = HBar()
#         self.top_bar = HBar()

#         # self.left_bar.children = tuple([self.toolbar])

#         # self.figure = Figure.__init__(self, *args, **kwargs)

#         super().__init__([
#             self.top_bar,
#             HBox([
#                 self.left_bar,
#                 # self._to_image() if _is_sphinx_build() else self._fig.canvas,
#                 self.figure.canvas.fig.canvas,
#                 self.right_bar
#             ]),
#             self.bottom_bar
#         ])

#     # def _post_init(self):

#     #     self._fig.canvas.toolbar_visible = False
#     #     self._fig.canvas.header_visible = False

#     #     self.left_bar = VBox()
#     #     self.right_bar = VBox()
#     #     self.bottom_bar = HBox()
#     #     self.top_bar = HBox()

#     #     self.toolbar = Toolbar(
#     #         tools={
#     #             'home': self.home,
#     #             'pan': self.pan,
#     #             'zoom': self.zoom,
#     #             'logx': self.logx,
#     #             'logy': self.logy,
#     #             'save': self.save
#     #         })
#     #     self._fig.canvas.toolbar_visible = False
#     #     self._fig.canvas.header_visible = False
#     #     self.left_bar.children = tuple([self.toolbar])

#     def home(self):
#         self.figure.autoscale()
#         # self.figure.canvas.crop(**self._crop)
#         self.figure.crop()
#         self.figure.canvas.draw()

#     def pan(self):
#         if self.figure.canvas.toolbar_mode == 'zoom rect':
#             self.toolbar.zoom()
#         self.figure.canvas.pan()

#     def zoom(self):
#         if self.figure.canvas.toolbar_mode == 'pan/zoom':
#             self.toolbar.pan()
#         self.figure.canvas.zoom()

#     def save(self):
#         self.figure.canvas.save()

#     def logx(self):
#         # super().logx()
#         self.figure.canvas.xscale = 'log' if self.toolbar.logx.value else 'linear'
#         self.figure.autoscale()
#         self.figure.canvas.draw()

#     def logy(self):
#         # super().logy()
#         self.figure.canvas.yscale = 'log' if self.toolbar.logy.value else 'linear'
#         self.figure.autoscale()
#         self.figure.canvas.draw()
#         # self.toolbar.logy.value = self._ax.get_yscale() == 'log'

# class InteractiveFig1d(Interactive):

#     def __init__(self, *args, **kwargs):
#         self.figure = Figure1d(*args, **kwargs)
#         self.figure.canvas.fig.canvas.toolbar_visible = False
#         self.figure.canvas.fig.canvas.header_visible = False
#         super().__init__(tools=['home', 'pan', 'zoom', 'logx', 'logy', 'save'])
#         self.toolbar.logx.value = self.figure.canvas.xscale == 'log'
#         self.toolbar.logy.value = self.figure.canvas.yscale == 'log'

# class InteractiveFig2d(Interactive):

#     def __init__(self, *args, **kwargs):
#         self.figure = Figure2d(*args, **kwargs)
#         self.figure.canvas.fig.canvas.toolbar_visible = False
#         self.figure.canvas.fig.canvas.header_visible = False
#         super().__init__(tools=[
#             'home', 'pan', 'zoom', 'logx', 'logy', ('lognorm',
#                                                     self.figure.toggle_norm), 'save'
#         ])
#         self.toolbar.logx.value = self.figure.canvas.xscale == 'log'
#         self.toolbar.logy.value = self.figure.canvas.yscale == 'log'
