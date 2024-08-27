# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from . import factory as fa

testing_dims = ['xx', 'yy', 'zz', 'time', 'temperature']


variable = partial(fa.variable, dims=testing_dims)
data_array = partial(fa.data_array, dims=testing_dims)
dataset = partial(fa.dataset, dims=testing_dims)
scatter = fa.scatter
