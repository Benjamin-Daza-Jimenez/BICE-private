import Data_Management.limpieza as limpieza
import Data_Management.manejo as manejo
import Data_Management.graficar as graficar
import pandas as pd
import numpy as np

RUTA_DATA = 'DB/BaseIncidentesBot.xlsx'

COLUMNAS = [
        'Key',
        'Status',
        'Priority', # IMPORTANTE
        'Equipo Resolutor',
        'Assignee',
        'Fecha Real Incidente', # IMPORTANTE
        'Fecha Resolución Real Incidente', # IMPORTANTE
        'Tiempo de Ejecución',
        'Fecha Inicio Ejecución',
        'Duración Incidente', # IMPORTANTE
        'Activo de SW',
        'GDI',
        'Servicio Reportado',
        'Resuelto con:', # IMPORTANTE
        'Causa Raíz/Origen',
        'Descripción de la Solución' # IMPORTANTE
    ]

COLUMNAS_SELECCIONADAS = [
        'Priority',
        'Fecha Real Incidente',
        'Fecha Resolución Real Incidente',
        'Duración Incidente',
        'Resuelto con:',
        'Descripción de la Solución:'
    ]

def prueba_1(df_limpio):
    df1 = df_limpio[df_limpio['Duración Incidente'] < 120]
    x = df1[['Priority', 
    'Fecha Real Incidente Semanal sen', 
    'Fecha Real Incidente Semanal cos',
    'Resuelto con:_Negocio']]
    y = df1['Duración Incidente']

    print("\nResultados de la Regresión Lineal 1:")
    manejo.regresion_lineal(x, y)

def prueba_2(df_limpio):
    df = df_limpio[df_limpio['Duración Incidente'] < 100]
    df = df[df['Duración Incidente'] > 10]
    x = df[['Priority', 
    'Fecha Real Incidente Semanal sen', 
    'Fecha Real Incidente Semanal cos',
    'Resuelto con:_Negocio']]
    y = df['Duración Incidente']
    print("Resultados de la Regresión Lineal 2:")
    manejo.regresion_lineal(x, y)
    
    # Desarrollo Segunda Prueba

    # Columna Priority vs Duración Incidente
    print("\nAnálisis de la Segunda Prueba:")
    graficar.grafico_box(df, 'Priority', 'Duración Incidente', 'box_priority_vs_duracionIncidente_(2)') 
    meanP1 = df[df['Priority'] == 1]['Duración Incidente'].mean()
    meanP2 = df[df['Priority'] == 2]['Duración Incidente'].mean()
    meanP3 = df[df['Priority'] == 3]['Duración Incidente'].mean()
    meanP4 = df[df['Priority'] == 4]['Duración Incidente'].mean()
    meanP5 = df[df['Priority'] == 5]['Duración Incidente'].mean()
    print(f"\nMedia Duración Incidente por Priority (2):\nPriority 1: {meanP1}\nPriority 2: {meanP2}\nPriority 3: {meanP3}\nPriority 4: {meanP4}\nPriority 5: {meanP5}\n")

    # Columna Fecha Real Incidente Semanal vs Duración Incidente
    print("Conteo de Incidentes por Día de la Semana:")
    print(df['Fecha Real Incidente Semanal'].value_counts().sort_index())

def main():
    # Cargar datos desde el archivo Excel
    df_general = pd.read_excel(RUTA_DATA, sheet_name='Base')

    # Separar y limpiar datos
    df_separado, df_limpio = limpieza.separar(df_general, COLUMNAS_SELECCIONADAS, 'Fecha Real Incidente') # Se deja df_separado, contiene valores vacíos
    df_limpio = df_limpio.drop(columns = ['Descripción de la Solución:']) # Se elimina columna no numérica

    # --------------------------------- Regresión lineal --------------------------------

    # Convertir fechas a formato cíclico
    df_limpio = limpieza.convertir_fecha_a_ciclica(df_limpio,'Fecha Real Incidente')
    df_limpio = limpieza.convertir_fecha_a_ciclica(df_limpio,'Fecha Resolución Real Incidente')

    # Aplicar tipos de datos
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Duración Incidente', 'int64')

    # Convertir texto de 'Priority' a números
    diccionario = {'Lowest':1, 'Low':2, 'Medium':3, 'High':4, 'Highest':5}
    df_limpio = limpieza.convertir_texto_a_numero(df_limpio, 'Priority', diccionario)
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Priority', 'int64')

    # Convertir con OHE la columna 'Resuelto con:'
    df_limpio = limpieza.OHE(df_limpio, 'Resuelto con:')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Configuración', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Equipo Resolutor', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Gestión', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_MIB', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Modificación de Datos/Param', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Negocio', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Paso a Producción', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Reinicio', 'int64')
    df_limpio = limpieza.aplicar_tipo(df_limpio, 'Resuelto con:_Soporte', 'int64')

    # Guardar DataFrames resultantes
    limpieza.guardar_dataframe(df_separado, 'DB/Incidentes_Separado.xlsx')
    limpieza.guardar_dataframe(df_limpio, 'DB/Incidentes_Limpio.xlsx')

    # Mostrar información del DataFrame limpio
    print("\nInformación del DataFrame limpio:\n")
    df_limpio.info()
    
    # Llamar funciones del archivo manejo.py
    mean, median, mode, max, min =  manejo.distribucion(df_limpio, 'Duración Incidente')

    # Primera prueba
    prueba_1(df_limpio)

    # Segunda prueba
    prueba_2(df_limpio)
    
    

    # --------------------------------- Fin Regresión lineal --------------------------------
    # ------------------------------------ Clasificación ------------------------------------

    # ---------------------------------- Fin Clasificación ----------------------------------

if __name__ == '__main__':
    main()