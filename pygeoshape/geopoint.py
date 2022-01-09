from typing import List
from shapely.geometry import Point
from pyproj import Transformer
import numpy as np
import numba as nb
import matplotlib.pyplot as plt
from pygeoshape.utils import fast_intersection_append


class GeoPoint:
    """Base GeoPoint type"""

    def __init__(
        self,
        coordinate: List,
        epsg_proj: str = "epsg:2163",
        epsg_from: str = "epsg:4326",
        is_xy: bool = False,
    ):
        """
        Args:
        ----

        coordinate (List): Input coordinates in (longitude, latitude, altitude) or (x, y, z)
        epsg_proj (str): EPSG code to transform longitude, latitude into x, y (default: 2163)
        epsg_from (str): EPSG code to transform longitude, latitude from (default: 4326)
        is_xy (bool): Boolean for if the input coordinates are already in (x, y, [z]) format

        """
        # coords should contain [[lon1, lat1, alt1],[lon2,...]]
        # Units for altitude should be meters

        self.coordinate = coordinate
        self.epsg_proj = epsg_proj
        self.epsg_from = epsg_from
        self.is_xy = is_xy
        self.transformer = Transformer.from_crs(
            self.epsg_from, self.epsg_proj, always_xy=True
        )

        # convert input coordinates to X, Y
        if not self.is_xy:
            self.lonlat_coords = self.coordinate
            self.xy_coords = self.project_coords()
        else:
            self.xy_coords = self.coordinate

        self.np_coords = np.array(self.xy_coords)
        self.dimensions = len(self.xy_coords)

        # need linestring for each dimension
        # x, y, [z]
        # x, z, [y]
        # y, z, [x]

        if self.dimensions == 2:
            self.xy = Point((self.xy_coords[0], self.xy_coords[1]))

        if self.dimensions == 3:

            self.xy = Point(
                (self.xy_coords[0], self.xy_coords[1], self.xy_coords[2]))
            self.xz = Point(
                (self.xy_coords[0], self.xy_coords[2], self.xy_coords[1]))
            self.yz = Point(
                (self.xy_coords[1], self.xy_coords[2], self.xy_coords[0]))

    def project_coords(self):
        """
        Projects the longitude, latitude coordinates to X, Y (meters)


        Returns:
        -------
        xy_coords (List): List of coordinates in (X, Y, [Z])

        """
        xy_coords = []
        for coordinate in self.coordinate:
            x, y = self.transformer.transform(coordinate[0], coordinate[1])
            if len(coordinate) > 2:
                xy_coords.append((x, y, coordinate[2]))
            else:
                xy_coords.append((x, y))

        return xy_coords

    def plot(self, geo_obj=None, label_fontsize=12):
        """
        Plot the 3D Point using Matplotlib.

        Args:
        ----
        geo_obj (GeoLineString): Second GeoLineString to add to plot (Optional)
        label_fontsize (int):  Fontsize for the axes labels


        Returns:
        -------
        fig: Matplotlib figure
        ax: Matplotlin axes

        """

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.plot(self.np_coords[:, 0],
                self.np_coords[:, 1], self.np_coords[:, 2])

        if geo_obj is not None:
            ax.plot(
                geo_obj.np_coords[:, 0],
                geo_obj.np_coords[:, 1],
                geo_obj.np_coords[:, 2],
            )
        ax.set_xlabel("x", fontsize=label_fontsize)
        ax.set_ylabel("y", fontsize=label_fontsize)
        ax.set_zlabel("z", fontsize=label_fontsize)
        return fig, ax

    def intersects(self, geo_obj):
        """
        Determines if the GeoPoint intersects with geo_obj

        Args:
        ----
        geo_obj (GeoPoint or GeoLineString): Second geo_obj for comparison

        Returns:
        -------
        bool: True if GeoLineStrings intersect, False otherwise

        """
        intersection_points = self.intersection(geo_obj)

        if len(intersection_points) > 0:
            return True
        else:
            return False

    def intersection(self, geo_obj, lonlat=False):
        """
        Determines where the GeoPoint intersects with geo_obj

        Args:
        ----
        geo_obj (GeoPoint or GeoLineString): Second geo_obj for comparison
        lonlat (bool): Format of output coordinates. True returns the coordinates in longitude, latitude. False returns coordinates in x, y

        Returns:
        -------
        intersection (List): Intersection coordinates

        """

        intersection = nb.typed.List.empty_list(
            nb.types.UniTuple(nb.float64, self.dimensions))

        inter1 = self.xy.intersection(geo_obj.xy)
        inter2 = self.xz.intersection(geo_obj.xz)
        inter3 = self.yz.intersection(geo_obj.yz)

        if not hasattr(inter1, "geoms"):
            xy = np.array(inter1.coords)[0]
            n_xy_intersections = 1

        else:
            n_xy_intersections = len(inter1.geoms)

        if not hasattr(inter2, "geoms"):
            xz = np.array(inter2.coords)[0]
            n_xz_intersections = 1
        else:
            n_xz_intersections = len(inter2.geoms)

        if not hasattr(inter3, "geoms"):
            yz = np.array(inter3.coords)[0]
            n_yz_intersections = 1
        else:
            n_yz_intersections = len(inter3.geoms)

        for i in range(n_xy_intersections):

            for j in range(n_xz_intersections):

                for k in range(n_yz_intersections):

                    if hasattr(inter1, "geoms"):
                        xy = np.array(inter1.geoms[i].coords)
                    else:
                        xy = np.array(inter1.coords)

                    if hasattr(inter2, "geoms"):
                        xz = np.array(inter2.geoms[j].coords)
                    else:
                        xz = np.array(inter2.coords)

                    if hasattr(inter3, "geoms"):
                        yz = np.array(inter3.geoms[k].coords)
                    else:
                        yz = np.array(inter3.coords)

                    fast_intersection_append(xy, xz, yz, intersection)

            intersection = np.unique(intersection, axis=0)

            if lonlat:
                lon, lat, alt = self.transformer.transform(
                    intersection[:, 0],
                    intersection[:, 1],
                    intersection[:, 2],
                    direction="INVERSE",
                )
                intersection = np.array(
                    [[lon[i], lat[i], alt[i]] for i in range(len(lon))]
                )
            return intersection
