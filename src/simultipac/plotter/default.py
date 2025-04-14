"""Define a default plotter."""

import logging
from pathlib import Path
from typing import Any, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vedo
import vedo.backends
from matplotlib.axes import Axes
from matplotlib.typing import ColorType
from numpy.typing import NDArray
from vedo.mesh import Points

from simultipac.constants import markdown
from simultipac.plotter.plotter import Plotter
from simultipac.types import PARTICLE_0D_t, PARTICLE_3D_t

VEDO_BACKENDS_t = Literal["k3d", "vtk", "2d"]


class DefaultPlotter(Plotter):
    """An object using maptlotlib for 2D, Vedo for 3D."""

    def __init__(
        self, vedo_backend: VEDO_BACKENDS_t = "2d", *args, **kwargs
    ) -> None:
        """Set basic settings for the 3D Vedo plotter.

        Parameters
        ----------
        vedo_backend :
            The backend used by ``vedo``. The options that I tested were:

              - ``"k3d"``: Needs ``k3d`` library. Would be the ideal setting.
                But raises error in Jupyter Notebooks: ``TraitError: The
                'point_size' trait of a Points instance expected a float or a
                dict, not the float64 0.0.``
              - ``"vtk"``: Interactive 3D plots. Does not appear in ``HTML``
                (documentation).
              - ``"2d"``: Non-interactive 2D plots. Does appear in ``HTML``
                outputs.

        """
        self._vedo_backend: VEDO_BACKENDS_t
        self.vedo_backend = vedo_backend
        self._plotter_3d = vedo.Plotter()
        self._show_3d = False

        return super().__init__(*args, **kwargs)

    @property
    def vedo_backend(self) -> VEDO_BACKENDS_t:
        """The name of the vedo backend; *a priori*, no need to access that."""
        return self._vedo_backend

    @vedo_backend.setter
    def vedo_backend(self, value: VEDO_BACKENDS_t) -> None:
        """Update the vedo backend."""
        vedo.settings.default_backend = value
        self._vedo_backend = value

        if value in ("k3d",):
            self._k3d_patch()

    def plot(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        grid: bool = True,
        axes: Axes | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        label: str | None = None,
        **kwargs,
    ) -> tuple[Axes | NDArray[Any], ColorType]:
        """Plot 2D data.

        Parameters
        ----------
        data :
            Holds all data to plot.
        x, y :
            Name of column in ``data`` for x/y.
        grid :
            If grid should be plotted. Default is True.
        axes :
            Axes to re-use, if provided. The default is None (plot on new
            axis).
        xlabel, ylabel :
            Name of the labels. If not provided, we use the markdown equivalent
            of x/y, if defined in :data:`.markdown`.
        label :
            If provided, overrides the legend. Useful when several simulations
            are shown on the same plot.
        kwargs :
            Other keyword passed to the ``pd.DataFrame.plot`` method.

        Returns
        -------
        axes : Axes | NDArray[Any]
            Objects created by the ``pd.DataFrame.plot`` method.
        color : ColorType
            Color used for the plot.

        """
        if xlabel is None:
            xlabel = markdown.get(x, x)
        if ylabel is None:
            ylabel = markdown.get(y, y)
        axes = data.plot(
            x=x,
            y=y,
            grid=grid,
            ax=axes,
            xlabel=xlabel,
            ylabel=ylabel,
            label=label,
            **kwargs,
        )
        assert axes is not None
        color = self._get_color_from_last_plot(axes)
        return axes, color

    def _get_color_from_last_plot(
        self, axes: Axes | NDArray[Any]
    ) -> ColorType:
        """Get the color used for the last plot."""
        ax = axes if isinstance(axes, Axes) else axes[-1]
        assert isinstance(ax, Axes)
        lines = ax.get_lines()
        color = lines[-1].get_color()
        return color

    def hist(
        self,
        data: pd.DataFrame,
        x: PARTICLE_0D_t,
        bins: int = 200,
        hist_range: tuple[float, float] | None = None,
        xlabel: str | None = None,
        title: str | None = None,
        **kwargs,
    ) -> Any:
        if xlabel is None:
            xlabel = markdown.get(x, x)
        axes = data.plot(
            kind="hist",
            bins=bins,
            range=hist_range,
            xlabel=xlabel,
            title=title,
            **kwargs,
        )
        assert axes is not None
        return axes

    def plot_3d(
        self,
        data: Any,
        key: PARTICLE_3D_t,
        *args,
        **kwargs,
    ) -> Any:
        self._show_3d = True
        raise NotImplementedError

    def plot_mesh(self, mesh: vedo.Mesh, *args, **kwargs) -> vedo.Plotter:
        """Plot the mesh (``STL`` file)."""
        self._show_3d = True
        self._plotter_3d += mesh
        return self._plotter_3d

    def plot_trajectory(
        self,
        points: list[NDArray[np.float64]],
        emission_color: str | None = None,
        collision_color: str | None = None,
        collision_point: NDArray[np.float64] = np.array([], dtype=np.float64),
        lw: int = 7,
        r: int = 2,
        **kwargs,
    ) -> vedo.Plotter:
        """Plot the :class:`.Particle` trajectory stored in ``points``.

        Parameters
        ----------
        points :
            List of positions, as returned by :meth:`.Vector.to_list`.
        emission_color :
            If provided, the first known position is colored with this color.
        collision_color :
            If provided, the last known position is colored with this color.
        collision_point :
            If provided and ``collision_color`` is not ``None``, we plot this
            point instead of the last of ``points``. This is useful when the
            extrapolated time is large, and actuel collision point may differ
            significantly from last position points.
        lw :
            Trajectory line width.
        r :
            Size of the emission/collision points.

        """
        self._show_3d = True
        objects = vedo.Lines(points[:-1], points[1:], lw=lw, **kwargs)

        if emission_color is not None:
            objects += vedo.Point(pos=points[0], r=r, c=emission_color)

        if collision_color is not None:
            if len(collision_point) == 0:
                collision_point = points[-1]
            objects += vedo.Point(pos=collision_point, r=r, c=collision_color)

        self._plotter_3d += objects
        return self._plotter_3d

    def load_mesh(
        self, stl_path: str | Path, stl_alpha: float | None = None, **kwargs
    ) -> vedo.Mesh:
        mesh = vedo.load(stl_path)
        if stl_alpha is not None:
            mesh.alpha(stl_alpha)
        return mesh

    def show(self) -> None:
        """Show the plots that were produced.

        Useful for the bash interface.
        """
        plt.show()
        if not self._show_3d:
            return

        _plotter_3d: vedo.Plotter = self._plotter_3d

        _plotter_3d.show()

    def _k3d_patch(self) -> None:
        """Patch ``point_size`` to avoid following error.

        .. code-block::

              File "/home/placais/Documents/simulation/python/simultipac/examples/./analyze_cst_particle_monitor.py", line 61, in <module>
                result.show()
                ~~~~~~~~~~~^^
              File "/home/placais/Documents/simulation/python/simultipac/src/simultipac/simulation_results/simulation_results.py", line 324, in show
                return self._plotter.show()
                       ~~~~~~~~~~~~~~~~~~^^
              File "/home/placais/Documents/simulation/python/simultipac/src/simultipac/plotter/default.py", line 235, in show
                _plotter_3d.show()
                ~~~~~~~~~~~~~~~~^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/vedo/plotter.py", line 3337, in show
                return backends.get_notebook_backend(self.objects)
                       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/vedo/backends.py", line 31, in get_notebook_backend
                return start_k3d(actors2show)
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/vedo/backends.py", line 349, in start_k3d
                kobj = k3d.points(
                    ia.coordinates.astype(np.float32),
                ...<5 lines>...
                    name=name,
                )
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/k3d/factory.py", line 620, in points
                Points(
                ~~~~~~^
                    positions=positions,
                    ^^^^^^^^^^^^^^^^^^^^
                ...<15 lines>...
                    compression_level=compression_level,
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                ),
                ^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/k3d/objects.py", line 735, in __init__
                super(Points, self).__init__(**kwargs)
                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/k3d/objects.py", line 194, in __init__
                super(DrawableWithCallback, self).__init__(**kwargs)
                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/k3d/objects.py", line 108, in __init__
                super(Drawable, self).__init__(**kwargs)
                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/ipywidgets/widgets/widget.py", line 478, in __init__
                super(Widget, self).__init__(**kwargs)
                ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 1355, in __init__
                setattr(self, key, value)
                ~~~~~~~^^^^^^^^^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 716, in __set__
                self.set(obj, value)
                ~~~~~~~~^^^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 690, in set
                new_value = self._validate(obj, value)
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 722, in _validate
                value = self.validate(obj, value)
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 2460, in validate
                self.error(obj, value)
                ~~~~~~~~~~^^^^^^^^^^^^
              File "/home/placais/.pyenv/versions/simultipac/lib/python3.13/site-packages/traitlets/traitlets.py", line 831, in error
                raise TraitError(e)
            traitlets.traitlets.TraitError: The 'point_size' trait of a Points instance expected a float or a dict, not the float64 np.float64(0.0).

        This method overrides the default ``k3d.objects.Points`` constructor.
        May be related to
        [this issue](https://github.com/marcomusy/vedo/issues/1197).

        """
        logging.info("Applying patch for k3d.")

        import k3d

        original_k3d_points = k3d.points

        def patched_k3d_points(*args, **kwargs) -> k3d.objects.Points:
            """Instantiate ``k3d`` points with proper ``point_size`` arg."""
            ps = kwargs.get("point_size")
            if ps is None:
                return original_k3d_points(*args, **kwargs)

            if ps <= 0.0:
                logging.info("patching invalid point_size=0.0 -> 1.0.")
                ps = 1.0

            kwargs["point_size"] = ps
            return original_k3d_points(*args, **kwargs)

        k3d.points = patched_k3d_points
