import tkinter as tk


import src.ViewPort as VP
from src.Objetos import Objeto3D as Obj3D
from src.TransformationUtils.Clipper import Clipper
from src.TransformationUtils.Transformator import Transformator


class Window:
    def __init__(self, master=None, width_=600, height_=400):
        self.__viewport_frame = tk.Frame(master)
        self.__viewport_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 80))

        # Title: Viewport
        tk.Label(
            self.__viewport_frame, text="Viewport", font="System 12 bold", pady=5
        ).pack()

        self.__viewport = VP.ViewPort(self.__viewport_frame, width_, height_)
        # using the normalized device coordinates
        self.__clipper = Clipper("SCN", "L-B")
        self.__transformator = Transformator("SCN", height_, width_)

        self.__zoom_step = 0.1
        self.__width_drawings = 2

    def unrotate_vector(self, dx: float, dy: float, dz:float=0) -> tuple[float, float, float]:
        return self.__transformator.unrotate_vector(dx, dy, dz)
    
    def set_normalization_matrix(self, angle: float = 0):
        self.__transformator.set_normalization_matrix(angle)
    
    def draw_object(self, object: Obj3D.Objeto3D):
        obj_coords = object.calculate_perspective_normalized_coords(self.__transformator.dop, self.__transformator.perspective_matrix, self.__transformator.matrix)

        if not obj_coords:
            return

        if object.obj_type == Obj3D.ObjectType.POINT:
            self.draw_point(obj_coords[0], object.color)
        elif object.obj_type == Obj3D.ObjectType.LINE:
            self.draw_line(obj_coords, object.color)
        elif object.obj_type == Obj3D.ObjectType.WIREFRAME:
            self.draw_wireframe(obj_coords, object.edges, object.color, object.fill)
        elif object.obj_type in [Obj3D.ObjectType.BEZIER_CURVE, Obj3D.ObjectType.BSPLINE_CURVE]:
            self.draw_curve(object.generate_curve(obj_coords), object.color)
        elif object.obj_type in [Obj3D.ObjectType.BEZIER_SURFACE, Obj3D.ObjectType.BSPLINE_SURFACE]:
            self.draw_surface(object.generate_curves(obj_coords), object.color)

    def draw_point(self, coords: tuple[float], color: str) -> None:
        # if the point is outside the window, it is not drawn
        self.__viewport.draw_oval(self.__clipper.clip_point(coords),
                                  color, self.__width_drawings)

    def draw_line(self, coords: list[tuple[float]], color: str) -> None:
        self.__viewport.draw_line(self.__clipper.clip_line(coords),
                                  color, self.__width_drawings)

    def draw_wireframe(self, coords: list[tuple[float]],
                       edges:list[tuple[int]],
                       color: str, fill=False) -> None:
        self.__viewport.draw_polygon(*self.__clipper.clip_polygon(coords, edges),
                                     color, self.__width_drawings, fill)

    def draw_curve(self, coords: list[tuple[float]], color: str) -> None:
        self.__viewport.draw_curve(self.__clipper.clip_curve(coords),
                                   color, self.__width_drawings)

    def draw_surface(self, coords: list[list[list[float]]], color: str) -> None:
        for curve in coords:
            self.draw_curve(curve, color)

    
    def __update_width_drawings(self):
        self.__width_drawings = 2 * self.__transformator.scaling_factor

    def delete(self, object_name="all"):
        if object_name == "all":
            self.__viewport.delete("all")

    def __zoom(self, zoom_step: float) -> None:
        self.__transformator.scaling_factor *= 1 + zoom_step
        self.__update_width_drawings()
        self.set_normalization_matrix()

    def zoom_in(self) -> None:
        self.__zoom(self.__zoom_step)

    def zoom_out(self) -> None:
        self.__zoom(-self.__zoom_step)

    def pan(self, dx: float, dy: float) -> None:
        self.__transformator.update_center(dx, dy)
        self.set_normalization_matrix()

    def draw_viewport_outer_frame(self) -> None:
        self.__viewport.draw_outer_frame()

    # works for both lines and polygons algorithms
    def set_clipping_algorithm(self, algorithm: str) -> None:
        self.__clipper.set_clipping_algorithm(algorithm)
    
    # define the world limits for clipping
    def set_clipping_window(self, window: str) -> None:
        self.__clipper.set_window(window)
