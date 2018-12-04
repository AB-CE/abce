# from distutils.core import setup
# from distutils.extension import Extension
from Cython.Distutils import build_ext

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

setup(
    name='trade',
    ext_modules=[
        Extension('trade', ['trade.py']),
        Extension('logger/online_variance', ['logger/online_variance.pyx'])],
    cmdclass={'build_ext': build_ext}
)
