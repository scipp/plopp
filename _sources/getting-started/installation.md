# Installation

`````{tab-set}
````{tab-item} pip
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

## Interactive figures in JupyterLab

Interactive figures (`%matplotlib widget`) can fail to render in JupyterLab 4.4 and later,
with math text parse errors, blank figures, or kernel crashes.
JupyterLab routes widget messages over kernel subshells, which ipykernel 7 and later
service on their own threads.
Drawing a live canvas then races with figure creation during cell execution,
and Matplotlib is not thread-safe
(see [ipympl#610](https://github.com/matplotlib/ipympl/issues/610)).

A lock added in ipympl removes the math text parse errors, but the blank figures and
crashes remain, since the canvas frame and resize handlers still run concurrently with
drawing.
Until that is addressed, either

- set `commsOverSubshells` to `disabled` in the JupyterLab settings editor and restart
  JupyterLab (the setting only applies to newly connected kernels), or
- install `ipykernel<7`.
