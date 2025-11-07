from src.Objetos.Objeto3D import Objeto3D, ObjectType
import numpy as np


class CurvaBSpline(Objeto3D):
    def __init__(
        self,
        name,
        coordenadas=[(0, 0, 0), (1, 1, 1)],
        obj_type=ObjectType.BSPLINE_CURVE,
        color="#000000",
    ):
        super().__init__(name, coordenadas, obj_type, color)

        # As coordenadas guardadas são os pontos de controle

        self.__MBS = (
            np.array([[-1, 3, -3, 1],
                      [3, -6, 3, 0],
                      [-3, 0, 3, 0],
                      [1, 4, 1, 0]]) / 6
        )

        self.__delta = 0.1
        self.__n = int(1 / self.__delta)

        self.__e_forward_differences = np.array(
            [
                [0, 0, 0, 1],
                [self.__delta**3, self.__delta**2, self.__delta, 0],
                [6 * self.__delta**3, 2 * self.__delta**2, 0, 0],
                [6 * self.__delta**3, 0, 0, 0],
            ]
        )

    def generate_curve(self, control_points_normalized):
        points = []
        for i in range(len(control_points_normalized) - 3):
            g_x, g_y = np.array(control_points_normalized[i:i+4]).T

            c_x = np.matmul(self.__MBS, g_x)
            c_y = np.matmul(self.__MBS, g_y)

            x, dx, d2x, d3x = np.matmul(self.__e_forward_differences, c_x)
            y, dy, d2y, d3y = np.matmul(self.__e_forward_differences, c_y)

            points.extend(self.__fwd_diff(x, dx, d2x, d3x, y, dy, d2y, d3y))

        return points
    
    def __fwd_diff(self, x, dx, d2x, d3x, y, dy, d2y, d3y) -> list[tuple[float, float]]:
        points = [(x, y)]

        for _ in range(self.__n):
            x += dx
            dx += d2x
            d2x += d3x

            y += dy
            dy += d2y
            d2y += d3y 
            points.append((x, y))

        return points
