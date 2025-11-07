from src.Objetos.Objeto3D import Objeto3D, ObjectType

class WireFrame(Objeto3D):
    def __init__(self, name, coordenadas=[(0, 0), (1, 1), (0, 2)],
                 obj_type=ObjectType.WIREFRAME, color="000000", fill=False,
                 edges:list[tuple[tuple[float]]] = []):
        super().__init__(name, coordenadas, obj_type, color, edges=edges)
        self.__fill = fill

    @property
    def fill(self) -> bool:
        return self.__fill
