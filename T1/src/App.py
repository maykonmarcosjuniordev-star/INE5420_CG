import tkinter as tk
from tkinter import messagebox
import ast

import src.Window as WW
from src.Objetos import Objeto3D as Obj3D
from src.Objetos import Ponto3D as P3D
from src.Objetos import Linha3D as L3D
from src.Objetos import WireFrame as WF
from src.Objetos import CurvaBezier as BC
from src.Objetos import CurvaBSpline as BSC
from src.Objetos import BezierSurface as BBC
from src.Objetos import BSplineSurface as BSB
from src.OBJFileUtils import OBJParser as OBJP, OBJGenerator as OBJG
import src.WindowUtilis.DisplayFile as DF
import src.WindowUtilis.DrawWindow as DW
import src.WindowUtilis.OptionsFrame as OF


class App:
    def __init__(self, title="Window", width=960, height=720):
        self.__root = tk.Tk()

        self.__left_frame = tk.Frame(self.__root)
        self.__left_frame.pack(side=tk.LEFT, padx=(80, 0), fill=tk.X)

        self.__display_file = DF.DisplayFile(self.__left_frame,
                                             self.__apply_transformations)
        self.__root.title(title)
        self.__root.geometry(f"{width}x{height}")
        self.__root.resizable(False, False)

        self.__window = WW.Window(self.__root, 740, 740)

        self.__options_frame = None

        self.__create_options_frame()

        # Frame separator
        tk.Frame(self.__root, relief="sunken", width=4, bd=10).pack(
            fill=tk.Y, expand=True
        )
        self.__root.mainloop()

    def __create_options_frame(self):
        self.__options_frame = OF.OptionsFrame(self.__left_frame)
        self.__options_frame.pack(fill=tk.BOTH)

        self.__options_frame.add_button(button_text="Draw Object",
                                        function=self.__get_object,
                                        parent="object")
        self.__options_frame.add_label(label_text="Import/export .obj files",
                                       parent="object", bold=True, pady=(10, 0))
        self.__options_frame.add_button(button_text="Import .obj file",
                                        parent="object", function=self.__parse_obj)
        self.__options_frame.add_button(button_text="Export .obj file",
                                        parent="object",function=self.__generate_obj)

        # Window Zoom
        self.__options_frame.add_button(button_text="-",
                                        function=lambda: self.__zoom_window("out"),
                                        parent="zoom", side=tk.LEFT)
        self.__options_frame.add_label(label_text="Zoom", parent="zoom",
                                       side=tk.LEFT, padx=30, bold=True)
        self.__options_frame.add_button(button_text="+",
                                        function=lambda: self.__zoom_window("in"),
                                        parent="zoom", side=tk.LEFT)

        # Window Navigation
        self.__options_frame.add_label(label_text="Navigation", parent="nav", bold=True)

        self.__options_frame.add_button(button_text="Up",
                                        function=lambda: self.__pan_window(0, 10),
                                        parent="nav", side=tk.LEFT)
        self.__options_frame.add_button(button_text="Down",
                                        function=lambda: self.__pan_window(0, -10),
                                        parent="nav", side=tk.LEFT)
        self.__options_frame.add_button(button_text="Right",
                                        function=lambda: self.__pan_window(10, 0),
                                        parent="nav", side=tk.LEFT)
        self.__options_frame.add_button(button_text="Left",
                                        function=lambda: self.__pan_window(-10, 0),
                                        parent="nav",side=tk.LEFT)

        # Window Rotation
        self.__options_frame.add_label(label_text="Rotate Window",
                                       parent="rotation", bold=True)
        self.__options_frame.add_label(label_text="Angle (in degrees):", parent="rotation")
        self.__options_frame.add_entry(parent="rotation", var_name="angle")
        self.__options_frame.add_button(button_text="Rotate",
                                        function=self.__rotate_window,
                                        parent="rotation")
        
        # Clipping
        self.__options_frame.add_label(label_text="Change Clipping Method",
                                       parent="clipping", bold=True)
        self.__options_frame.add_button(button_text="Cohen Sutherland",
                                        function=lambda: self.__set_clipping_algorithm("C-S"),
                                        parent="clipping")
        self.__options_frame.add_button(button_text="Liang Barsky",
                                        function=lambda: self.__set_clipping_algorithm("L-B"),
                                        parent="clipping")
        

    def __get_object(self) -> list[tuple[float]]:
        try:
            name, coords, color, fill, obj_type = self.__open_draw_window()
            if name is None or coords is None or not name.strip() or not coords.strip():
                messagebox.showinfo("Information", "The object was not created. Name and coordinates are required.")
                return
            f_coords = []
            if obj_type in [Obj3D.ObjectType.BEZIER_SURFACE.value,
                            Obj3D.ObjectType.BSPLINE_SURFACE.value]:
                f_coords = self.__parse_surface_string(coords)
            else:
                f_coords = self.__string_to_float_tuple_list(coords)
            output = self.__create_object(name, f_coords, color, fill, obj_type)
            self.__update_display_file(output)
            return output

        except Exception as e:
            messagebox.showinfo("Input Error", "Invalid input. Please try again.")
            print("Error in get_object:", e)

    def __create_object(self, name, coords, color, fill=False,
                        obj_type: int=Obj3D.ObjectType.OBJECT3D.value, edges=[]) -> Obj3D:
        if obj_type == Obj3D.ObjectType.BEZIER_CURVE.value:
            output = BC.CurvaBezier(name, coords, color=color)
        elif obj_type == Obj3D.ObjectType.BSPLINE_CURVE.value:
            output = BSC.CurvaBSpline(name, coords, color=color)
        elif obj_type == Obj3D.ObjectType.BEZIER_SURFACE.value:
            output = BBC.BezierSurface(name, coords, color=color)
        elif obj_type == Obj3D.ObjectType.BSPLINE_SURFACE.value:
            output = BSB.BSplineSurface(name, coords, color=color)
        elif len(coords) == 1:
            output = P3D.Ponto3D(name, coords, color=color)
        elif len(coords) == 2:
            output = L3D.Linha3D(name, coords, color=color)
        else:
            output = WF.WireFrame(name, coords, color=color, fill=fill, edges=edges)
        return output

    def __string_to_float_tuple_list(self, string:str):
        # Remover parênteses externos e dividir a string em substrings de tuplas
        tuples = string.strip("()").split("),(")
        # Converter cada substring em uma tupla de floats
        tuple_list = []
        for t in tuples:
            tuple_list.append(ast.literal_eval("(" + t + ")"))

        return tuple_list

    def __parse_surface_string(self, string:str):
        # dividir a string em substrings de curvas
        curves = string.split(";")
        # Converter cada substring em uma lista de tuplas de floats
        curve_list = []
        for c in curves:
            curve = self.__string_to_float_tuple_list(c)
            curve_list.append(curve)

        return curve_list
    
    def __open_draw_window(self):
        self.__draw_window = DW.DrawWindow(self.__root)
        name, coords, color, fill, obj_type = self.__draw_window.show_window()
        return name, coords, color, fill, obj_type

    def __draw_all_objects(self):
        self.__window.delete("all")
        for obj in self.__display_file.objects:
            self.__window.draw_object(obj)
        self.__window.draw_viewport_outer_frame()

    def __apply_transformations(self, object_index: int, transformations: list):
        obj = self.__display_file.objects[object_index]
        obj.apply_transformations(transformations=transformations,
                                  transform_vector_function=self.__window.unrotate_vector)
        self.__draw_all_objects()

    def __update_display_file(self, new_object: Obj3D.Objeto3D):
        self.__display_file.add_object(new_object)
        self.__draw_all_objects()

    def __pan_window(self, dx: float, dy: int):
        self.__window.pan(dx, dy)
        self.__draw_all_objects()

    def __zoom_window(self, zoom_type: str):
        if zoom_type == 'in':
            self.__window.zoom_in()
        elif zoom_type == 'out':
            self.__window.zoom_out()
        self.__draw_all_objects()

    def __rotate_window(self, var_parent="rotation", var_name="angle"):
        angle = self.__options_frame.get_var_value(parent=var_parent,
                                                   var_name=var_name,
                                                   var_type=float)
        if angle is None:
            messagebox.showinfo("Information",
                                "The angle value is not of expected type (float).")
            return
        self.__window.set_normalization_matrix(angle)
        self.__draw_all_objects()

    def __parse_obj(self) -> None:
        parser = OBJP()
        objects = parser.objects

        # Convert the list of lists of 3D coordinates in a list of tuples
        for value in objects.values():
            value["coordinates"] = [tuple(coord) for coord in value["coordinates"]]
        
        for name, value in objects.items():
            edges = value["edges"] if value["type"] == "faced_obj" else []
            self.__display_file.add_object(self.__create_object(name=name,
                                                                coords=value["coordinates"],
                                                                color=value["color"], 
                                                                edges=edges)
                                          )

        self.__draw_all_objects()

    def __generate_obj(self) -> None:
        OBJG(self.__display_file.objects)

    # works for both the line and polygon algorithm
    def __set_clipping_algorithm(self, algorithm: str="C-S") -> None:
        self.__window.set_clipping_algorithm(algorithm)
