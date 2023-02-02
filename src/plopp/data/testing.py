# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

from functools import partial

from . import factory as fa

testing_dim_list = ['xx', 'yy', 'zz', 'time', 'temperature']

variable = partial(fa.variable, dim_list=testing_dim_list)
data_array = partial(fa.data_array, dim_list=testing_dim_list)
dataset = partial(fa.dataset, dim_list=testing_dim_list)
scatter = fa.scatter
