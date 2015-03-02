'''
Visualise
=========

This module contains functions for plotting knots, supporting
different toolkits and types of plot.
'''

import numpy as n
from colorsys import hsv_to_rgb
from pyknot2.utils import ensure_shape_tuple
import random

def plot_line(points, mode='auto', clf=True, **kwargs):
    '''
    Plots the given line, using the toolkit given by mode.

    kwargs are passed to the toolkit specific function, except for:

    Parameters
    ----------
    points : ndarray
        The nx3 array to plot.
    mode : str
        The toolkit to draw with. Defaults to 'auto', which will
        automatically pick the first available toolkit from
        ['mayavi', 'matplotlib', 'vispy'], or raise an exception
        if none can be imported.
    clf : bool
        Whether the existing figure should be cleared
        before drawing the new one.
    '''
    if mode == 'auto':
        try:
            import mayavi.mlab as may
            mode = 'mayavi'
        except ImportError:
            pass
    if mode == 'auto':
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            mode = 'matplotlib'
        except (ImportError, ValueError):
            pass
    if mode == 'auto':
        try:
            import vispy
            mode = 'vispy'
        except ImportError:
            pass
    if mode == 'auto':
        raise ImportError('Couldn\'t import any of mayavi, vispy, '
                          'or matplotlib\'s 3d axes.')
            
    if mode == 'mayavi':
        plot_line_mayavi(points, clf=clf, **kwargs)
    elif mode == 'vispy':
        plot_line_vispy(points, clf=clf, **kwargs)
    elif mode == 'matplotlib':
        plot_line_matplotlib(points, clf=clf, **kwargs)
    else:
        raise Exception('invalid toolkit/mode')

    
def plot_line_mayavi(points, clf=True, tube_radius=1., colormap='hsv',
                     mus=None,
                     **kwargs):
    import mayavi.mlab as may
    if clf:
        may.clf()
    if mus is None:
        mus = n.linspace(0, 1, len(points))
    may.plot3d(points[:, 0], points[:, 1], points[:, 2], mus,
               colormap=colormap, tube_radius=tube_radius, **kwargs)

def plot_line_matplotlib(points, **kwargs):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot(points[:, 0], points[:, 1], points[:, 2])
    fig.show()

def plot_line_vispy(points, **kwargs):
    from vispy import app, scene
    canvas = scene.SceneCanvas(keys='interactive')
    canvas.view = canvas.central_widget.add_view()

    from colorsys import hsv_to_rgb
    colours = n.linspace(0, 1, len(points))
    colours = n.array([hsv_to_rgb(c, 1, 1) for c in colours])
    
    l = scene.visuals.Tube(points, colors=colours,
                           shading='smooth',
                           tube_points=8)
    
    canvas.view.add(l)
    canvas.view.set_camera('turntable', mode='perspective',
                           up='z', distance=1.5*n.max(n.max(
                               points, axis=0)))
    l.transform = scene.transforms.AffineTransform()
    l.transform.translate(-1*n.average(points, axis=0))

    canvas.show()
    return canvas
    

def plot_projection(points, crossings=None, mark_start=False,
                    fig_ax=None, show=True):
    '''
    Plot the 2d projection of the given points, with optional
    markers for where the crossings are.

    Parameters
    ----------
    points : array-like
        The nxm array of points in the line, with m >= 2.
    crossings : array-like or None
        The nx2 array of crossing positions. If None, crossings
        are not plotted. Defaults to None.
    '''
    import matplotlib.pyplot as plt

    if fig_ax is not None:
        fig, ax = fig_ax
    else:
        fig, ax = plt.subplots()
    ax.plot(points[:, 0], points[:, 1])
    ax.set_xticks([])
    ax.set_yticks([])

    xmin, ymin = n.min(points[:, :2], axis=0)
    xmax, ymax = n.max(points[:, :2], axis=0)
    dx = (xmax - xmin) / 10.
    dy = (ymax - ymin) / 10.

    ax.set_xlim(xmin - dx, xmax + dx)
    ax.set_ylim(ymin - dy, ymax + dy)

    if mark_start:
        ax.plot([points[0, 0]], [points[0, 1]], color='blue',
                marker='o')
    
    if crossings is not None and len(crossings):
        crossings = n.array(crossings)
        ax.plot(crossings[:, 0], crossings[:, 1], 'ro', alpha=0.5)
    if show:
        fig.show()

    return fig, ax

def plot_cell(lines, boundary=None, clf=True, **kwargs):
    mode = 'mayavi'
    import mayavi.mlab as may
    may.clf()

    hues = n.linspace(0, 1, len(lines) + 1)[:-1]
    colours = [hsv_to_rgb(hue, 1, 1) for hue in hues]
    random.shuffle(colours)
    for (line, colour) in zip(lines, colours):
        for segment in line:
            plot_line(segment, clf=False, color=colour, **kwargs)
    
    if boundary is not None:
        if isinstance(boundary, (float, int)):
            boundary = ensure_shape_tuple(boundary)
        if len(boundary) == 3:
            boundary = (0, boundary[0], 0, boundary[1], 0, boundary[2])
