from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QGroupBox,
                             QSlider, QLabel, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import Qt


class FoundationTools(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout()

        # Группа для создания фундамента
        foundation_group = QGroupBox("Создание фундамента")
        foundation_layout = QVBoxLayout()

        self.create_foundation_btn = QPushButton("Создать фундамент")
        self.create_foundation_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.create_foundation_btn.setCheckable(True)
        foundation_layout.addWidget(self.create_foundation_btn)

        # Параметры фундамента
        foundation_layout.addWidget(QLabel("Толщина фундамента (м):"))
        thickness_layout = QHBoxLayout()
        self.thickness_slider = QSlider(Qt.Horizontal)
        self.thickness_slider.setRange(1, 20)
        self.thickness_slider.setValue(5)
        self.thickness_label = QLabel("0.5 м")
        thickness_layout.addWidget(self.thickness_slider)
        thickness_layout.addWidget(self.thickness_label)
        foundation_layout.addLayout(thickness_layout)

        foundation_group.setLayout(foundation_layout)
        main_layout.addWidget(foundation_group)

        # Группа для вспомогательных линий
        guide_group = QGroupBox("Вспомогательные линии")
        guide_layout = QVBoxLayout()

        self.create_guide_btn = QPushButton("Создать линию")
        self.create_guide_btn.setStyleSheet("background-color: #2196F3; color: white;")
        self.create_guide_btn.setCheckable(True)
        guide_layout.addWidget(self.create_guide_btn)

        self.snap_checkbox = QCheckBox("Привязка к сетке")
        self.snap_checkbox.setChecked(True)
        guide_layout.addWidget(self.snap_checkbox)

        guide_group.setLayout(guide_layout)
        main_layout.addWidget(guide_group)

        # Кнопка применения
        self.apply_btn = QPushButton("Применить изменения")
        self.apply_btn.setEnabled(False)
        main_layout.addWidget(self.apply_btn)

        main_layout.addStretch()
        self.setLayout(main_layout)

        # Подключение сигналов
        self.thickness_slider.valueChanged.connect(self.update_thickness_label)
        self.create_foundation_btn.clicked.connect(self.toggle_foundation_mode)
        self.create_guide_btn.clicked.connect(self.toggle_guide_mode)

    def update_thickness_label(self, value):
        thickness = value * 0.1
        self.thickness_label.setText(f"{thickness:.1f} м")

    def toggle_foundation_mode(self, checked):
        if checked:
            self.create_guide_btn.setChecked(False)

    def toggle_guide_mode(self, checked):
        if checked:
            self.create_foundation_btn.setChecked(False)

    def get_foundation_thickness(self):
        return self.thickness_slider.value() * 0.1

    def is_snap_enabled(self):
        return self.snap_checkbox.isChecked()