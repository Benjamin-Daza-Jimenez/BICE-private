import pandas as pd
import numpy as np

def separar(df):
    '''
    Separa y limpia el DataFrame de incidentes:
    - Separa por las columnas relevantes de la lista columnas_seleccionadas.
    - Limpia los datos eliminando filas con valores nulos, duplicados, ordena por fecha y convierte tipos de datos.

    Parámetros:
    df: DataFrame original con todos los datos de incidentes
    :return: tupla con dos DataFrames: (df_separado, df_limpio)
    '''

    columnas = [
        'Key',
        'Status',
        'Priority', # IMPORTANTE
        'Equipo Resolutor',
        'Assignee',
        'Fecha Real Incidente', # IMPORTANTE
        'Fecha Resolucióon Real Incidente', # IMPORTANTE
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

    columnas_seleccionadas = [
        'Priority',
        'Fecha Real Incidente',
        'Fecha Resolución Real Incidente',
        'Duración Incidente',
        'Resuelto con:',
        'Descripción de la Solución:'
    ]

    # DataFrame con las columnas seleccionadas
    df_separado = df[columnas_seleccionadas].copy()

    # Limpieza de datos: eliminar filas con valores nulos y duplicados
    df_limpio = df_separado.dropna(subset=columnas_seleccionadas)
    df_limpio = df_limpio.drop_duplicates()

    # Ordenar por 'Fecha Real Incidente' y convertir 'Duración Incidente' a int64
    df_limpio.sort_values(by='Fecha Real Incidente', inplace=True)
    df_limpio = df_limpio.astype({'Duración Incidente': 'int64'})

    # Borrar descripción de la solución
    df_limpio.drop(columns=['Descripción de la Solución:'], inplace=True)

    print("\n---- Primeras 10 filas del DataFrame limpio ----\n")
    print(df_limpio.head(10))

    return df_separado, df_limpio





def conversion(df):
    '''
    - Convierte la columna Priority de texto a valores numéricos (1-5).
    - Convierte la columnas de tipo fecha a un formato conveniente:
        * Lunes a viernes (1-7).
        * Días del mes (1-31).
    - Convierte las columnas de formato conveniente a sen y cos para análisis temporal (-1 a 1).
    
    Parámetros:
    df: DataFrame a modificar

    Return:
    df: DataFrame modificado con:
        - La columna Priority en formato int64
        - Las columnas de fecha en Codificación Cíclica (sen y cos) tanto semanal como mensual.
    '''

    # Convertir Priority de texto a numérico
    mapeo_prioridad = {'Lowest': 1, 'Low': 2,'Medium': 3, 'High': 4, 'Highest': 5}
    df['Priority'] = df['Priority'].map(mapeo_prioridad)
    df = df.astype({'Priority': 'int64'})

    # Convertir fechas a formato conveniente
    df['Fecha Real Incidente Semanal'] = df['Fecha Real Incidente'].dt.dayofweek + 1
    df['Fecha Real Incidente Mensual'] = df['Fecha Real Incidente'].dt.day
    df['Fecha Resolución Real Incidente Semanal'] = df['Fecha Resolución Real Incidente'].dt.dayofweek + 1
    df['Fecha Resolución Real Incidente Mensual'] = df['Fecha Resolución Real Incidente'].dt.day

    # Convertir formato conveniente a sen y cos (Codificación cíclica)
    df['Fecha Real Incidente Semanal sen'] = np.sin(2 * np.pi * df['Fecha Real Incidente Semanal'] / 7)
    df['Fecha Real Incidente Semanal cos'] = np.cos(2 * np.pi * df['Fecha Real Incidente Semanal'] / 7)
    df['Fecha Real Incidente Mensual sen'] = np.sin(2 * np.pi * df['Fecha Real Incidente Mensual'] / 31)
    df['Fecha Real Incidente Mensual cos'] = np.cos(2 * np.pi * df['Fecha Real Incidente Mensual'] / 31)
    df['Fecha Resolución Real Incidente Semanal sen'] = np.sin(2 * np.pi * df['Fecha Resolución Real Incidente Semanal'] / 7)
    df['Fecha Resolución Real Incidente Semanal cos'] = np.cos(2 * np.pi * df['Fecha Resolución Real Incidente Semanal'] / 7)
    df['Fecha Resolución Real Incidente Mensual sen'] = np.sin(2 * np.pi * df['Fecha Resolución Real Incidente Mensual'] / 31)
    df['Fecha Resolución Real Incidente Mensual cos'] = np.cos(2 * np.pi * df['Fecha Resolución Real Incidente Mensual'] / 31)  

    # Borrar columnas originales de fechas y formatos convenientes
    df.drop(columns=[
        'Fecha Real Incidente',
        'Fecha Resolución Real Incidente',
        'Fecha Real Incidente Semanal',
        'Fecha Real Incidente Mensual',
        'Fecha Resolución Real Incidente Semanal',
        'Fecha Resolución Real Incidente Mensual'
    ], inplace=True)

    # Generar variables dummies para la columna 'Resuelto con:'


    return df





def guardar_dataframe(df, ruta):
    '''
    Guarda los datos del dataframe en un archivo Excel en la carpeta DB.
    
    Parámetros:
    df: dataframe a guardar
    ruta: ruta del archivo Excel donde se guardará el dataframe
    '''
    try:    
        df.to_excel(ruta, index=False)
        print(f"\nDataFrame guardado en {ruta}")
    except Exception as e:
        print(f"\nError al guardar el DataFrame en {ruta}: {e}")