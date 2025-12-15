# app.py
import sys
import os
import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Интеграция FreeCAD (адаптируйте путь!)
FREECAD_PATH = r"C:\Program Files\FreeCAD 1.0\bin"  # ← ВАЖНО: укажите ваш путь!
if os.path.exists(FREECAD_PATH):
    sys.path.append(FREECAD_PATH)
    import FreeCAD
    import Part
else:
    print("⚠️ FreeCAD не найден! Геометрия будет упрощённой.")
    FreeCAD = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engineering Suite MVP")
        self.setGeometry(100, 100, 1200, 800)

        # 3D-виджет
        self.plotter = QtInteractor(self)
        self.setCentralWidget(self.plotter)

        # Создаём модель
        self.create_model()

        # Добавляем цветовую шкалу
        self.plotter.add_scalar_bar(title="Напряжение (Па)", n_labels=4)

    def create_model(self):
        """Создаёт модель балки и визуализирует напряжения"""
        if FreeCAD:
            # Геометрия через FreeCAD
            doc = FreeCAD.newDocument("Temp")
            beam = doc.addObject("Part::Box", "Beam")
            beam.Length = 5000  # мм
            beam.Width = 300
            beam.Height = 500
            doc.recompute()

            # Экспорт в треугольную сетку
            mesh = beam.Shape.tessellate(1.0)
            vertices = np.array(mesh[0])
            faces = np.hstack([np.full((len(mesh[1]), 1), 3), mesh[1]]).astype(np.int32)
        else:
            # Упрощённая геометрия без FreeCAD
            beam = pv.Cube(x_length=5, y_length=0.3, z_length=0.5)
            vertices = beam.points
            faces = beam.faces

        # Создаём PyVista-сетку
        grid = pv.PolyData(vertices, faces)

        # Генерируем "напряжения" (пример данных)
        x = vertices[:, 0]
        stress = 1e9 * (1 - x / np.max(x))  # Простая линейная модель
        grid["stress"] = stress

        # Визуализация
        self.plotter.add_mesh(
            grid,
            scalars="stress",
            cmap="coolwarm",
            show_edges=True
        )
        self.plotter.add_text("Аналог Plaxis/Renga (MVP)", font_size=10)
        self.plotter.show_axes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())