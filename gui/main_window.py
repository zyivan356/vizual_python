from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import numpy as np
from core import stress_calculator  # ← Вызывает скомпилированный C++ код!


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Инженерный калькулятор")
        self.button = QPushButton("Рассчитать напряжение")
        self.button.clicked.connect(self.run_calculation)
        self.setCentralWidget(self.button)

    def run_calculation(self):
        # Генерация данных на Python
        strain_data = np.random.uniform(0.001, 0.01, (1000000, 3))
        E = 210e9  # Модуль Юнга для стали

        # Вызов C++ кода через Python API
        stress_result = stress_calculator.calculate_stress(strain_data, E)

        print(f"Расчёт завершён! Среднее напряжение: {np.mean(stress_result):.2e} Па")


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()