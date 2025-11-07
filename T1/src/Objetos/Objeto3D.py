import numpy as np
from enum import Enum
from random import randint
from abc import ABC
from src.TransformationUtils.Transformations import Rotation3DType, Transformation

class ObjectType(Enum):
    OBJECT3D = 1
    POINT = 2
    LINE = 3
    WIREFRAME = 4
    BEZIER_CURVE = 5
    BSPLINE_CURVE = 6
    BEZIER_SURFACE = 7
    BSPLINE_SURFACE = 8


class Objeto3D(ABC):
    def __init__(self, name: str, coords: list[tuple[float]],
                 obj_type=ObjectType.OBJECT3D.value, color="#000000",
                 edges:list[tuple[int]] = []):
        self.__name = None
        self.__coords = None
        self.__obj_type = None
        self.certify_format(name, coords, obj_type)
        self.__color = color
        self.__edges = edges
        self.__edge_order_matter = True
        if not self.__edges:
            self.__edge_order_matter = False
            L = len(self.__coords)
            self.__edges = [(i, (i+1)%L) for i in range(L)]

    def translation(self, dx: float, dy: float, dz: float=0) -> None:
        matrix = self.get_translation_matrix(dx, dy, dz)
        self.__coords = self.calculate_coords(matrix)

    def scaling(self, sx: float, sy: float, sz:float=0) -> None:
        cx, cy, cz = self.geometric_center()
        temp_matrix = np.matmul(
            self.get_translation_matrix(-cx, -cy, -cz),
            self.get_scaling_matrix(sx, sy, sz)
        )
        scaling_matrix = np.matmul(temp_matrix,
                                   self.get_translation_matrix(cx, cy, cz))

        self.__coords = self.calculate_coords(scaling_matrix)

    def rotation(self,
                 rotation_type: str="RotationType.Z",
                 angle: float=90,
                 p1:tuple[float, float, float]=(0,0,0),
                 p2:tuple[float, float, float]=(0,0,0)) -> None:
        matrix = []

        if rotation_type == str(Rotation3DType.any_axis):
            matrix = self.__aux_rotation(p1, p2, angle)
        elif rotation_type == str(Rotation3DType.X):
            matrix = self.get_X_rotation_matrix(angle)
        elif rotation_type == str(Rotation3DType.Y):
            matrix = self.get_Y_rotation_matrix(angle)
        elif rotation_type == str(Rotation3DType.Z):
            matrix = self.get_Z_rotation_matrix(angle)
        elif rotation_type == str(Rotation3DType.center_X):
            center = self.geometric_center()
            p2 = (center[0] + 1, center[1], center[2])
            matrix = self.__aux_rotation(center, p2, angle)
        elif rotation_type == str(Rotation3DType.center_Y):
            center = self.geometric_center()
            p2 = (center[0], center[1] + 1, center[2])
            matrix = self.__aux_rotation(center, p2, angle)
        elif rotation_type == str(Rotation3DType.center_Z):
            center = self.geometric_center()
            p2 = (center[0], center[1], center[2] + 1)
            matrix = self.__aux_rotation(center, p2, angle)
        else:
            print("Invalid rotation type")
            return

        self.__coords = self.calculate_coords(matrix)

    def apply_transformations(self, transformations: list[Transformation],
                              transform_vector_function: callable) -> None:
        for transform in transformations:
            match transform.__class__.__name__:
                case "Translation":
                    # The user-entered coordinates represent the desired translation,
                    # but when the window is rotated, 
                    # the object's coordinates need to be updated differently.
                    # This is achieved by using the unrotated vector.
                    self.translation(*transform_vector_function(transform.dx, transform.dy, transform.dz))
                case "Rotation":
                    self.rotation(
                        transform.rotation_type,
                        transform.angle,
                        transform.p1,
                        transform.p2
                    )
                case "Scaling":
                    self.scaling(transform.sx, transform.sy, transform.sz)

    def get_translation_matrix(self, dx: float, dy: float, dz:float=0) -> np.array:
        return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [dx, dy, dz, 1]])

    def get_scaling_matrix(self, sx: float, sy: float, sz: float=0) -> np.array:
        return np.array([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]])

    def get_X_rotation_matrix(self, angle: float) -> np.array:
        theta = np.radians(angle)
        return np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(theta), np.sin(theta), 0],
                [0,-np.sin(theta), np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

    def get_Y_rotation_matrix(self, angle: float) -> np.array:
        theta = np.radians(angle)
        return np.array(
            [
                [np.cos(theta), 0,-np.sin(theta), 0],
                [0, 1, 0, 0],
                [np.sin(theta), 0, np.cos(theta), 0],
                [0, 0, 0, 1],
            ]
        )

    def get_Z_rotation_matrix(self, angle: float) -> np.array:
        theta = np.radians(angle)
        return np.array(
            [
                [ np.cos(theta), np.sin(theta), 0, 0],
                [-np.sin(theta), np.cos(theta), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

    def geometric_center(self) -> tuple[float]:
        return tuple(np.mean(self.__coords, axis=0))

    def get_vector_angle(self,
                         p1:tuple[float, float, float],
                         p2:tuple[float, float, float]) -> tuple[float, float, float]:
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        Qx = np.rad2deg(np.arctan2(dx, np.sqrt(dy**2 + dz**2)))
        Qy = np.rad2deg(np.arctan2(dy, np.sqrt(dx**2 + dz**2))) 
        Qz = np.rad2deg(np.arctan2(np.sqrt(dy**2 + dx**2), dz))
        return Qx, Qy, Qz

    def __aux_rotation(self,
                       P:tuple[float, float, float],
                       A:tuple[float, float, float],
                       angle: float) -> np.array:
        dx, dy, dz = P
        A = (*A, 1)

        # Translada o eixo A para a origem
        T = self.get_translation_matrix(-dx, -dy, -dz)
        A = np.dot(A, T)

        # Rotaciona o vetor A no eixo x para ele ficar sobre o plano xy
        Qx = np.degrees(np.arctan2(A[2], A[0]))
        Rx = self.get_X_rotation_matrix(Qx)
        A = np.dot(A, Rx)

        # Rotaciona o vetor A no eixo z para ele se alinhar ao eixo y
        Qz = np.degrees(np.arctan2(A[0], A[1]))
        Rz = self.get_Z_rotation_matrix(Qz)

        # Faz a rotação principal ao redor do eixo y
        Ry = self.get_Y_rotation_matrix(angle)

        # Reverte as transformações auxiliares
        Rz_reverse = self.get_Z_rotation_matrix(-Qz)
        Rx_reverse = self.get_X_rotation_matrix(-Qx)
        T_reverse = self.get_translation_matrix(dx, dy, dz)

        return T @ Rx @ Rz @ Ry @ Rz_reverse @ Rx_reverse @ T_reverse

    @property
    def name(self) -> str:
        return self.__name

    @property
    def coordinates(self) -> list[tuple[float]]:
        coords = self.__convert_to_tuples_list(self.__coords)
        return coords

    @property
    def edges(self) -> list[tuple[int]]:
        return self.__edges

    @property
    def obj_type(self) -> str:
        return self.__obj_type

    @property
    def color(self) -> str:
        return self.__color
    
    @property
    def edge_order_matter(self) -> bool:
        return self.__edge_order_matter

    def __str__(self):
        coords = [tuple(round(i, 2) for i in j) for j in self.coordinates]
        return f"{self.obj_type}: - {self.__name} - {coords}"

    def __convert_to_tuples_list(self, coords: np.ndarray) -> list[tuple[float]]:
        return [tuple(float(j) for j in i) for i in coords.tolist()]

    def calculate_coords(self, matrix: np.ndarray) -> list[tuple[float]]:
        R = np.array(
            [
                np.dot(np.array([coord[0], coord[1], coord[2], 1]), matrix)[:-1]
                for coord in self.__coords
            ]
        )

        return R

    def calculate_perspective_normalized_coords(self, d: int, mper: np.ndarray,
                                                normalize_matrix: np.ndarray):
        normalized_coords = []
        for x, y, z in self.__coords:
            if z < d:
                print("A coordenada z do objeto é menor do",
                      f"que o mínimo desenhado (mínimo = {d}, z = {z})")
                return []
            x, y, z, w = np.dot(mper, [x, y, z, 1])
            normalized_coord = np.dot([x / w, y / w, d, 1], normalize_matrix)
            normalized_coords.append([normalized_coord[0], normalized_coord[1]])

        return normalized_coords

    def certify_format(self, name:str, coords_:list[tuple[float]],
                       obj_type:ObjectType) -> tuple[str, np.array, ObjectType]:
        coords = coords_[:]
        if not isinstance(name, str):
            print("Invalid name for", name, ", renamed to 'obj'")
            name = 'obj'
        if len(coords) == 0:
            print("No coordinates defined for", name, ", defined as (0,0,0)")
            coords = [(0,0,0)]
        if obj_type.name not in ObjectType.__members__:
            print("Invalid object type", obj_type)
            print("Object type not defined for", name, "-> automatically guessed")
            if len(coords) == 1:
                obj_type = ObjectType.POINT
            elif len(coords) == 2:
                obj_type = ObjectType.LINE
            else:
                obj_type = ObjectType.WIREFRAME
        if len(coords) == 1 and obj_type != ObjectType.POINT:
            print("Wrong object type")
            obj_type = ObjectType.POINT
        if len(coords) == 2 and obj_type != ObjectType.LINE:
            print("Wrong object type")
            obj_type = ObjectType.LINE
        if len(coords) > 2 and obj_type in [ObjectType.POINT,
                                            ObjectType.LINE]:
            print("Wrong object type")
            obj_type = ObjectType.WIREFRAME
        if obj_type.name in [ObjectType.BEZIER_CURVE,
                        ObjectType.BSPLINE_CURVE] and len(coords) < 4:
            added_points = [(randint(-1000, 1000),
                             randint(-1000, 1000),
                             randint(-1000, 1000)) for _ in range(4 - len(coords))]
            print("Insufficient Control Points for Curve")
            print(f"The following random points will be added to the coordinates: {added_points}")
            coords.extend(added_points)
        if not all(isinstance(i, tuple) for i in coords):
            print("Invalid format for coordinates, should be a list of tuples")
            coords = [tuple(i) for i in coords]
        if any(len(i) < 3 for i in coords):
            print("Invalid format for coordinates, 3 values are needed for each point")
            print("points with less than 3 values will be added a 0")
            for i in range(len(coords)):
                if len(coords[i]) < 3:
                    coords[i] = (*coords[i], 0.0)
        if any(len(i) > 3 for i in coords):
            print(
                "Invalid format for coordinates, only 3 values are needed for each point"
            )
            print("extra values will be removed")
            coords = [(j[i] for i in range(3)) for j in coords]
        if not all(isinstance(i, (float, float, float)) for i in coords):
            try:
                coords = [tuple(float(i) for i in j) for j in coords]
            except:
                print("Invalid format for coordinates, the tuples should be made of floats")
                print("coordinates will be remanaged to (i, i, i)")
                coords = [(i, i, i) for i in range(len(coords))]
        self.__name = name
        self.__coords = np.array(coords)
        self.__obj_type = obj_type
