import tkinter as tk
from abc import abstractmethod
from typing import Type


class TransformationToplevel(tk.Toplevel):
    def __init__(
        self, master=None, title: str = "Options", width: int = 300, height: int = 300
    ):
        super().__init__(master)

        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.title(title)

        self._transformation_applied = False

        self._place_labels_and_entries()

        self._apply_button = tk.Button(
            self, text="Apply", command=self._apply_transformation
        )
        self._apply_button.pack(pady=10)

    def _apply_transformation(self) -> None:
        self._transformation_applied = True
        if self._validate_entries():
            self.destroy()

    @abstractmethod
    def _validate_entries(self) -> bool:
        pass

    @abstractmethod
    def _place_labels_and_entries(self) -> None:
        pass

    @abstractmethod
    def show_window(self) -> Type["TransformationToplevel"]:
        pass
