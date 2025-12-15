import sys
import os
import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor, MainWindow
import vtk
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QDockWidget, QHBoxLayout, QFrame, QMessageBox)
from PyQt5.QtCore import Qt

# Интеграция FreeCAD (адаптируйте путь!)
FREECAD_PATH = r"C:\Program Files\FreeCAD 1.0\bin"  # ← ВАЖНО: укажите ваш путь!
if os.path.exists(FREECAD_PATH):
    sys.path.append(FREECAD_PATH)
    import FreeCAD
    import Part
else:
    print("⚠️ FreeCAD не найден! Геометрия будет упрощённой.")
    FreeCAD = None

# Импорт наших инструментов
try:
    from gui.foundation_tools import FoundationTools
except ImportError as e:
    print(f"Ошибка импорта FoundationTools: {e}")
    print("Проверьте структуру папки gui и наличие файла foundation_tools.py")
    sys.exit(1)


class EngineeringSuiteApp(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Engineering Suite MVP")
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # 3D-виджет
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter)

        self.setCentralWidget(central_widget)

        # Правая панель с инструментами
        right_panel = QDockWidget("Инструменты", self)
        right_panel.setAllowedAreas(Qt.RightDockWidgetArea)
        self.tools_widget = FoundationTools()
        right_panel.setWidget(self.tools_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, right_panel)

        # Переменные для интерактивного создания
        self.creation_mode = None  # "foundation" или "guide_line"
        self.start_point = None
        self.end_point = None
        self.temp_actor = None
        self.guide_points = []
        self.guide_actors = []
        self.foundations = []
        self.grid_spacing = 0.5

        # Подключение сигналов инструментов
        self.tools_widget.create_foundation_btn.clicked.connect(self.set_foundation_creation_mode)
        self.tools_widget.create_guide_btn.clicked.connect(self.set_guide_creation_mode)
        self.tools_widget.apply_btn.clicked.connect(self.apply_changes)

        # Отладка инициализации
        print("Инициализация приложения...")
        print("3D-виджет инициализирован:", hasattr(self.plotter, 'iren'))
        print("Наличие рендерера:", hasattr(self.plotter, 'renderer'))

        # Настройка обработчиков событий мыши
        self.setup_mouse_events()

        # Добавляем обработчик для клавиш для отмены операций
        self.plotter.add_key_event('Escape', self.cancel_creation)

        # Первоначальное создание модели
        self.plotter.reset_camera()
        self.create_initial_model()

        print("Приложение готово к работе!")

    def setup_mouse_events(self):
        """Настройка обработчиков событий мыши для PyVistaQt 0.11.1"""
        print("Настройка обработчиков событий мыши...")

        # Инициализация picker
        self.plotter.picker = vtk.vtkCellPicker()
        self.plotter.picker.SetTolerance(0.005)

        # Подключение обработчика кликов
        self.plotter.track_click_position(self.on_mouse_click, side="left")
        print("Обработчик левого клика подключен")

        # Правильный способ подключения обработчика движения мыши для PyVistaQt 0.11.1
        self.plotter.track_mouse_position()
        # Используем VTK observer для события движения мыши
        self.plotter.iren.add_observer('MouseMoveEvent', self.on_mouse_move_vtk)
        print("Обработчик движения мыши подключен через VTK observer")

    def create_initial_model(self):
        """Создаёт начальную модель для демонстрации"""
        print("Создание начальной модели...")
        self.plotter.add_text("Engineering Suite: Интерактивное проектирование фундаментов",
                              font_size=10, position="upper_edge")
        self.plotter.show_axes()

        # Создание базовой поверхности (земля)
        ground = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=20, j_size=20)
        self.ground_actor = self.plotter.add_mesh(ground, color="green", opacity=0.3, show_edges=True)
        print("Базовая поверхность создана")

        # Принудительно обновляем рендер
        self.plotter.update()

    def set_foundation_creation_mode(self, checked):
        """Установка режима создания фундамента"""
        if checked:
            self.creation_mode = "foundation"
            self.tools_widget.create_guide_btn.setChecked(False)
            self.clear_temp_objects()
            print("Режим: создание фундамента")
        else:
            self.creation_mode = None
            print("Режим создания отключен")

    def set_guide_creation_mode(self, checked):
        """Установка режима создания вспомогательных линий"""
        if checked:
            self.creation_mode = "guide_line"
            self.tools_widget.create_foundation_btn.setChecked(False)
            self.clear_temp_objects()
            self.guide_points = []
            print("Режим: создание вспомогательных линий")
        else:
            self.creation_mode = None
            print("Режим создания отключен")

    def cancel_creation(self):
        """Отмена текущей операции создания"""
        print("Отмена операции создания")
        self.creation_mode = None
        self.start_point = None
        self.end_point = None
        self.guide_points = []
        self.clear_temp_objects()
        self.tools_widget.create_foundation_btn.setChecked(False)
        self.tools_widget.create_guide_btn.setChecked(False)

    def on_mouse_click(self, position):
        """Обработчик клика мыши в 3D-сцене"""
        print("\n=== Обнаружен клик мыши ===")
        print(f"Текущий режим создания: {self.creation_mode}")

        if not self.creation_mode:
            print("Не в режиме создания")
            return

        if not hasattr(self.plotter, 'picker') or self.plotter.picker is None:
            print("Picker не инициализирован")
            return

        # Обработка позиции - в PyVistaQt 0.11.1 position содержит мировые координаты
        print(f"Тип position: {type(position)}")
        print(f"Значение position: {position}")

        # Конвертируем в numpy array
        world_pos = np.array(position)
        print(f"Мировая позиция: {world_pos}")

        # Привязка к сетке если включена
        if self.tools_widget.is_snap_enabled():
            world_pos = np.round(world_pos / self.grid_spacing) * self.grid_spacing
            print(f"Позиция после привязки к сетке: {world_pos}")

        # Логика создания объектов
        if self.creation_mode == "foundation":
            if self.start_point is None:
                self.start_point = world_pos
                print(f"Установлена первая точка фундамента: {self.start_point}")
            else:
                self.end_point = world_pos
                print(f"Установлена вторая точка фундамента: {self.end_point}")
                print("Создание фундамента...")
                self.create_foundation()
                self.start_point = None
                self.end_point = None

        elif self.creation_mode == "guide_line":
            self.guide_points.append(world_pos)
            print(f"Добавлена точка линии: {world_pos}, всего точек: {len(self.guide_points)}")
            if len(self.guide_points) > 1:
                self.add_guide_line(self.guide_points[-2], self.guide_points[-1])

    def on_mouse_move_vtk(self, obj, event):
        """Обработчик движения мыши через VTK observer"""
        if not self.creation_mode:
            return

        try:
            # Получаем позицию мыши в экранных координатах
            interactor = self.plotter.iren
            if not hasattr(interactor, 'GetEventPosition'):
                return

            # Получаем экранные координаты
            screen_pos = interactor.GetEventPosition()
            if not screen_pos:
                return

            x, y = screen_pos[:2]
            print(f"Экранная позиция мыши: ({x}, {y})")  # Отладочное сообщение

            # Находим точку в 3D пространстве
            renderer = self.plotter.renderer
            self.plotter.picker.Pick(x, y, 0, renderer)

            # Получаем позицию в мировых координатах
            world_pos = np.array(self.plotter.picker.GetPickPosition())

            # Проверяем валидность координат
            if np.all(np.abs(world_pos) < 1e-6) or np.isnan(world_pos).any():
                print("Некорректные координаты от picker")
                return

            print(f"Мировая позиция от picker: {world_pos}")  # Отладочное сообщение

            # Привязка к сетке если включена
            if self.tools_widget.is_snap_enabled():
                world_pos = np.round(world_pos / self.grid_spacing) * self.grid_spacing
                print(f"Позиция после привязки к сетке: {world_pos}")  # Отладочное сообщение

            # Обновление предпросмотра
            if self.creation_mode == "foundation" and self.start_point is not None:
                self.update_foundation_preview(world_pos)

            elif self.creation_mode == "guide_line" and self.guide_points:
                self.update_guide_preview(world_pos)

        except Exception as e:
            print(f"Ошибка в обработчике движения мыши: {e}")

    def update_foundation_preview(self, current_pos):
        """Обновление предпросмотра фундамента"""
        self.clear_temp_objects()

        if self.start_point is None:
            return

        min_point = np.minimum(self.start_point, current_pos)
        max_point = np.maximum(self.start_point, current_pos)

        width = max_point[0] - min_point[0]
        length = max_point[1] - min_point[1]
        thickness = self.tools_widget.get_foundation_thickness()

        if width < 0.1 or length < 0.1:
            return

        # Создание прямоугольного фундамента
        foundation = pv.Cube(
            center=((min_point[0] + max_point[0]) / 2,
                    (min_point[1] + max_point[1]) / 2,
                    min_point[2] + thickness / 2),
            x_length=width,
            y_length=length,
            z_length=thickness
        )

        # Удаляем предыдущий временный актер, если он существует
        if hasattr(self, 'temp_actor') and self.temp_actor is not None:
            try:
                self.plotter.remove_actor(self.temp_actor)
            except:
                pass

        self.temp_actor = self.plotter.add_mesh(
            foundation,
            color="yellow",
            opacity=0.7,
            show_edges=True,
            name="temp_foundation"
        )

    def update_guide_preview(self, current_pos):
        """Обновление предпросмотра вспомогательной линии"""
        self.clear_temp_objects()

        # Отображение всех постоянных линий
        for i, point in enumerate(self.guide_points):
            if i > 0:
                line = pv.Line(self.guide_points[i - 1], point)
                self.plotter.add_mesh(line, color="blue", line_width=3, name=f"guide_{i}")

        # Предпросмотр текущей линии
        if self.guide_points:
            line = pv.Line(self.guide_points[-1], current_pos)
            # Удаляем предыдущий временный актер, если он существует
            if hasattr(self, 'temp_actor') and self.temp_actor is not None:
                try:
                    self.plotter.remove_actor(self.temp_actor)
                except:
                    pass

            self.temp_actor = self.plotter.add_mesh(line, color="cyan", line_width=2, style="wireframe")

    def create_foundation(self):
        """Создание постоянного фундамента"""
        if self.start_point is None or self.end_point is None:
            print("Ошибка: нет точек для создания фундамента")
            return

        self.clear_temp_objects()

        min_point = np.minimum(self.start_point, self.end_point)
        max_point = np.maximum(self.start_point, self.end_point)

        width = max_point[0] - min_point[0]
        length = max_point[1] - min_point[1]
        thickness = self.tools_widget.get_foundation_thickness()

        if width < 0.1 or length < 0.1:
            print("Ошибка: слишком маленькие размеры фундамента")
            QMessageBox.warning(self, "Ошибка", "Размеры фундамента слишком малы. Попробуйте выбрать большую область.")
            return

        foundation = pv.Cube(
            center=((min_point[0] + max_point[0]) / 2,
                    (min_point[1] + max_point[1]) / 2,
                    min_point[2] + thickness / 2),
            x_length=width,
            y_length=length,
            z_length=thickness
        )

        # Генерация "напряжений" для визуализации
        stress = np.zeros(foundation.n_points)

        # Простая модель распределения напряжений
        center = np.array([(min_point[0] + max_point[0]) / 2,
                           (min_point[1] + max_point[1]) / 2,
                           min_point[2] + thickness / 2])

        points = foundation.points
        for i, point in enumerate(points):
            # Расстояние от центра фундамента
            dist = np.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
            # Простая модель напряжений: больше у краев, меньше в центре
            stress[i] = 1e6 * (1 - np.exp(-dist / 2))

        foundation["stress"] = stress

        # Добавляем цветовую шкалу только при первом добавлении фундамента
        if not self.foundations:
            self.plotter.add_scalar_bar(title="Напряжение (Па)", n_labels=4, interactive=True)

        actor = self.plotter.add_mesh(
            foundation,
            scalars="stress",
            cmap="coolwarm",
            show_edges=True
        )

        # Сохранение информации о фундаменте
        foundation_data = {
            "actor": actor,
            "geometry": foundation,
            "position": ((min_point[0] + max_point[0]) / 2,
                         (min_point[1] + max_point[1]) / 2,
                         min_point[2] + thickness / 2),
            "dimensions": (width, length, thickness)
        }

        self.foundations.append(foundation_data)
        print(f"Фундамент создан успешно. Размеры: {width:.2f}м x {length:.2f}м x {thickness:.2f}м")

        # Активация кнопки применения
        self.tools_widget.apply_btn.setEnabled(True)

    def add_guide_line(self, start_point, end_point):
        """Добавление постоянной вспомогательной линии"""
        line = pv.Line(start_point, end_point)
        self.plotter.add_mesh(line, color="blue", line_width=3)
        print(f"Добавлена вспомогательная линия от {start_point} до {end_point}")

    def clear_temp_objects(self):
        """Удаление временных объектов предпросмотра"""
        if hasattr(self, 'temp_actor') and self.temp_actor is not None:
            try:
                # Проверяем, существует ли актер в сцене
                if self.plotter.renderer.has_actor(self.temp_actor):
                    self.plotter.remove_actor(self.temp_actor)
                print("Временные объекты удалены")
            except Exception as e:
                print(f"Ошибка при удалении временного объекта: {e}")
            finally:
                self.temp_actor = None

    def apply_changes(self):
        """Применение изменений к созданной модели"""
        if not self.foundations:
            print("Нет фундаментов для применения")
            return

        print("Применение изменений к фундаментам...")
        for i, foundation in enumerate(self.foundations):
            print(f"Фундамент #{i + 1}, размеры: {foundation['dimensions']}")
            # Здесь можно добавить реальный расчёт напряжений

        # Деактивация кнопки применения
        self.tools_widget.apply_btn.setEnabled(False)
        print("Изменения применены")


if __name__ == "__main__":
    print("Запуск Engineering Suite...")
    print(f"Текущая директория: {os.getcwd()}")

    app = QApplication(sys.argv)
    window = EngineeringSuiteApp()
    window.show()

    print("Приложение запущено. Для создания фундамента:")
    print("1. Нажмите кнопку 'Создать фундамент' в правой панели")
    print("2. Кликните в сцене для первой точки")
    print("3. Переместите мышь и кликните для второй точки")

    sys.exit(app.exec_())