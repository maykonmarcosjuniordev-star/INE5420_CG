import tkinter as tk

from src.Objetos import Objeto3D as Obj3D
from src.WindowUtilis.DisplayFileFrame import DisplayFileFrame

class DisplayFile:
    def __init__(self, root, transformations_function: callable):
        self.__objects = []
        self.__frame = DisplayFileFrame(root, transformations_function)
        self.__frame.pack(side=tk.TOP)

    def add_object(self, new_object: Obj3D.Objeto3D) -> None:
        if new_object not in self.__objects and isinstance(new_object, Obj3D.Objeto3D):
            self.__objects.append(new_object)
            self.__frame.add_new_object(new_object.name, new_object.obj_type)

    def remove_object(self, obj: Obj3D.Objeto3D) -> None:
        if obj in self.__objects:
            self.__objects.remove(obj)

    @property
    def objects(self) -> list[Obj3D.Objeto3D]:
        return self.__objects
