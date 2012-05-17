#
# Adapted from Scipy Cookbook Line Integral Convolution
#
#     http://www.scipy.org/Cookbook/LineIntegralConvolution
#
# Originally by A M Archibald
#

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("lic_internal", ["lic_internal.pyx"], include_dirs = [numpy.get_include()])]
)

