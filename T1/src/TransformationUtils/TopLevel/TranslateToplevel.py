import tkinter as tk
from src.TransformationUtils.TopLevel.TransformationTopLevel import TransformationToplevel
from src.TransformationUtils.Transformations import Translation


class TranslateToplevel(TransformationToplevel):
    def __init__(self, master=None, title="Translation Options", width=300, height=300):
        super().__init__(master, title, width, height)

        self.__dx = self.__dy = self.__dz = None

    def _place_labels_and_entries(self) -> None:
        tk.Label(self, text="Dx:").pack()
        self.__dx_entry = tk.Entry(self)
        self.__dx_entry.pack()

        tk.Label(self, text="Dy:").pack()
        self.__dy_entry = tk.Entry(self)
        self.__dy_entry.pack()

        tk.Label(self, text="Dz:").pack()
        self.__dz_entry = tk.Entry(self)
        self.__dz_entry.pack()

    def _validate_entries(self) -> bool:
        try:
            self.__dx = 0 if not self.__dx_entry.get() else float(self.__dx_entry.get())
            self.__dy = 0 if not self.__dy_entry.get() else float(self.__dy_entry.get())
            self.__dz = 0 if not self.__dz_entry.get() else float(self.__dz_entry.get())
            return True
        except ValueError as e:
            print("Error:", e)
            return False

    def show_window(self) -> Translation:
        self.wait_window()
        if self._transformation_applied:
            return Translation(self.__dx, self.__dy, self.__dz)
        return None
