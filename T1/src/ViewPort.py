import tkinter as tk


class ViewPort:
    def __init__(self, master=None, width_=600, height_=400, bg_="white"):
        self.__border_size = 10

        self.__canvas = tk.Canvas(master, width=width_ + 2 * self.__border_size, height=height_ + 2 * self.__border_size, bg=bg_)

        self.__canvas.configure(scrollregion=self.__canvas.bbox("all"))

        self.__canvas.pack()

        self.__width = width_
        self.__height = height_
        
        self.draw_outer_frame()


    def delete(self, object_name="all") -> None:
        self.__canvas.delete(object_name)


    def draw_outer_frame(self) -> None:
        self.__canvas.create_rectangle(self.__border_size, self.__border_size, self.__width + self.__border_size, self.__height + self.__border_size, outline="red")


    def draw_oval(self, point:tuple[float], color: str, width) -> None:
        if not point:
            return
        x, y = point
        xc, yc = self.viewport_transform(x, y)
        x0, y0 = xc - width, yc - width
        x1, y1 = xc + width, yc + width
        self.__canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color)


    def draw_line(self, points:list[tuple[float]], color: str, width: float) -> None:
        if points == []:
            return
        p0, p1 = points
        x0, y0 = self.viewport_transform(*p0)
        x1, y1 = self.viewport_transform(*p1)
        self.__canvas.create_line(x0, y0, x1, y1, fill=color, width=width)


    def draw_polygon(self, points: list[tuple[float]], edges: list[tuple[int]], color: str, width:float, fill=False) -> None:
        if points == []:
            return
        points = [self.viewport_transform(*point) for point in points]
        if fill:
            self.__canvas.create_polygon(points, fill=color, outline=color, width=width)
            return

        for start_p, end_p in edges:
            self.__canvas.create_line(*points[start_p], *points[end_p], fill=color, width=width)


    def draw_curve(self, sub_curves: list[tuple[float]],
                   color: str, width: float) -> None:
        for sub_curve in sub_curves:
            for i in range(len(sub_curve) - 1):
                line = [sub_curve[i], sub_curve[i + 1]]
                self.draw_line(line, color, width)


    def viewport_transform(self, x: float, y: float) -> list[float]:
        vx = (x + 1) / 2 * self.__width + self.__border_size
        vy = (1 - (y + 1) / 2) * self.__height + self.__border_size
        return [vx, vy]
