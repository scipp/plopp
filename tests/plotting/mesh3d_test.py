import plopp as pp
import scipp as sc
import numpy as np
from plopp.data.mesh import teapot


def make_one_teapot_mesh3d(**kwargs):
    mesh, faces, names = teapot()
    return pp.mesh3d(mesh, faces, **names, **kwargs)


def make_two_teapots_mesh3d(**kwargs):
    x0 = sc.spatial.translation(value=[40, 0, 10], unit='m')
    s0 = sc.spatial.scaling_from_vector(value=[1, 0.3, 1])
    r0 = sc.spatial.rotations_from_rotvecs(sc.vector(value=[-90, 0, 0], unit='degree'))
    t0, _, _ = teapot(intensity=1, transform=s0*r0*x0)
    t1, faces, names = teapot(intensity=2)

    a = names['point']
    b = names['intensity']
    ts = sc.DataArray(data=sc.concat((t0.data, t1.data), dim=a),
                      coords={b: sc.concat((t0.coords[b], t1.coords[b]), dim=a)})
    return pp.mesh3d(ts, faces, **names, **kwargs)


def make_many_teapots_mesh3d(number: int = 100, seed: int = 1, **kwargs):
    rng = np.random.default_rng(seed)
    x = sc.vector(value=[1, 0, 0], unit='m')
    theta = sc.arange(start=0., stop=360., step=360/number, dim='teapot', unit='degree')
    ry = sc.spatial.rotations_from_rotvecs(sc.vector(value=[0, 1, 0]) * theta)
    tz = 300 * sc.vector(value=[0, 1, 0], unit='m') * sc.sin(theta) ** 2
    p0 = tz + ry * ((50 * sc.cos(theta)**2 + 20) * x)
    t_f_n = [teapot(intensity=i, transform=p0['teapot', i]) for i in range(p0.sizes['teapot'])]
    ts, fs, ns = list(zip(*t_f_n))
    names = ns[0]
    data = sc.concat(tuple(x.data for x in ts), dim=names['point'])
    intensity = sc.concat(tuple(x.coords[names['intensity']] for x in ts), dim=names['point'])
    mesh = sc.DataArray(data=data, coords={names['intensity']: intensity})
    return pp.mesh3d(mesh, fs[0], **names, **kwargs)


def test_one_teapot():
    from plopp.data.mesh import teapot_vertices_faces
    obj = make_one_teapot_mesh3d()

    figure = obj.children[0]
    assert len(figure.artists) == 1
    artist = list(figure.artists.values())[0]

    vertices, faces = teapot_vertices_faces()
    assert np.allclose(faces, artist._faces.values)
    assert np.allclose(vertices, artist._data.data.values)


def test_many_teapots():
    try:
        make_many_teapots_mesh3d()
        assert True
    except ValueError:
        assert False
