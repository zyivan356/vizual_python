# viz/scene_manager.py
import pyvista as pv
from PySide6.QtWidgets import QFrame


class QtPyVistaWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotter = pv.QtInteractor(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.plotter.interactor)

        # Загрузка модели
        self.model = pv.read("foundation.stl")
        self.plotter.add_mesh(self.model, color="tan")

        # Добавление результатов расчёта
        self.plotter.add_scalar_bar(title="Напряжение (Па)")

    def update_results(self, stress_data):
        """Обновление визуализации при расчёте"""
        self.model["stress"] = stress_data
        self.plotter.update_scalar_bar_range([0, np.max(stress_data)])
        self.plotter.render()


# В gui/main_window.py:
class MainWindow(QMainWindow):
    def __init__(self):
        self.viz_widget = QtPyVistaWidget()
        self.setCentralWidget(self.viz_widget)