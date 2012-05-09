#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
import numpy

iris_dtype = numpy.dtype([
    ('sepal length', float),
    ('sepal width', float),
    ('petal length', float),
    ('petal width', float),
    ('species', 'O')])

def load_iris(filename):
    return numpy.loadtxt(filename, iris_dtype, delimiter=',')
    
