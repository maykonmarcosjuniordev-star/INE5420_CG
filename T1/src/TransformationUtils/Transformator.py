import numpy as np
from src.Objetos.Ponto3D import Ponto3D
from math import sqrt

class Transformator:
    def __init__(self, system:str="SCN",
                 height: int = 400,
                 width: int = 600):
        self.__system = system

        self.__xwmin = self.__ywmin = 0
        self.__xwmax = width
        self.__ywmax = height
        # middle point of the window
        self.__dop = round(width * (sqrt(3) / 2))
        self.__center = np.array([0, 0, self.__dop, 1])
        self.__cop = np.array([0, 0, 0, 1])
        self.__mper = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0],
             [0, 0, 1, 0], [0, 0, 1 / self.__dop, 0]]
        )
        self.__scaling_factor = 1

        self._normal_matrix = None
        self.obj = Ponto3D("generic_obj")
        # view up vector
        self.__viewup = np.array([0, 1, 0, 1])
        self.__viewup_angle = 0
        self.__vpn = np.array([self.__center[0], self.__center[1], self.__center[2] + 1])
        self.set_normalization_matrix(0)

    def set_normalization_matrix(self, angle: float = 0):
        self.__update_view_up_vector(angle)

        theta = self.__viewup_angle

        sx = 2 * self.__scaling_factor / (self.__xwmax - self.__xwmin)
        sy = 2 * self.__scaling_factor / (self.__ywmax - self.__ywmin)

        R = self.__get_rotate_matrix(theta)
        S = self.__get_scale_matrix(sx, sy)
        self._normal_matrix = np.matmul(np.matmul(self.__get_parallel_projection_matrix(), R), S)

    def __get_parallel_projection_matrix(self) -> np.ndarray:
        dx = self.__cop[0]
        dy = self.__cop[1]
        dz = self.__cop[2]

        T = self.__get_translate_matrix(-dx, -dy, -dz)
        Qx, Qy, _ = self.obj.get_vector_angle((dx, dy, 0), self.__vpn)
        Rx = self.obj.get_X_rotation_matrix(-Qx)
        Ry = self.obj.get_Y_rotation_matrix(-Qy)

        return T @ Rx @ Ry

    def __update_view_up_vector(self, theta: float):
        rotate_matrix = self.__get_rotate_matrix(theta)
        self.__viewup = np.matmul(self.__viewup, rotate_matrix)

        # The arctan2 function gives the angle that the vector makes with the positive x-axis.
        # To get the angle made with the positive y-axis, we subtract the result from pi/2.
        # The multiplication by -1 is needed to make the rotation counter-clockwise.
        self.__viewup_angle = np.degrees(-1 * (np.pi / 2 - np.arctan2(self.__viewup[1], self.__viewup[0])))

    def unrotate_vector(self, dx: float, dy: float, dz:float=0) -> tuple[float, float, float]:
        old_vector = np.array([dx, dy, dz, 1])
        rotate_matrix = self.__get_rotate_matrix(-self.__viewup_angle)
        new_vector = np.dot(old_vector, rotate_matrix)
        return new_vector[0], new_vector[1], new_vector[2]

    def __get_rotate_matrix(self, theta: float) -> np.array:
        return self.obj.get_Z_rotation_matrix(theta)

    def __get_translate_matrix(self, dx: float, dy: float, dz:float=0) -> np.array:
        return self.obj.get_translation_matrix(dx, dy, dz)

    def __get_scale_matrix(self, sx: float, sy: float, sz:float=0) -> np.array:
        return self.obj.get_scaling_matrix(sx, sy, sz)

    @property
    def matrix(self) -> np.array:
        return self._normal_matrix

    @property
    def dop(self) -> int:
        return self.__dop

    @property
    def perspective_matrix(self) -> np.ndarray:
        return self.__mper

    @property
    def scaling_factor(self) -> float:
        return self.__scaling_factor

    @scaling_factor.setter
    def scaling_factor(self, value: float):
        self.__scaling_factor = value

    @property
    def center(self) -> np.array:
        return self.__center

    def update_center(self, dx:float, dy:float):
        changed_x, changed_y, _ = self.unrotate_vector(dx, dy)
        translate_matrix = self.__get_translate_matrix(changed_x, changed_y)
        self.__center = np.dot(self.__center, translate_matrix)
        self.__vpn = np.array([self.__center[0], self.__center[1], self.__center[2] + 1])
        self.__cop = np.array([self.__center[0], self.__center[1], 0, 1])
