import os
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Фикс для Windows: отключаем OpenMP
if os.name == 'nt':
    extra_compile_args = ["/O2"]
    extra_link_args = []
else:
    extra_compile_args = ["-O3", "-fopenmp"]
    extra_link_args = ["-fopenmp"]

extensions = [
    Extension(
        "core.stress_calculator",
        ["core/stress_calculator.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c++"
    )
]

setup(
    name="vizual_python",
    ext_modules=cythonize(
        extensions,
        language_level=3,
        compiler_directives={'binding': True}
    ),
    zip_safe=False,
)