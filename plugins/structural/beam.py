# plugins/structural/beam.py
from pyOCCT.BRepPrimAPI import BRepPrimAPI_MakeBox
from pyOCCT.gp import gp_Pnt, gp_Dir, gp_Ax2


class Beam:
    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height

    def create_3d_model(self):
        """Создаёт 3D-модель балки через OpenCASCADE"""
        origin = gp_Pnt(0, 0, 0)
        axis = gp_Dir(0, 0, 1)
        plane = gp_Ax2(origin, axis)
        box = BRepPrimAPI_MakeBox(plane, self.length, self.width, self.height)
        return box.Shape()  # Возвращает OpenCASCADE-объект


# Использование в GUI:
beam = Beam(length=5.0, width=0.3, height=0.5)
shape = beam.create_3d_model()
scene.add(shape)  # Передача в визуализацию