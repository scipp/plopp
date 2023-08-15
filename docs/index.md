<div style="display: block; margin-left: auto; margin-right: auto; width: 60%;">
    <img src="_static/logo.svg" width="100%" />
</div>

# Plopp

**Plopp** is the data visualization framework for the [Scipp](https://scipp.github.io>) project.

## Installation

### Using pip

You can install from ``pip`` using

```bash
pip install plopp[scipp]
```

This will install both ``plopp`` and ``scipp`` which is required to use ``plopp``.
If you already have ``scipp`` installed, you can leave the ``[scipp]`` part out:

```bash
pip install plopp
```

By default, this will only install minimal requirements which will allow you to create
static 1d and 2d plots.
If you wish to use additional features (interactive figures and 3d rendering),
you can install all the optional dependencies by doing

```bash
pip install plopp[all]
```

### Using conda

You can install from ``conda`` using

```bash
conda install -c conda-forge -c scipp plopp
```

## Get in touch

- If you have questions that are not answered by these documentation pages, ask on [GitHub discussions](https://github.com/scipp/plopp/discussions>).
Please include a self-contained reproducible example if possible.
- Report bugs (including unclear, missing, or wrong documentation!), suggest features or view the source code [on GitHub](https://github.com/scipp/plopp>).


```{toctree}
---
hidden:
---

getting-started/index
basics/index
customization/index
examples/index
about/index
```
