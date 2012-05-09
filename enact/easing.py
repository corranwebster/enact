#
# (C) Copyright 2012 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from numpy import zeros_like

from traits.api import Trait, Callable

def cts_easing(f):
    def easing(dt, initial, final):
        return initial + (final-initial)*f(dt)
    return easing

def int_easing(f):
    def easing(dt, initial, final):
        return int(round(initial + (final-initial)*f(dt)))
    return easing

def list_extend_easing(f):
    """ Extend a list with easing
    """
    def easing(dt, initial, final):
        l_i = len(initial)
        l_f = len(final)
        l = int(round(l_i + (l_f-l_i)*f(dt)))
        if l_i < l_f:
            return final[:l]
        else:
            return initial[:l]
    return easing

def cts_array_extend_easing(f, g):
    """ Extend a float array with easing length and values
    """
    def easing(dt, initial, final):
        l_i = len(initial)
        l_f = len(final)
        l = int(round(l_i + (l_f-l_i)*g(dt)))
        if l_i < l_f:
            full_initial = zeros_like(final)
            full_initial[:l_i] = initial
            return (full_initial + (final-full_initial)*f(dt))[:l]
        else:
            full_final = zeros_like(initial)
            full_final[:l_f] = final
            return (initial + (full_final-initial)*f(dt))[:l]
            
    return easing

def reverse(f):
    def f_prime(t):
        return 1.0 - f(1.0-t)
    return f_prime
 

cts_linear = cts_easing(lambda t: t)
cts_ease_out_quad = cts_easing(lambda t: t**2)
cts_ease_in_quad = cts_easing(lambda t: 1.0-(1.0-t)**2)

int_linear = int_easing(lambda t: t)
int_ease_out_quad = int_easing(lambda t: t**2)
int_ease_in_quad = int_easing(lambda t: 1.0-(1.0-t)**2)

list_linear = list_extend_easing(lambda t: t)
list_ease_out_quad = list_extend_easing(lambda t: t**2)
list_ease_in_quad = list_extend_easing(lambda t: 1.0-(1.0-t)**2)

array_linear = cts_array_extend_easing(lambda t: t, lambda t: t)
array_ease_out_quad = cts_array_extend_easing(lambda t: t**2, lambda t: t**2)
array_ease_in_quad = cts_array_extend_easing(lambda t: 1.0-(1.0-t)**2, lambda t: 1.0-(1.0-t)**2)

easing_functions = {
    'linear': cts_linear,
    'ease_out': cts_ease_out_quad,
    'ease_in': cts_ease_in_quad,
    'int_linear': int_linear,
    'int_ease_in': int_ease_in_quad,
    'int_ease_out': int_ease_out_quad,
    'list_linear': list_linear,
    'list_ease_in': list_ease_in_quad,
    'list_ease_out': list_ease_out_quad,
    'array_linear': array_linear,
    'array_ease_in': array_ease_in_quad,
    'array_ease_out': array_ease_out_quad,
}

Easing = Trait('linear', easing_functions, Callable)
