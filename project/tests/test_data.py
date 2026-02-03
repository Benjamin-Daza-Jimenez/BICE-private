import func.data as data
import unittest
import pandas as pd
import contextlib
import os
 
class TestData(unittest.TestCase):

    def setUp(self):
        """Datos de prueba"""
        self.dfTest = pd.DataFrame({
            'Fecha_Inicio': pd.to_datetime([
                '2022-01-01 08:00', 
                '2022-01-02 09:30',  
                '2022-12-04 11:15', 
                '2022-12-07 14:00', 
                None, 
                '2022-01-07 09:00'
                ]),
            'Fecha_Fin': pd.to_datetime([
                '2022-01-01 12:00', # Duración 4 horas
                '2022-01-02 11:29', # Duración 1 hora 59 min -> 1 hora
                '2022-12-04 11:20', # Duración 5 min -> 0 horas
                '2022-12-06 16:00', # Fecha_Inicio > Fecha_Fin -> eliminar
                '2022-01-07 10:00', # Fila con Fecha_Inicio None -> eliminar
                None                # Fila con Fecha_Fin None -> eliminar   
                ]),
            'Resuelto_con': [
                'A', 
                'B', 
                'C', 
                'B', 
                'B', 
                None]         
            })
        
    def test_Duracion(self):
        """Verifica duración correcta"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.duracion(self.dfTest.copy(), 'Fecha_Inicio', 'Fecha_Fin', 'Duracion')
        
        duracion_esperada = [4, 1, 0]
        self.assertListEqual(df['Duracion'].tolist(), duracion_esperada)
    
    def test_Clean_Eliminacion(self):
        """Verifica eliminación de filas con valores nulos/duplicados"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.clean(self.dfTest.copy(), ['Fecha_Inicio', 'Fecha_Fin'], 'Fecha_Inicio')

        self.assertEqual(len(df), 4)

    def test_Clean_Ordenamiento(self):
        """Verifica ordenamiento"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.clean(self.dfTest.copy(), ['Fecha_Inicio', 'Fecha_Fin'], 'Fecha_Inicio')
        
        self.assertTrue(df['Fecha_Inicio'].is_monotonic_increasing)
    
    def test_CyclicalEncoding_Columnas(self):
        """Verifica creación de columnas Año, Mes, Día y Día de la semana"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        self.assertIn('Fecha_Inicio_Anual', df.columns)
        self.assertIn('Fecha_Inicio_Mensual', df.columns)
        self.assertIn('Fecha_Inicio_Semanal', df.columns)

    def test_CyclicalEncoding_SenCos(self):
        """Verifica creación de columnas sen y cos"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        self.assertIn('Fecha_Inicio_Anual_Sen', df.columns)
        self.assertIn('Fecha_Inicio_Anual_Cos', df.columns)
        self.assertIn('Fecha_Inicio_Mensual_Sen', df.columns)
        self.assertIn('Fecha_Inicio_Mensual_Cos', df.columns)
        self.assertIn('Fecha_Inicio_Semanal_Sen', df.columns)
        self.assertIn('Fecha_Inicio_Semanal_Cos', df.columns)

    def test_CyclicalEncoding_Eliminacion(self):
        """Verifica eliminación de columna original"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        self.assertNotIn('Fecha_Inicio', df.columns)

    def test_CyclicalEncoding_Valores_Semanales(self):
        """Verifica valores semanales"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')
        
        valores_semanales_esperados = [6, 7, 5, 7, 3]
        self.assertListEqual(df['Fecha_Inicio_Semanal'].tolist(), valores_semanales_esperados)

    def test_CyclicalEncoding_Valores_Mensuales(self):
        """Verifica valores mensuales"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        valores_mensuales_esperados = [1, 2, 7, 4, 7]
        self.assertListEqual(df['Fecha_Inicio_Mensual'].tolist(), valores_mensuales_esperados)
    
    def test_CyclicalEncoding_Valores_Anuales(self):
        """Verifica valores anuales"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        valores_anuales_esperados = [1, 1, 1, 12, 12]
        self.assertListEqual(df['Fecha_Inicio_Anual'].tolist(), valores_anuales_esperados)

    def test_CyclicalEncoding_Valores_SenCos(self):
        """Verifica valores sen y cos dentro del rango [-1, 1]"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.cyclical_encoding(self.dfTest.copy(), 'Fecha_Inicio')

        self.assertTrue(df['Fecha_Inicio_Semanal_Sen'].between(-1, 1).all())
        self.assertTrue(df['Fecha_Inicio_Semanal_Cos'].between(-1, 1).all())
        self.assertTrue(df['Fecha_Inicio_Mensual_Sen'].between(-1, 1).all())
        self.assertTrue(df['Fecha_Inicio_Mensual_Cos'].between(-1, 1).all())
        self.assertTrue(df['Fecha_Inicio_Anual_Sen'].between(-1, 1).all())
        self.assertTrue(df['Fecha_Inicio_Anual_Cos'].between(-1, 1).all())

    def test_OHE_Columnas(self):
        """Verifica creación de columnas one-hot"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.OHE(self.dfTest.copy(), 'Resuelto_con')

        self.assertIn('Resuelto_con_A', df.columns)
        self.assertIn('Resuelto_con_B', df.columns)
        self.assertIn('Resuelto_con_C', df.columns)

    def test_OHE_Valores(self):
        """Verifica valores correctos en columnas one-hot"""
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                df = data.OHE(self.dfTest.copy(), 'Resuelto_con')

        valores_esperados_A = [1, 0, 0, 0, 0]
        valores_esperados_B = [0, 1, 0, 1, 1]
        valores_esperados_C = [0, 0, 1, 0, 0]

        self.assertListEqual(df['Resuelto_con_A'].tolist(), valores_esperados_A)
        self.assertListEqual(df['Resuelto_con_B'].tolist(), valores_esperados_B)
        self.assertListEqual(df['Resuelto_con_C'].tolist(), valores_esperados_C)
    
if __name__ == '__main__':
    unittest.main()