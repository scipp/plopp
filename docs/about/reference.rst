.. currentmodule:: plopp

*************
API Reference
*************

Plotting
========

.. autosummary::
   :toctree: generated

   plot
   slicer
   superplot
   inspector
   scatter3d

Core
====

.. autosummary::
   :toctree: generated

   core.Node
   core.View
   core.node
   core.input_node
   core.widget_node
   core.show_graph

Graphics
========

.. autosummary::
   :toctree: generated

   graphics.ColorMapper
   graphics.FigImage
   graphics.FigLine
   graphics.FigScatter3d
   graphics.figure1d
   graphics.figure2d
   graphics.figure3d

Widgets and tools
=================

.. autosummary::
   :toctree: generated

   widgets.Box
   widgets.Checkboxes
   widgets.HBar
   widgets.SliceWidget
   widgets.VBar

   widgets.tools.AxesTool
   widgets.tools.ButtonTool
   widgets.tools.CameraTool
   widgets.tools.ColorTool
   widgets.tools.HomeTool
   widgets.tools.LogNormTool
   widgets.tools.LogxTool
   widgets.tools.LogyTool
   widgets.tools.MultiToggleTool
   widgets.tools.OutlineTool
   widgets.tools.PanZoomTool
   widgets.tools.SaveTool
   widgets.tools.ToggleTool

   widgets.drawing.DrawingTool
   widgets.drawing.PointsTool

   widgets.cut3d.Cut3dTool
   widgets.cut3d.TriCutTool

Backends
========

.. toctree::
   :caption: Backends
   :maxdepth: 1

   reference/matplotlib
   reference/plotly
   reference/pythreejs
