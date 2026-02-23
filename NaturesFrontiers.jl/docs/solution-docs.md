The solutions are saved as HDF5 files (solutions.h5) in order to save disk space and speed up use for mapping particular scenarios.

In order to use them in python, you'll need to install the `h5py` module (e.g. `conda install h5py`).

The files are structured with a "solutions" group containing separate arrays for "maximization" and "minimization" solutions. These arrays are indexed by `(sdu, sol)`. In order to access a particular solution, do something like:

```python
    sols = h5py.File('solutions.h5', 'r')
    s = sols['solutions']['maximization'][:, i]
```