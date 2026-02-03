import unittest
import pandas as pd
import os
import contextlib
from func.temporal import temporal_app

class TestTemporal(unittest.TestCase):

    def setUp(self):
        """Datos de prueba"""
        self.dfTest = pd.DataFrame({
            'Fecha_Inicio': pd.to_datetime(['2022-01-01', '2022-12-31', '2023-01-01', '2023-12-31']),
            'Duracion': [0, 10, 15, 20],
            'Otro': ['A', 'B', 'C', 'D']
            })
    
    def test_Columnas(self):
        """Verifica pertenencia de columnas"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest.copy())

        
        self.assertIn('Año',dfTemp.columns)
        self.assertIn('Mes',dfTemp.columns)
        self.assertIn('Día',dfTemp.columns)

    def test_Valores(self):
        """Verificar datos"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest.copy())
        
        valores_esperados = {
            'Año': [2022, 2022, 2023, 2023],
            'Mes': [1, 12, 1, 12],
            'Día': [1, 31, 1, 31]
        }
        self.assertListEqual(dfTemp['Año'].tolist(), valores_esperados['Año'])
        self.assertListEqual(dfTemp['Mes'].tolist(), valores_esperados['Mes'])
        self.assertListEqual(dfTemp['Día'].tolist(), valores_esperados['Día'])

if __name__ == '__main__':
    unittest.main()

