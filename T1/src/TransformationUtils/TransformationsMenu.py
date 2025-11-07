import tkinter as tk
from src.TransformationUtils.Transformations import (Transformation)
from src.TransformationUtils.TopLevel.RotateToplevel import RotateToplevel
from src.TransformationUtils.TopLevel.ScaleToplevel import ScaleToplevel
from src.TransformationUtils.TopLevel.TranslateToplevel import TranslateToplevel


class TransformationsMenu(tk.Toplevel):
    def __init__(self, object_name: str, master=None, width=400, height=300):
        super().__init__(master)

        self.__transformations: list[Transformation] = []

        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.title(f"Object Transformations - {object_name}")

        tk.Label(self, text="Transformations", font="System 12 bold").pack(
            fill=tk.X, pady=15
        )

        tk.Button(
            self, text="Translate Object", command=self.__translate_toplevel
        ).pack(pady=15)
        tk.Button(self, text="Scale Object", command=self.__scale_toplevel).pack(
            pady=15
        )
        tk.Button(self, text="Rotate Object", command=self.__rotate_toplevel).pack(
            pady=15
        )

        tk.Button(
            self,
            text="Apply All Transformations",
            command=self.__apply_all,
            bg="green",
            fg="white",
        ).pack(pady=15)

    def __apply_all(self) -> None:
        self.destroy()

    def show_window(self) -> dict:
        self.wait_window()
        return self.__transformations

    def __translate_toplevel(self) -> None:
        t_toplevel = TranslateToplevel(self)
        translation = t_toplevel.show_window()

        if translation is not None:
            self.__transformations.append(translation)

    def __scale_toplevel(self) -> None:
        s_toplevel = ScaleToplevel(self)
        scaling = s_toplevel.show_window()

        if scaling is not None:
            self.__transformations.append(scaling)

    def __rotate_toplevel(self) -> None:
        r_toplevel = RotateToplevel(self)
        rotation = r_toplevel.show_window()

        if rotation is not None:
            self.__transformations.append(rotation)
