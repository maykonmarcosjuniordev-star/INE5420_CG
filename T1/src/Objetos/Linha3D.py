from src.Objetos.Objeto3D import Objeto3D, ObjectType

class Linha3D(Objeto3D):
    def __init__(self, name, coordenadas=[(0, 0, 0), (1, 1, 1)],
                 obj_type=ObjectType.LINE, color="#000000"):
        super().__init__(name, coordenadas, obj_type, color)
