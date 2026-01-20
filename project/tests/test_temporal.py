import unittest
import pandas as pd
import os
import contextlib
from func.temporal import anual, mensual, temporal_app

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
                dfTemp = temporal_app(self.dfTest.copy(), nombre_archivo="Test_Temporal_Results.xlsx")

        
        self.assertIn('Año',dfTemp.columns)
        self.assertIn('Mes',dfTemp.columns)
        self.assertIn('Día',dfTemp.columns)

    def test_Valores(self):
        """Verificar datos"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest.copy(), nombre_archivo="Test_Temporal_Results.xlsx")
        
        valores_esperados = {
            'Año': [2022, 2022, 2023, 2023],
            'Mes': [1, 12, 1, 12],
            'Día': [1, 31, 1, 31]
        }
        self.assertListEqual(dfTemp['Año'].tolist(), valores_esperados['Año'])
        self.assertListEqual(dfTemp['Mes'].tolist(), valores_esperados['Mes'])
        self.assertListEqual(dfTemp['Día'].tolist(), valores_esperados['Día'])
    
    def test_Anual_Largo(self):
        """Verificar largo de rutas"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = anual(dfTemp)

        self.assertEqual(len(rutas), 2)

    def test_Anual_Existencia(self):
        """Verificar existencia de archivos"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = anual(dfTemp)
        
        self.assertTrue(all([os.path.exists(ruta) for ruta in rutas]))

    def test_Anual_Rutas(self):
        """Verificar rutas correctas"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = anual(dfTemp)
        
        self.assertIn('reports/anual_analysis_2022.png', rutas)
        self.assertIn('reports/anual_analysis_2023.png', rutas)
    
    def test_Mensual_Largo(self):
        """Verificar largo de rutas"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = mensual(dfTemp)

        self.assertEqual(len(rutas), 2)

    def test_Mensual_Existencia(self):
        """Verificar existencia de archivos"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = mensual(dfTemp)

        self.assertTrue(all([os.path.exists(ruta) for ruta in rutas]))

    def test_Mensual_Rutas(self):
        """Verificar rutas correctas"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                dfTemp = temporal_app(self.dfTest)
                rutas = mensual(dfTemp)
                
        self.assertIn('reports/mensual_analysis_2022.png', rutas)
        self.assertIn('reports/mensual_analysis_2023.png', rutas)

    def tearDown(self):
        """Eliminar archivos generados"""
        rutas_anual = ['reports/anual_analysis_2022.png', 'reports/anual_analysis_2023.png']
        rutas_mensual = ['reports/mensual_analysis_2022.png', 'reports/mensual_analysis_2023.png']
        ruta_data = ['data/Test_Temporal_Results.xlsx']
        for ruta in rutas_anual + rutas_mensual + ruta_data:
            if os.path.exists(ruta):
                os.remove(ruta)

if __name__ == '__main__':
    unittest.main()

