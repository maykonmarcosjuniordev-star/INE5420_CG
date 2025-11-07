import tkinter as tk
from tkinter import colorchooser
from src.Objetos.Objeto3D import ObjectType


class DrawWindow(tk.Toplevel):
    def __init__(self, master=None, height=600, width=900):
        super().__init__(master)
        self.__coordinates_str = None  # Value to be returned
        self.__name_str = None
        self.__color = "#000000"
        self.__fill_var_bool = None

        self.__object_type_var = tk.IntVar(self, ObjectType.OBJECT3D.value)
        self.__object_type = None

        self.title("Draw Options")
        self.geometry(f"{width}x{height}")

        frame_obj_type = tk.Frame(self)
        frame_obj_type.pack(pady=10)

        tk.Label(frame_obj_type, text="Object Type: ").pack(side=tk.LEFT)
        tk.Radiobutton(frame_obj_type, text="Objeto 3D",
                       variable=self.__object_type_var,
                       value=ObjectType.OBJECT3D.value).pack(side=tk.LEFT)
        tk.Radiobutton(frame_obj_type, text="Curva de Bézier",
                       variable=self.__object_type_var,
                       value=ObjectType.BEZIER_CURVE.value).pack(side=tk.LEFT)
        tk.Radiobutton(frame_obj_type, text="Curva B-Spline",
                       variable=self.__object_type_var,
                       value=ObjectType.BSPLINE_CURVE.value).pack(side=tk.LEFT)
        tk.Radiobutton(frame_obj_type, text="Superfície de Bézier",
                       variable=self.__object_type_var,
                       value=ObjectType.BEZIER_SURFACE.value).pack(side=tk.LEFT)
        tk.Radiobutton(frame_obj_type, text="Superfície B-Spline",
                       variable=self.__object_type_var,
                       value=ObjectType.BSPLINE_SURFACE.value).pack(side=tk.LEFT)

        tk.Label(self, text="Name:").pack()
        self.__object_name = tk.Entry(self)
        self.__object_name.pack(fill=tk.X, padx=20)

        tk.Label(self,
                 text=('Enter Coordinates (in the format "(x1, y1, z1),(x2, y2, z2),..."):' + 
                 ' (for curves, enter the control points separated by ";")')).pack(pady=(10, 0))
        self.__coord_entry = tk.Entry(self)
        self.__coord_entry.pack(fill=tk.X, padx=20)

        tk.Button(self, text="Choose Color",
                  command=self.__choose_color).pack(pady=(20, 0))

        tk.Label(self, text="Selected Color:").pack(pady=10)
        self.__selected_color_label = tk.Label(self, bg=self.__color,
                                               width=5, height=1)
        self.__selected_color_label.pack()

        self.__fill_var = tk.IntVar()
        tk.Checkbutton(self, text="Fill Polygon",
                       variable=self.__fill_var,
                       onvalue=1,
                       offvalue=0).pack(pady=20)

        tk.Button(self, text="Submit", command=self.__submit_option).pack(pady=(20, 0))

    def show_window(self) -> tuple[str, str, str, bool, int]:
        self.wait_window()
        return self.get_informations()

    def __submit_option(self) -> None:
        self.__coordinates_str = self.__coord_entry.get()
        self.__name_str = self.__object_name.get()
        self.__fill_var_bool = self.__fill_var.get() == 1
        self.__object_type = self.__object_type_var.get()
        self.destroy()

    def get_informations(self) -> tuple[str, str, str, bool, int]:
        return (
            self.__name_str,
            self.__coordinates_str,
            self.__color,
            self.__fill_var_bool,
            self.__object_type
        )

    def __choose_color(self) -> None:
        color = colorchooser.askcolor("#000000", title="Choose color")[1]
        if color:
            self.__selected_color_label.config(bg=color)
            self.__color = color
