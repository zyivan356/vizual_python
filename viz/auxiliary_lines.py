# Файл: vizual_python/viz/auxiliary_lines.py

import pyvista as pv
import numpy as np


class AuxiliaryLinesManager:
    """Менеджер для создания и управления вспомогательными линиями"""

    def __init__(self, scene_widget):
        self.scene_widget = scene_widget
        self.lines = []
        self.points = []
        self.snap_points = []  # Точки для привязки
        self.active_line = None
        self.visible = True

    def add_point(self, x, y, z):
        """Добавить точку для линии"""
        point_id = len(self.points)
        self.points.append([x, y, z])
        return point_id

    def add_line(self, start_point, end_point):
        """Добавить линию между двумя точками"""
        if start_point < len(self.points) and end_point < len(self.points):
            line_id = len(self.lines)
            self.lines.append([start_point, end_point])

            # Обновляем визуализацию
            self.update_visualization()
            return line_id
        return None

    def add_snap_point(self, x, y, z, radius=0.1):
        """Добавить точку привязки"""
        self.snap_points.append({
            'position': [x, y, z],
            'radius': radius
        })

    def toggle_visibility(self):
        """Переключить видимость вспомогательных линий"""
        self.visible = not self.visible
        self.update_visualization()

    def clear(self):
        """Очистить все линии"""
        self.lines = []
        self.points = []
        self.snap_points = []
        self.update_visualization()

    def update_visualization(self):
        """Обновить визуализацию линий в сцене"""
        self.scene_widget.remove_actor("auxiliary_lines")
        self.scene_widget.remove_actor("snap_points")

        if not self.visible:
            return

        # Создаем визуализацию линий
        if self.lines and self.points:
            line_data = []
            for line in self.lines:
                p1 = self.points[line[0]]
                p2 = self.points[line[1]]
                line_data.append([2, line[0], line[1]])

            points = np.array(self.points)
            lines_polydata = pv.PolyData(points, lines=np.hstack(line_data))

            # Добавляем в сцену
            self.scene_widget.add_to_scene(lines_polydata, name="auxiliary_lines",
                                           color="yellow", line_width=2)

        # Создаем визуализацию точек привязки
        if self.snap_points:
            spheres = pv.MultiBlock()
            for snap in self.snap_points:
                sphere = pv.Sphere(radius=snap['radius'], center=snap['position'])
                spheres.append(sphere)

            self.scene_widget.add_to_scene(spheres.combine(), name="snap_points",
                                           color="red", opacity=0.5)

    def snap_to_nearest_point(self, x, y, z, threshold=0.5):
        """Привязка к ближайшей точке"""
        if not self.snap_points:
            return x, y, z

        min_dist = float('inf')
        snap_pos = [x, y, z]

        for snap in self.snap_points:
            dist = np.linalg.norm(np.array([x, y, z]) - np.array(snap['position']))
            if dist < min_dist and dist < threshold:
                min_dist = dist
                snap_pos = snap['position']

        return snap_pos