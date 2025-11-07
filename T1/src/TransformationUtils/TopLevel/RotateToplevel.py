import tkinter as tk
from src.TransformationUtils.TopLevel.TransformationTopLevel import TransformationToplevel
from src.TransformationUtils.Transformations import Rotation3DType, Rotation


class RotateToplevel(TransformationToplevel):
    def __init__(self, master=None, title="Rotation Options", width=600, height=600):
        super().__init__(master, title, width, height)


        self.__choosed_rotation_type = None
        self.__angle = None
        self.__p1 = (0, 0, 0)
        self.__p2 = (0, 0, 0)

        self.__x1_label = tk.Label(self, text="X1:")
        self.__x1_entry = tk.Entry(self)
        self.__y1_label = tk.Label(self, text="Y1:")
        self.__y1_entry = tk.Entry(self)
        self.__z1_label = tk.Label(self, text="Z1:")
        self.__z1_entry = tk.Entry(self)

        self.__x2_label = tk.Label(self, text="X2:")
        self.__x2_entry = tk.Entry(self)
        self.__y2_label = tk.Label(self, text="Y2:")
        self.__y2_entry = tk.Entry(self)
        self.__z2_label = tk.Label(self, text="Z2:")
        self.__z2_entry = tk.Entry(self)

    def _place_labels_and_entries(self) -> None:
        self.__rotation_type = tk.StringVar()
        self.__rotation_type.set(Rotation3DType.Z)
        tk.Radiobutton(
            self,
            text="Rotation around the X axis",
            variable=self.__rotation_type,
            value=Rotation3DType.X,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around the Y axis",
            variable=self.__rotation_type,
            value=Rotation3DType.Y,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around the Z axis",
            variable=self.__rotation_type,
            value=Rotation3DType.Z,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around the center of the object, on X axis",
            variable=self.__rotation_type,
            value=Rotation3DType.center_X,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around the center of the object, on Y axis",
            variable=self.__rotation_type,
            value=Rotation3DType.center_Y,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around the center of the object, on Z axis",
            variable=self.__rotation_type,
            value=Rotation3DType.center_Z,
            command=self.__on_rotation_type_change,
        ).pack()
        tk.Radiobutton(
            self,
            text="Rotation around any axis",
            variable=self.__rotation_type,
            value=Rotation3DType.any_axis,
            command=self.__on_rotation_type_change,
        ).pack()

        tk.Label(self, text="Rotation Angle (in degrees):").pack()
        self.__angle_entry = tk.Entry(self)
        self.__angle_entry.pack()

    def __on_rotation_type_change(self) -> None:
        if self.__rotation_type.get() == str(Rotation3DType.any_axis):
            self._apply_button.pack_forget()
            self.__x1_label.pack()
            self.__x1_entry.pack()
            self.__y1_label.pack()
            self.__y1_entry.pack()
            self.__z1_label.pack()
            self.__z1_entry.pack()
            self.__x2_label.pack()
            self.__x2_entry.pack()
            self.__y2_label.pack()
            self.__y2_entry.pack()
            self.__z2_label.pack()
            self.__z2_entry.pack()
            self._apply_button.pack()
            return
        self.__x1_label.pack_forget()
        self.__y1_label.pack_forget()
        self.__z1_label.pack_forget()
        self.__x1_entry.pack_forget()
        self.__y1_entry.pack_forget()
        self.__z1_entry.pack_forget()
        self.__x2_label.pack_forget()
        self.__y2_label.pack_forget()
        self.__z2_label.pack_forget()
        self.__x2_entry.pack_forget()
        self.__y2_entry.pack_forget()
        self.__z2_entry.pack_forget()

    def _validate_entries(self, rotation_type: str) -> bool:
        try:
            self.__angle = float(self.__angle_entry.get())
            if rotation_type == str(Rotation3DType.any_axis):
                x = float(self.__x1_entry.get())
                y = float(self.__y1_entry.get())
                z = float(self.__z1_entry.get())
                self.__p1 = (x, y, z)
                x = float(self.__x2_entry.get())
                y = float(self.__y2_entry.get())
                z = float(self.__z2_entry.get())
                self.__p2 = (x, y, z)
            return True
        except ValueError as e:
            print("Error:", e)
            return False

    def _apply_transformation(self):
        self.__choosed_rotation_type = self.__rotation_type.get()
        self._transformation_applied = True
        if self._validate_entries(self.__choosed_rotation_type):
            self.destroy()

    def show_window(self):
        self.wait_window()
        if self._transformation_applied:
            return Rotation(
                self.__choosed_rotation_type,
                self.__angle, self.__p1, self.__p2
            )
        return None
