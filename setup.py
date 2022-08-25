# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Scipp contributors (https://github.com/scipp)

import os
import setuptools
import subprocess
import sys


def set_version_and_find_packages():
    # Write fixed version to file to avoid having gitpython as a hard
    # dependency
    v = subprocess.check_output(['git', 'describe', '--tags'],
                                stderr=subprocess.STDOUT,
                                shell=sys.platform == 'win32')
    with open(os.path.join('src', 'plopp', '_version.py'), 'w') as f:
        f.write('__version__ = \'{}\'\n'.format(v.decode().strip()))
    return setuptools.find_packages('src')


setuptools.setup(name='plopp',
                 packages=set_version_and_find_packages(),
                 package_dir={"": "src"})
