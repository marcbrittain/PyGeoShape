from typing import List
from shapely.geometry import LineString
from pyproj import Transformer
import numpy as np
import matplotlib.pyplot as plt


class GeoLineString:
    """Base GeoLinString type"""

    def __init__(
        self,
        coords: List,
        epsg_proj: str = "epsg:2163",
        epsg_from: str = "epsg:4326",
        is_xy: bool = False,
    ):
        """
        Args:
        ----

        coords (List): Input coordinates in (longitude, latitude, altitude) or (x, y, z)
        epsg_proj (str): EPSG code to transform longitude, latitude into x, y (default: 2163)
        epsg_from (str): EPSG code to transform longitude, latitude from (default: 4326)
        is_xy (bool): Boolean for if the input coordinates are already in (x, y, [z]) format

        """
        # coords should contain [[lon1, lat1, alt1],[lon2,...]]
        # Units for altitude should be meters

        self.coords = coords
        self.epsg_proj = epsg_proj
        self.epsg_from = epsg_from
        self.is_xy = is_xy
        self.transformer = Transformer.from_crs(
            self.epsg_from, self.epsg_proj, always_xy=True
        )

        # convert input coordinates to X, Y
        if not self.is_xy:
            self.lonlat_coords = self.coords
            self.xy_coords = self.project_coords()
        else:
            self.xy_coords = self.coords

        self.np_coords = np.array(self.xy_coords)
        self.length = self.geolinestring_length()
        dimensions = len(self.xy_coords[0])

        # need linestring for each dimension
        # x, y, [z]
        # x, z, [y]
        # y, z, [x]

        if dimensions == 2:
            self.xy = LineString([(coord[0], coord[1])
                                 for coord in self.xy_coords])

        if dimensions == 3:

            self.xy = LineString(
                [(coord[0], coord[1], coord[2]) for coord in self.xy_coords]
            )
            self.xz = LineString(
                [(coord[0], coord[2], coord[1]) for coord in self.xy_coords]
            )
            self.yz = LineString(
                [(coord[1], coord[2], coord[0]) for coord in self.xy_coords]
            )

    def geolinestring_length(self):
        """
        Determines the length of the GeoLineString in meters


        Returns:
        -------
        length (float): Length of GeoLineString

        """

        # sqrt( (x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)
        # then take sum for each segment for total distance
        length = np.sum(
            np.sqrt(np.sum(np.square(np.diff(self.np_coords, axis=0)), axis=1)))
        return length

    def project_coords(self):
        """
        Projects the longitude, latitude coordinates to X, Y (meters)


        Returns:
        -------
        xy_coords (List): List of coordinates in (X, Y, [Z])

        """
        xy_coords = []
        for coordinate in self.coords:
            x, y = self.transformer.transform(coordinate[0], coordinate[1])
            if len(coordinate) > 2:
                xy_coords.append((x, y, coordinate[2]))
            else:
                xy_coords.append((x, y))

        return xy_coords

    def plot(self, geo_obj=None, label_fontsize=12):
        """
        Plot the 3D LineString using Matplotlib.

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
        Determines if the GeoLineString intersects with geo_obj

        Args:
        ----
        geo_obj (GeoLineString): Second GeoLineString for comparision

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
        Determines where the GeoLineString intersects with geo_obj

        Args:
        ----
        geo_obj (GeoLineString): Second GeoLineString for comparision
        lonlat (bool): Format of output coordinates. True returns the coordinates in longitude, latitude. False returns coordinates in x, y

        Returns:
        -------
        intersection (List): Intersection coordinates

        """
        xy_check = self.xy.intersects(geo_obj.xy)
        xz_check = self.xz.intersects(geo_obj.xz)
        yz_check = self.yz.intersects(geo_obj.yz)

        intersection = []

        if all([xy_check, xz_check, yz_check]):

            inter1 = self.xy.intersection(geo_obj.xy)
            inter2 = self.xz.intersection(geo_obj.xz)
            inter3 = self.yz.intersection(geo_obj.yz)

            if not hasattr(inter1, "geoms"):
                xy = list(inter1.coords)[0]
                n_xy_intersections = 1
            else:
                n_xy_intersections = len(inter1.geoms)

            if not hasattr(inter2, "geoms"):
                xz = list(inter2.coords)[0]
                n_xz_intersections = 1
            else:
                n_xz_intersections = len(inter2.geoms)

            if not hasattr(inter3, "geoms"):
                yz = list(inter3.coords)[0]
                n_yz_intersections = 1
            else:
                n_yz_intersections = len(inter3.geoms)

            for i in range(n_xy_intersections):

                for j in range(n_xz_intersections):

                    for k in range(n_yz_intersections):

                        if hasattr(inter1, "geoms"):
                            xy = list(inter1.geoms[i].coords)
                        else:
                            xy = list(inter1.coords)

                        if hasattr(inter2, "geoms"):
                            xz = list(inter2.geoms[j].coords)
                        else:
                            xz = list(inter2.coords)

                        if hasattr(inter3, "geoms"):
                            yz = list(inter3.geoms[k].coords)
                        else:
                            yz = list(inter3.coords)

                        for ii in range(len(xy)):

                            x_y_z = xy[ii]
                            x_z_y = (x_y_z[0], x_y_z[2], x_y_z[1])

                            if x_z_y in xz:

                                y_z_x = (x_y_z[1], x_y_z[2], x_y_z[0])

                                if y_z_x in yz:

                                    intersection.append(x_y_z)

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
