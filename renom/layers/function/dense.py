#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from renom.core import Variable, precision
from renom.operation import dot
from .parameterized import Parametrized
from renom.utility.initializer import GlorotNormal


class Dense(Parametrized):
    '''Fully connected layer as described bellow.

        :math:`f(x)= w \cdot x + b`


    If the argument `input_size` is passed, this layers' weight is initialized
    in the __init__ function.
    Otherwise, the weight is initialized in its first forward calculation.

    Args:
        output_size (int): Output unit size.
        input_size (int): Input unit size.
        initializer (Initializer): Initializer object for weight initialization.

    Example:
        >>> import numpy as np
        >>> import renom as rm
        >>> x = np.random.rand(3, 2)
        >>> x.shape
        (3, 2)
        >>> layer = rm.Dense(3)
        >>> z = layer(x)
        >>> z.shape
        (3, 3)
    '''

    def __init__(self, output_size, input_size=None, initializer=GlorotNormal()):
        self._output_size = output_size
        self._initializer = initializer
        super(Dense, self).__init__(input_size)

    def clone(self, n):
        return [self.__class__(self._output_size) for _ in range(n)]

    def weight_initiallize(self, input_size):
        size_i = input_size[0] if isinstance(input_size, tuple) else input_size
        size_o = self._output_size
        self.params = {
            "w": Variable(self._initializer((size_i, size_o)), auto_update=True),
            "b": Variable(np.zeros((1, size_o)).astype(precision), auto_update=True)}

    def forward(self, x):
        return dot(x, self.params["w"]) + self.params["b"]
