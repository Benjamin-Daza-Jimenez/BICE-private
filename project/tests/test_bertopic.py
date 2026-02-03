import func.bertopic as bertopic
import unittest
import pandas as pd
import contextlib
import os 

class TestBERTopic(unittest.TestCase):
    def setUp(self):
        """Datos de prueba"""
        self.dfTest = pd.DataFrame({
            'Descripcion': [
                'Error de login usuario no accede', 'Usuario bloqueado no puede entrar',
                'Problema acceso login', 'No permite iniciar sesion usuario',
                'Error credenciales acceso', 'Fallo autenticacion login'
            ] * 30, 
            'Causa': ['Credenciales invalidas'] * 180,
            'Solucion': ['Resetear password'] * 180,
            'Resumen': ['Error acceso'] * 180
        })

        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull):
                self.dfResultado = bertopic.bertopic_app(
                    self.dfTest, 
                    ['Descripcion', 'Causa', 'Solucion', 'Resumen'], 
                    verbose=False
                )
    
    def test_BERTopic_Columnas(self):
        """Verifica creación de nuevas columnas de temas"""
        self.assertIn('Temas_Descripcion', self.dfResultado.columns)
        self.assertIn('Temas_Causa', self.dfResultado.columns)
        self.assertIn('Temas_Solucion', self.dfResultado.columns)
        self.assertIn('Temas_Resumen', self.dfResultado.columns)

    def test_BERTopic_No_Nulos(self):
        """Verifica que las nuevas columnas no estén vacías"""
        self.assertTrue(self.dfResultado['Temas_Descripcion'].notna().all())
        self.assertTrue(self.dfResultado['Temas_Causa'].notna().all())
        self.assertTrue(self.dfResultado['Temas_Solucion'].notna().all())
        self.assertTrue(self.dfResultado['Temas_Resumen'].notna().all())
    
if __name__ == '__main__':
    unittest.main()
