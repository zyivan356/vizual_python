from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np

# Определение нативных расширений
extensions = [
    Extension(
        "core.stress_calculator",
        ["core/stress_calculator.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3",],
        extra_link_args=[],
        language="c++"
    )
]

setup(
    name="my_engineering_app",
    packages=find_packages(),
    ext_modules=cythonize(extensions, language_level=3),
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "engineering-app=app:main"
        ]
    }
)