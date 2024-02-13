import plopp as pp
from plopp.data.testing import cylinder, cylinders


def test_single_cylinder3d():
    dg = cylinder(0.1, 2)
    pp.cylinders3d(dg)


def test_multiple_cylinder3d():
    dg = cylinders()
    pp.cylinders3d(dg)
