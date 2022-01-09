import numba as nb
import numpy as np


@nb.njit
def fast_intersection_append(xy, xz, yz, intersection):

    for ii in range(len(xy)):

        x, y_check, _ = xy[ii]

        idx = np.where(xz[:, 0] == x)[0]

        if len(idx) > 0:

            for jj in range(len(idx)):

                z = xz[idx[jj], 1]

                yz_idx = np.where(yz[:, 1] == z)[0]

                if len(yz_idx) > 0:

                    y = yz[yz_idx, 0]

                    if y_check in y:
                        intersection.append((x, y_check, z))
