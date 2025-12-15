import sys
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy as np

# Явное указание пакетов для сборки
packages = [
    'core',
    'gui',
    'viz',
    'bim',
    'plugins',
    'plugins.structural',
    'plugins.geotech'
]

extensions = [
    Extension(
        "core.stress_calculator",
        ["core/stress_calculator.pyx"],
        include_dirs=[np.get_include()],
        language="c++",
        extra_compile_args=["-std=c++11"] if sys.platform != "win32" else []
    )
]

setup(
    name="Engineering Suite Core",
    packages=packages,
    ext_modules=cythonize(extensions, language_level=3),
    zip_safe=False,
)