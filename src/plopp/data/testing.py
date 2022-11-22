# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

from . import factory as fa
from functools import partial

testing_dim_list = ['xx', 'yy', 'zz', 'time', 'temperature']

variable = partial(fa.variable, dim_list=testing_dim_list)
data_array = partial(fa.data_array, dim_list=testing_dim_list)
dataset = partial(fa.dataset, dim_list=testing_dim_list)
scatter_data = fa.scatter_data
