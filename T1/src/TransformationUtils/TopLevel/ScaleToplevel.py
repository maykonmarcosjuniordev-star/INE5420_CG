import tkinter as tk
from src.TransformationUtils.TopLevel.TransformationTopLevel import TransformationToplevel
from src.TransformationUtils.Transformations import Scaling


class ScaleToplevel(TransformationToplevel):
    def __init__(self, master=None, title="Scaling Options", width=300, height=300):
        super().__init__(master, title, width, height)

        self.__sx = self.__sy = self.__sz = None

    def _place_labels_and_entries(self) -> None:
        tk.Label(self, text="Sx:").pack()
        self.__sx_entry = tk.Entry(self)
        self.__sx_entry.pack()

        tk.Label(self, text="Sy:").pack()
        self.__sy_entry = tk.Entry(self)
        self.__sy_entry.pack()

        tk.Label(self, text="Sz:").pack()
        self.__sz_entry = tk.Entry(self)
        self.__sz_entry.pack()

    def _validate_entries(self) -> bool:
        try:
            self.__sx = 1 if not self.__sx_entry.get() else float(self.__sx_entry.get())
            self.__sy = 1 if not self.__sy_entry.get() else float(self.__sy_entry.get())
            self.__sz = 1 if not self.__sz_entry.get() else float(self.__sz_entry.get())
            return True
        except ValueError as e:
            print("Error:", e)
            return False

    def show_window(self):
        self.wait_window()
        if self._transformation_applied:
            return Scaling(self.__sx, self.__sy, self.__sz)
        return None
