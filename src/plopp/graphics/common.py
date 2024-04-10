# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2024 Scipp contributors (https://github.com/scipp)


def args_to_update(*args, **kwargs):
    new = kwargs
    if args:
        if len(args) > 1:
            raise TypeError('Update expected at most 1 arg.  Got {}.'.format(len(args)))
        else:
            new.update(args[0])
    return new
