# Файл: vizual_python/gui/foundation_tool_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QComboBox, QDoubleSpinBox, QGroupBox, QFormLayout,
                             QHBoxLayout, QToolButton)
from PyQt5.QtCore import Qt


class FoundationToolPanel(QWidget):
    """Панель инструментов для создания фундаментов"""

    def __init__(self, scene_widget, parent=None):
        super().__init__(parent)
        self.scene_widget = scene_widget
        self.drawing_mode = False
        self.current_foundation = None
        self.setup_ui()
        from .foundation_tool_panel import FoundationToolPanel
        from viz.auxiliary_lines import AuxiliaryLinesManager

    def setup_ui(self):
        layout = QVBoxLayout()

        # Группа для создания фундамента
        creation_group = QGroupBox("Создание фундамента")
        creation_layout = QVBoxLayout()

        # Кнопки управления режимом
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Начать создание")
        self.btn_start.clicked.connect(self.start_foundation_creation)
        btn_layout.addWidget(self.btn_start)

        self.btn_finish = QPushButton("Завершить")
        self.btn_finish.setEnabled(False)
        self.btn_finish.clicked.connect(self.finish_foundation_creation)
        btn_layout.addWidget(self.btn_finish)

        creation_layout.addLayout(btn_layout)

        # Текущий статус
        self.status_label = QLabel("Статус: Готов к созданию")
        creation_layout.addWidget(self.status_label)

        creation_group.setLayout(creation_layout)
        layout.addWidget(creation_group)

        # Свойства фундамента
        props_group = QGroupBox("Свойства фундамента")
        props_layout = QFormLayout()

        self.material_combo = QComboBox()
        self.material_combo.addItems(["Бетон", "Железобетон", "Кирпич"])
        props_layout.addRow("Материал:", self.material_combo)

        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0.1, 5.0)
        self.thickness_spin.setValue(0.5)
        self.thickness_spin.setSingleStep(0.1)
        props_layout.addRow("Толщина (м):", self.thickness_spin)

        self.load_spin = QDoubleSpinBox()
        self.load_spin.setRange(1, 10000)
        self.load_spin.setValue(100)
        self.load_spin.setSuffix(" кН")
        props_layout.addRow("Нагрузка:", self.load_spin)

        props_group.setLayout(props_layout)
        layout.addWidget(props_group)

        # Кнопка расчета
        self.calculate_btn = QPushButton("Рассчитать напряжения")
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.clicked.connect(self.calculate_stresses)
        layout.addWidget(self.calculate_btn)

        layout.addStretch()
        self.setLayout(layout)

    def start_foundation_creation(self):
        """Активировать режим создания фундамента"""
        self.drawing_mode = True
        self.current_foundation = CustomFoundation()
        self.btn_start.setEnabled(False)
        self.btn_finish.setEnabled(True)
        self.status_label.setText("Статус: Добавьте вершины фундамента")
        self.scene_widget.set_foundation_mode(True, self.current_foundation)

    def finish_foundation_creation(self):
        """Завершить создание фундамента"""
        if len(self.current_foundation.vertices) >= 3:
            # Автоматически создаем грань из всех вершин
            self.current_foundation.create_polygon_face(list(range(len(self.current_foundation.vertices))))

            # Применяем свойства
            material_map = {
                "Бетон": {'density': 2400, 'strength': 20e6},
                "Железобетон": {'density': 2500, 'strength': 30e6},
                "Кирпич": {'density': 1800, 'strength': 10e6}
            }
            selected_mat = self.material_combo.currentText()
            self.current_foundation.set_property('thickness', self.thickness_spin.value())
            self.current_foundation.set_property('density', material_map[selected_mat]['density'])
            self.current_foundation.set_property('strength', material_map[selected_mat]['strength'])

            # Генерируем и отображаем сетку
            mesh = self.current_foundation.generate_mesh()
            if mesh:
                self.scene_widget.add_to_scene(mesh, name="Фундамент")
                self.calculate_btn.setEnabled(True)
                self.status_label.setText(
                    f"Статус: Фундамент создан с {len(self.current_foundation.vertices)} вершинами")

        self.drawing_mode = False
        self.btn_start.setEnabled(True)
        self.btn_finish.setEnabled(False)
        self.scene_widget.set_foundation_mode(False)

    def calculate_stresses(self):
        """Выполнить расчет напряжений"""
        if self.current_foundation:
            load = self.load_spin.value() * 1000  # кН в Н
            stress_results = self.current_foundation.calculate_stress(load)
            if stress_results:
                self.scene_widget.show_stress_map(stress_results)
                self.status_label.setText("Статус: Расчет напряжений выполнен")