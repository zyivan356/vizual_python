# core/fem_solver.py
import subprocess
import json
import numpy as np

def run_geotech_analysis(geom_file, material_params):
    """
    Интеграция с Code_Aster (открытый МКЭ-решатель)
    """
    # Подготовка командного файла для Code_Aster
    comm_file = f"""
    DEBUT(LANG='RU')
    MAIL = LIRE_MAILLAGE(FORMAT='MED', UNITE=20)
    MAT = DEFI_MATERIAU(ELAS=_F(E={material_params['E']}, NU={material_params['nu']}))
    ...
    FIN()
    """

    # Запуск через subprocess
    result = subprocess.run([
        "aster",
        "-commande", "analysis.comm",
        "-num_job", "12345"
    ], capture_output=True)

    # Парсинг результатов
    with open("results.rmed") as f:
        stresses = parse_med_file(f)  # Кастомный парсер MED-формата

    return stresses

# В GUI: при нажатии кнопки "Рассчитать"
if user_clicked_calculate:
    results = run_geotech_analysis("foundation.med", {"E": 210e9, "nu": 0.3})
    viz.show_stress_map(results)  # Визуализация в PyVista