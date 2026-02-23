from setuptools import setup

setup(
    name="wbnci",
    packages=["wbnci"],
    include_package_data=True,
    install_requires=[
        'numpy', 'gdal', 'pygeoprocessing', 'pandas', 'geopandas',
        'cython', 'matplotlib', 'h5py', 'tables'
    ],
)
