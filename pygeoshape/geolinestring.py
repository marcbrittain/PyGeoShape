from shapely.geometry import LineString, Point
from typing import List
from pyproj import Transformer
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class GeoLineString:
    def __init__(self, coords: List, epsg_proj: str = 'epsg:2163', epsg_from: str = 'epsg:4326', isXY: bool = False):
        # coords should contain [[lon1, lat1, alt1],[lon2,...]]
        # Units for altitude should be meters

        self.coords = coords
        self.epsg_proj = epsg_proj
        self.epsg_from = epsg_from
        self.isXY = isXY
        self.transformer = Transformer.from_crs(
            self.epsg_from, self.epsg_proj, always_xy=True)

        # convert input coordinates to X, Y
        if not self.isXY:
            self.lonlat_coords = self.coords
            self.xy_coords = self.project_coords()
        else:
            self.xy_coords = self.coords

        self.np_coords = np.array(self.xy_coords)
        dimensions = len(self.xy_coords[0])

        # need linestring for each dimension
        # x, y, [z]
        # x, z, [y]
        # y, z, [x]

        if dimensions == 2:
            self.xy = LineString([(coord[0], coord[1])
                                 for coord in self.xy_coords])

        if dimensions == 3:

            self.xy = LineString([(coord[0], coord[1], coord[2])
                                 for coord in self.xy_coords])
            self.xz = LineString([(coord[0], coord[2], coord[1])
                                 for coord in self.xy_coords])
            self.yz = LineString([(coord[1], coord[2], coord[0])
                                 for coord in self.xy_coords])

    def project_coords(self):

        xy_coords = []
        for coordinate in self.coords:
            x, y = self.transformer.transform(coordinate[0], coordinate[1])
            if len(coordinate) > 2:
                xy_coords.append((x, y, coordinate[2]))
            else:
                xy_coords.append((x, y))

        return xy_coords

    def plot(self, geo_obj=None, label_fontsize=12):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(self.np_coords[:, 0],
                self.np_coords[:, 1], self.np_coords[:, 2])

        if geo_obj is not None:
            ax.plot(geo_obj.np_coords[:, 0],
                    geo_obj.np_coords[:, 1], geo_obj.np_coords[:, 2])
        ax.set_xlabel('x', fontsize=label_fontsize)
        ax.set_ylabel('y', fontsize=label_fontsize)
        ax.set_zlabel('z', fontsize=label_fontsize)

    def intersects(self, geo_obj):
        """
        Does current GeoLineString intersect with geo_obj?

        """
        xy_check = self.xy.intersects(geo_obj.xy)
        xz_check = self.xz.intersects(geo_obj.xz)
        yz_check = self.yz.intersects(geo_obj.yz)

        if all([xy_check, xz_check, yz_check]):
            return True

    def intersection(self, geo_obj, lonlat=False):
        """
        Does current GeoLineString intersect with geo_obj?

        """
        xy_check = self.xy.intersects(geo_obj.xy)
        xz_check = self.xz.intersects(geo_obj.xz)
        yz_check = self.yz.intersects(geo_obj.yz)

        intersection = []

        if all([xy_check, xz_check, yz_check]):

            inter1 = self.xy.intersection(geo_obj.xy)
            inter2 = self.xz.intersection(geo_obj.xz)
            inter3 = self.yz.intersection(geo_obj.yz)

            try:
                xy = list(inter1.coords)[0]
                n_xy_intersections = 1
            except:
                n_xy_intersections = len(inter1.geoms)

            try:
                xz = list(inter2.coords)[0]
                n_xz_intersections = 1
            except:
                n_xz_intersections = len(inter2.geoms)

            try:
                yz = list(inter3.coords)[0]
                n_yz_intersections = 1
            except:
                n_yz_intersections = len(inter3.geoms)

            for i in range(n_xy_intersections):

                for j in range(n_xz_intersections):

                    for k in range(n_yz_intersections):

                        try:
                            xy = list(inter1.geoms[i].coords)
                        except:
                            xy = list(inter1.coords)

                        try:
                            xz = list(inter2.geoms[j].coords)
                        except:
                            xz = list(inter2.coords)

                        try:
                            yz = list(inter3.geoms[k].coords)
                        except:
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
                    intersection[:, 0], intersection[:, 1], intersection[:, 2], direction='INVERSE')
                intersection = np.array(
                    [[lon[i], lat[i], alt[i]] for i in range(len(lon))])
            return intersection
