from src.Objetos.Objeto3D import Objeto3D, ObjectType

class Ponto3D(Objeto3D):
    def __init__(self, name:str,
                 coordenadas=[(0, 0, 0)],
                 obj_type=ObjectType.POINT,
                 color="#000000") -> None:
        super().__init__(name, coordenadas, obj_type, color)

