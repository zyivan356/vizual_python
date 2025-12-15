# bim/ifc_importer.py
import ifcopenshell
import ifcopenshell.geom


def import_ifc_file(file_path):
    """Импорт IFC-файла в внутреннюю структуру данных"""
    model = ifcopenshell.open(file_path)

    # Извлечение стен
    walls = model.by_type("IfcWall")
    for wall in walls:
        geometry = ifcopenshell.geom.create_shape(
            ifcopenshell.geom.settings(),
            wall
        )
        mesh = convert_to_pyvista_mesh(geometry)  # Конвертация в формат PyVista
        scene.add(mesh, color="brick")

    # Извлечение материалов
    materials = extract_materials(model)
    return BimModel(geometries=meshes, materials=materials)


# В интерфейсе:
if user_clicked_import_ifc:
    model = import_ifc_file("building.ifc")
    gui.model_tree.populate(model)  # Заполнение дерева объектов