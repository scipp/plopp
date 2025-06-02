:::{image} _static/logo.svg
:class: only-light
:alt: Plopp
:width: 60%
:align: center
:::

:::{image} _static/logo-dark.svg
:class: only-dark
:alt: Plopp
:width: 60%
:align: center
:::

```{raw} html
   <style>
    .transparent {display: none; visibility: hidden;}
    .transparent + a.headerlink {display: none; visibility: hidden;}
   </style>
```

```{role} transparent
```

# {transparent}`Plopp`

<span style="font-size:1.2em;font-style:italic;color:var(--pst-color-text-muted)">
  Visualization library for Scipp
  </br></br>
</span>


## Getting started

::::{grid} 2

:::{grid-item-card} {octicon}`desktop-download;1em`&nbsp; Installation
:link: getting-started/installation.md

:::

:::{grid-item-card} {octicon}`eye;1em`&nbsp; Overview
:link: getting-started/overview.ipynb

:::

::::

::::{grid} 2

:::{grid-item-card} {octicon}`graph;1em`&nbsp; Numpy, Pandas, and Xarray
:link: getting-started/numpy-pandas-xarray.ipynb

:::

:::{grid-item-card} {octicon}`download;1em`&nbsp; Saving figures to disk
:link: getting-started/saving-figures.ipynb

:::

::::

## Plotting

::::{grid} 3

:::{grid-item-card} Line plot
:link: plotting/line-plot.ipynb
:img-bottom: _static/plotting/line-plot.png

:::

:::{grid-item-card} Image plot
:link: plotting/image-plot.ipynb
:img-bottom: _static/plotting/image-plot.png

:::

::::{grid-item-card} Scatter plot
:link: plotting/scatter-plot.ipynb
:img-bottom: _static/plotting/scatter-plot.png

:::

::::

::::{grid} 3

:::{grid-item-card} Slicer plot
:link: plotting/slicer-plot.ipynb
:img-bottom: _static/plotting/slicer-plot.png

:::

:::{grid-item-card} Inspector plot
:link: plotting/inspector-plot.ipynb
:img-bottom: _static/plotting/inspector-plot.png

:::

:::{grid-item-card} Super-plot
:link: plotting/super-plot.ipynb
:img-bottom: _static/plotting/super-plot.png

:::

::::

::::{grid} 3

:::{grid-item-card} Scatter 3D plot
:link: plotting/scatter3d-plot.ipynb
:img-bottom: _static/plotting/scatter3d-plot.png

:::

:::{grid-item-card} Mesh 3D plot
:link: plotting/mesh3d-plot.ipynb
:img-bottom: _static/plotting/mesh3d-plot.png

:::

::::

## Custom figures

::::{grid} 3

:::{grid-item-card} Subplots / Tiled plots
:link: customization/subplots.ipynb
:img-bottom: _static/customization/subplots.png

:::

:::{grid-item-card} Tweaking figures
:link: customization/tweaking-figures.ipynb
:img-bottom: _static/customization/tweaking-figures.png

:::

::::{grid-item-card} Building custom interfaces
:link: customization/custom-interfaces.ipynb
:img-bottom: _static/customization/custom-interfaces.png

:::

::::

::::{grid} 3

:::{grid-item-card} Graph and node tips
:link: customization/graph-node-tips.ipynb
:img-bottom: _static/customization/graph-node-tips.png

:::

::::

```{toctree}
---
hidden:
---

getting-started/index
plotting/index
customization/index
gallery/index
api-reference/index
developer/index
about/index
```
