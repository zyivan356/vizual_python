# Файл: vizual_python/plugins/geotech/foundation_builder.py

from core.stress_calculator import calculate_foundation_stress
import numpy as np
import pyvista as pv


class CustomFoundation:
    """Класс для создания и управления пользовательскими моделями фундаментов"""

    def __init__(self):
        self.vertices = []
        self.edges = []
        self.faces = []
        self.properties = {
            'material': 'concrete',
            'density': 2500,  # кг/м³
            'strength': 25e6,  # Па
            'thickness': 0.5  # м, по умолчанию
        }

    def add_vertex(self, x, y, z):
        """Добавить вершину к модели фундамента"""
        self.vertices.append([x, y, z])
        return len(self.vertices) - 1

    def add_edge(self, v1_idx, v2_idx):
        """Добавить ребро между вершинами"""
        if v1_idx < len(self.vertices) and v2_idx < len(self.vertices):
            self.edges.append([v1_idx, v2_idx])
            return True
        return False

    def create_polygon_face(self, vertex_indices):
        """Создать грань из набора вершин"""
        if all(idx < len(self.vertices) for idx in vertex_indices):
            self.faces.append(vertex_indices)
            return True
        return False

    def set_property(self, key, value):
        """Установить свойство фундамента"""
        if key in self.properties:
            self.properties[key] = value

    def generate_mesh(self):
        """Создать сетку для расчетов на основе определенных вершин и граней"""
        if not self.vertices or not self.faces:
            return None

        # Создание сетки с помощью pyvista
        points = np.array(self.vertices)
        faces = []

        for face in self.faces:
            faces.append(len(face))
            faces.extend(face)

        mesh = pv.PolyData(points, faces=faces)

        # Выдавливание для создания объемного фундамента
        if self.properties['thickness'] > 0:
            extruded = mesh.extrude([0, 0, -self.properties['thickness']], capping=True)
            return extruded
        return mesh

    def calculate_stress(self, load=1e5):
        """Рассчитать напряжения в фундаменте"""
        mesh = self.generate_mesh()
        if mesh:
            return calculate_foundation_stress(mesh, load, self.properties)
        return None