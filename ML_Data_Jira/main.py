import Data_Management.limpieza as limpieza
import Data_Management.manejo as manejo
import pandas as pd

RUTA_DATA = 'DB/BaseIncidentesBot.xlsx'

'''
Columnas
        [0] 'Priority'
        [1] 'Fecha Real Incidente'
        [2] 'Fecha Resolución Real Incidente'
        [3] 'Duración Incidente'
        [4] 'Resuelto con:'
        [5] 'Descripción de la Solución:'
'''

def main():
    df_general = pd.read_excel(RUTA_DATA, sheet_name='Base')

    # Llamar funciones del archivo limpieza.py
    df_separado, df_limpio = limpieza.separar(df_general) # Se deja df_separado, contiene valores vacíos

    df_limpio = limpieza.conversion(df_limpio)

    limpieza.guardar_dataframe(df_separado, 'DB/Incidentes_Separado.xlsx')
    limpieza.guardar_dataframe(df_limpio, 'DB/Incidentes_Limpio.xlsx')

    # Llamar funciones del archivo manejo.py
    #datos_3 =  manejo.distribucion(df_limpio, 'Duración Incidente')


if __name__ == '__main__':
    main()