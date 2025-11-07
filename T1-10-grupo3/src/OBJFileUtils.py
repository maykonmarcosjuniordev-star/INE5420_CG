from tkinter import filedialog
from os import path, getcwd

from src.Objetos.Objeto3D import Objeto3D, ObjectType


class OBJParser:
    def __init__(self):
        self.__vertices = []
        self.__objects = {}

        self.__mtl_elements = {}

        self.__import_obj()

    def __get_import_file_name(self) -> str:
        filename = filedialog.askopenfilename(
            title="Open a .obj file",
            initialdir=getcwd(),
            filetypes=[("Wavefront OBJ", "*.obj")],
        )
        return filename

    def __import_obj(self) -> None:
        file_name = self.__get_import_file_name()
        if not file_name:
            print("Please select a file.")
            return

        with open(file_name, "r") as f:
            lines = f.readlines()

        current_object_name = None
        current_group_name = "default_group"
        current_color = "#000000"

        for line in lines:
            if not line.strip():  # line is empty
                continue

            elements = line.split()

            if elements[0] == "v":  # Definição de coordenadas
                self.__create_vertex(str_coordinates=elements[1:])
            elif elements[0] == "o":  # Definição de um objeto
                current_object_name = elements[1]
            elif elements[0] == "g":  # Definição de um grupo
                if len(elements) > 1:
                    current_group_name = elements[1]
            elif elements[0] == "p":  # Definição de um ponto com base em um vertice
                obj_name = self.__get_object_name(current_group_name, current_object_name)
                self.__create_point(
                    v_number_str=elements[1],
                    current_color=current_color,
                    current_name=obj_name,
                )
            elif elements[0] == "l":  # Definição de uma linha ou um wireframe
                obj_name = self.__get_object_name(current_group_name, current_object_name)
                self.__create_line_or_wireframe(
                    str_vertices=elements[1:],
                    current_color=current_color,
                    current_name=obj_name,
                )
            elif elements[0] == "mtllib":  # Declarar a biblioteca mtllib
                mtl_file_name = elements[1]
                self.__parse_mtl(file_name, mtl_file_name)
            elif elements[0] == "usemtl":  # Vai declarar qual usar da biblioteca
                current_color = self.__mtl_elements[elements[1]]
            elif (
                elements[0] == "f"
            ):
                obj_name = self.__get_object_name(current_group_name, current_object_name)

                self.__add_face_to_current_group(
                    str_vertices=elements[1:],
                    current_color=current_color,
                    current_name=obj_name,
                )

    @property
    def objects(self) -> dict:
        return self.__objects

    def __get_object_name(self, current_group_name: str, current_object_name=None) -> str:
        if (
            current_object_name is not None
            and current_object_name not in self.__objects
        ):
            return current_object_name
        return current_group_name

    def __create_vertex(self, str_coordinates: str) -> None:
        self.__vertices.append([float(k) for k in str_coordinates])

    def __create_point(
        self, v_number_str: str, current_color: str, current_name: str
    ) -> None:
        vertex_number = int(v_number_str) - 1
        point = {
            "type": "point",
            "color": current_color,
            "coordinates": [self.__vertices[vertex_number]],
        }
        self.__objects[current_name] = point

    def __create_line_or_wireframe(
        self,
        str_vertices: str,
        current_color: str,
        current_name: str,
    ) -> None:

        vertices_numbers = [
            int(k) - 1 if "-" not in k else int(k) for k in str_vertices
        ]
        obj_vertices = [self.__vertices[i] for i in vertices_numbers]
        obj_type = "line" if len(obj_vertices) == 2 else "wireframe"

        # Se for wireframe, a 1 coordenada é igual a última
        if obj_type == "wireframe":
            obj_vertices.pop()

        obj = {"type": obj_type, "color": current_color, "coordinates": obj_vertices}

        self.__objects[current_name] = obj

    def __add_face_to_current_group(
        self, str_vertices: str, current_color: str, current_name: str
    ) -> None:

        vertices_numbers = [
            int(k) - 1 if "-" not in k else int(k) for k in str_vertices
        ]

        obj_vertices = [tuple(self.__vertices[i]) for i in vertices_numbers]

        if current_name in self.__objects:
            vertices_not_already_in = list(
                set(obj_vertices).difference(
                    set(self.__objects[current_name]["coordinates"])
                )
            )
            self.__objects[current_name]["coordinates"].extend(vertices_not_already_in)
            current_vertices = self.__objects[current_name]["coordinates"]

            obj_edges = self.__get_edges_with_current_index_list(current_vertices, vertices_numbers)
            self.__objects[current_name]["edges"].extend(obj_edges)
            return

        current_vertices = obj_vertices
        obj_edges = self.__get_edges_with_current_index_list(obj_vertices, vertices_numbers)

        obj = {
            "type": "faced_obj",
            "color": current_color,
            "coordinates": obj_vertices,
            "edges": obj_edges,
        }
        self.__objects[current_name] = obj

    def __get_edges_with_current_index_list(self, current_vertices_list: list[tuple[float]], out_of_date_indexes: list[int]) -> list:
        vertex_map = {vertex: index for index, vertex in enumerate(current_vertices_list)}

        obj_edges = [
            (
                vertex_map[tuple(self.__vertices[out_of_date_indexes[i]])],
                vertex_map[tuple(self.__vertices[out_of_date_indexes[i + 1]])]
            )
            for i in range(len(out_of_date_indexes) - 1)
        ]
        obj_edges.append(
            (
                vertex_map[tuple(self.__vertices[out_of_date_indexes[-1]])],
                vertex_map[tuple(self.__vertices[out_of_date_indexes[0]])]
            )
        )
        return obj_edges

    def __get_hex_from_rgb(self, rgb: list[float]) -> str:
        rgb_tuple = tuple(int(x * 255) for x in rgb)
        return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"

    def __parse_mtl(self, file_path: str, mtl_filename: str) -> None:
        directory_path = path.dirname(file_path)  # Get the directory path
        new_file_path = path.join(directory_path, mtl_filename)

        with open(new_file_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            if not line.strip():  # line is empty
                continue

            elements = line.split()
            if elements[0] == "newmtl":
                current_element = elements[1]
            elif elements[0] == "Kd":
                self.__mtl_elements[current_element] = self.__get_hex_from_rgb(
                    [float(k) for k in elements[1:]]
                )


class OBJGenerator:
    def __init__(self, object_list: list[Objeto3D]):
        self.__vertices = {}

        self.__generate_obj(object_list)

    def __generate_mtl_file(self, elements: dict, file_name: str):
        with open(file_name, "w", encoding="utf-8") as f:
            for key in elements.keys():
                f.write(f"newmtl {elements[key]}\n")
                f.write(f"Kd {key}\n")

    def __choose_file_name(self) -> str:
        return filedialog.asksaveasfilename(
            title="Open a .obj file",
            filetypes=[("Wavefront OBJ", "*.obj")],
        )

    def __generate_obj(self, object_list: list[Objeto3D]):
        file_name = self.__choose_file_name()
        if not file_name:
            print("Please choose a file name.")
            return

        kd_number = 0

        mtl_elements = {}
        mtl_file_name = file_name.strip(".obj") + ".mtl"

        lines = []

        for objeto in object_list:
            self.__add_vertices(objeto.coordinates)

            normalized_rgb_str = self.__get_rgb_str_from_hex(objeto.color)
            if normalized_rgb_str in mtl_elements.keys():
                color_name = mtl_elements[normalized_rgb_str]
            else:
                color_name, kd_number = self.__get_current_kd_str_mtl(kd_number)
                mtl_elements[normalized_rgb_str] = color_name

            lines.append(f"o {objeto.name}\n")
            lines.append(f"usemtl {color_name}\n")

            match objeto.obj_type:
                case ObjectType.POINT:
                    lines.append(f"p {self.__vertices[objeto.coordinates[0]]}\n")
                case ObjectType.LINE:
                    lines.append(
                        f"l {self.__vertices[objeto.coordinates[0]]} {self.__vertices[objeto.coordinates[1]]}\n"
                    )
                case ObjectType.WIREFRAME:
                    if not objeto.edge_order_matter or len(objeto.edges) % 3 != 0:
                        indexes = self.__get_vertices_indexes(objeto.coordinates)
                        lines.append(f"l {' '.join(indexes)}\n")
                        continue

                    lines[-2] = f"g {objeto.name}\n"

                    edges = objeto.edges
                    for i in range(0, len(edges), 3):
                        first, second, third = edges[i][0], edges[i][1], edges[i + 1][1]
                        lines.append(f"f {first + 1} {second + 1} {third + 1}\n")

        self.__write_to_files(
            file_name, mtl_file_name, self.__vertices, lines, mtl_elements
        )

    def __get_rgb_str_from_hex(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        normalized_rgb = tuple(f"{component / 255:.6f}" for component in rgb)
        return " ".join(normalized_rgb)

    def __get_current_kd_str_mtl(self, kd: int) -> tuple[str, int]:
        return "color" + str(kd), kd + 1

    def __add_vertices(self, vertices: list[tuple[float, float]]):
        for v in vertices:
            if v not in self.__vertices:
                self.__vertices[v] = len(self.__vertices) + 1

    def __get_vertices_indexes(self, coords: list[tuple[float]]) -> list[str]:
        indexes = []

        for coord in coords:
            indexes.append(str(self.__vertices[coord]))

        indexes.append(str(indexes[0]))

        return indexes

    def __write_to_files(
        self,
        file_name: str,
        mtl_file_name: str,
        vertices: list[tuple[float, float]],
        lines: list[str],
        mtl_elements: dict,
    ) -> None:
        with open(file_name, "w", encoding="utf-8") as f:
            # vertices
            for vertice in vertices:
                f.write(f"v {vertice[0]:.5f} {vertice[1]:.5f} {vertice[2]:.5f}\n")

            # mtl file
            if len(lines) > 0:
                f.write(f"mtllib {path.basename(mtl_file_name)}\n")
                self.__generate_mtl_file(mtl_elements, mtl_file_name)

            # objects
            f.writelines(lines)
