import math
from src.Objetos.Objeto3D import Objeto3D, ObjectType
import numpy as np


class BSplineSurface(Objeto3D):
    def __init__(
        self,
        name: str,
        coords: list[tuple[float]],
        obj_type=ObjectType.BSPLINE_SURFACE,
        color="#000000",
        curves: list[tuple[int]] = [],
    ):
        new_coords = []
        for curve in coords:
            new_coords.extend(curve)
        super().__init__(name, new_coords, obj_type, color, curves)

        self.__MBS = (
            np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]]) / 6
        )

    def generate_curves(self, ctrl_pts_) -> list[list[list[float]]]:
        NN = len(ctrl_pts_)
        n_root = int(math.sqrt(NN))
        if n_root < 4 or n_root > 20:
            raise ValueError("The control points matrix must be between 4x4 and 20x20 in size")

        if n_root**2 != NN:
            raise ValueError("The number of control points is not a perfect square")

        curves = []
        for i in range(n_root - 3):
            for j in range(n_root - 3):
                submatrix = []
                for k in range(4):
                    row_start = (i + k) * n_root + j
                    row_end = row_start + 4
                    submatrix.append(ctrl_pts_[row_start:row_end])
                curves.extend(self.generate_curve(np.array(submatrix)))
        return curves

    def generate_curve(self, ctrl_points) -> list[list[list[float]]]:
        points = []

        NS = NT = 20
        DS = 1.0 / (NS - 1)
        DT = 1.0 / (NT - 1)

        E_s = self.__get_delta_matrix(DS)
        E_t = self.__get_delta_matrix(DT).transpose()

        G = np.array(ctrl_points)
        g_x, g_y = G[:, :, 0], G[:, :, 1]

        c_x = self.__MBS @ g_x @ self.__MBS.transpose()
        c_y = self.__MBS @ g_y @ self.__MBS.transpose()

        DDx = E_s @ c_x @ E_t
        DDy = E_s @ c_y @ E_t

        DDx2 = np.copy(DDx).T
        DDy2 = np.copy(DDy).T

        points.extend(self.__create_subcurve(DDx, DDy, NS, NT))
        points.extend(self.__create_subcurve(DDx2, DDy2, NT, NS))

        return points

    def __fwd_diff(
        self, n, x, dx, d2x, d3x, y, dy, d2y, d3y
    ) -> list[tuple[float, float]]:
        points = [(x, y)]

        for _ in range(n):
            x += dx
            dx += d2x
            d2x += d3x

            y += dy
            dy += d2y
            d2y += d3y
            points.append((x, y))

        return points

    def __get_delta_matrix(self, d: float) -> np.ndarray:
        return np.array(
            [
                [0, 0, 0, 1],
                [d**3, d**2, d, 0],
                [6 * d**3, 2 * d**2, 0, 0],
                [6 * d**3, 0, 0, 0],
            ]
        )

    def __create_subcurve(
        self, DDx: np.ndarray, DDy: np.ndarray, main_n: int, minor_n: int
    ) -> list[list[tuple[float, float]]]:
        coordinates = []

        for _ in range(main_n + 1):
            coordinates.append(self.__fwd_diff(minor_n, *DDx[0], *DDy[0]))

            for i in range(len(DDx) - 1):
                for j in range(len(DDx[0])):
                    DDx[i][j] += DDx[i + 1][j]
                    DDy[i][j] += DDy[i + 1][j]

        return coordinates
