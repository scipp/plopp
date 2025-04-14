# Installation

`````{tab-set}
````{tab-item} pip
```sh
pip install plopp[scipp]
```

This will install both `plopp` and `scipp` which is required to use `plopp`.
If you already have `scipp` installed, you can leave the `[scipp]` part out:

```sh
pip install plopp
```

By default, this will only install minimal requirements which will allow you to create static 1d and 2d plots.
If you wish to use additional features (interactive figures and 3d rendering), you can install all the optional dependencies by doing

```sh
pip install plopp[all]
```
````
````{tab-item} conda
```sh
conda install -c conda-forge plopp
```
````
`````
