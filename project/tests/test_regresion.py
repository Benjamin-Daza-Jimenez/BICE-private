import func.regresion as regresion
import unittest
import pandas as pd
import contextlib
import os

COLUMNS = [
    'Prioridad',
    'Equipo',
    'Duracion',
    'Activo_SW',    
    'Reporte',
    'Fecha_Inicio_Semanal',
    'Fecha_Inicio_Mensual',
    'Fecha_Inicio_Anual',
    'Fecha_Inicio_Semanal_Sen',
    'Fecha_Inicio_Mensual_Sen',
    'Fecha_Inicio_Anual_Sen',
    'Fecha_Inicio_Semanal_Cos',
    'Fecha_Inicio_Mensual_Cos',
    'Fecha_Inicio_Anual_Cos',
    'Resuelto_con_C1',
    'Resuelto_con_C2',
    'Resuelto_con_C3',
    'Resuelto_con_C4',
    'Resuelto_con_C5',
]

class TestRegresion(unittest.TestCase):
    def setUp(self):
        """Datos de prueba"""
        self.dfTest = pd.DataFrame({
            'Prioridad': ['Lowest', 'Low', 'Medium', 'High', 'Highest', 'Highest', 'High', 'Medium', 'Low', 'Lowest'],
            'Equipo': ['A', 'B', 'C', 'B', 'A', 'C', 'B', 'A', 'C', 'B'],
            'Fecha_Inicio': pd.to_datetime(['2022-01-01', '2022-06-15', '2022-12-31', '2023-03-10', '2023-07-25', '2023-08-15', '2023-09-10', '2023-10-30', '2023-12-30', '2023-12-31']),
            'Duracion': [5, 10, 15, 20, 25, 10, 20, 5, 15, 25],
            'Activo_SW': ['X', 'Y', 'Z', 'W', 'V', 'Y', 'W', 'X', None, 'V'],
            'Reporte': ['R1', 'R2', 'R3', 'R4', 'R5', 'R2', 'R4', 'R1', 'R3', None],
            'Resuelto_con': ['C1', 'C2', 'C3', 'C4', 'C5', 'C2', 'C4', None, 'C3', 'C5']
        })

    def test_Regresion(self):
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfResultado = regresion.regresion_data(self.dfTest.copy()) 
        """Verifica que las columnas esperadas estén en el DataFrame resultante"""
        for col in COLUMNS:
            self.assertIn(col, dfResultado.columns)
    
    def test_Regresion_Prioridad(self):
        dfResultado = regresion.regresion_data(self.dfTest.copy()) 
        """Verifica que la columna 'Prioridad' haya sido convertida a numérico correctamente"""
        prioridad_esperada = [1, 2, 3, 4, 5, 5, 4, 2, 1]
        self.assertListEqual(dfResultado['Prioridad'].tolist(), prioridad_esperada)
    

    
        