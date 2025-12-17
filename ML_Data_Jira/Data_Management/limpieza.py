import pandas as pd
import numpy as np

def separar(df, columnas_seleccionadas, ordenar):
    '''
    Separa y limpia el DataFrame de incidentes:
    - Separa por las columnas relevantes de la lista columnas_seleccionadas.
    - Limpia los datos eliminando filas con valores nulos, duplicados y ordena.

    Parámetros:
        df: DataFrame original con todos los datos de incidentes
        columnas_seleccionadas: lista de columnas relevantes a seleccionar
        ordenar: columna por la cual ordenar el DataFrame limpio

    Return:
        tupla con dos DataFrames: (df_separado, df_limpio)
    '''

    # DataFrame con las columnas seleccionadas
    df_separado = df[columnas_seleccionadas].copy()

    # Limpieza de datos: eliminar filas con valores nulos y duplicados
    df_limpio = df_separado.dropna(subset=columnas_seleccionadas)
    df_limpio = df_limpio.drop_duplicates()

    # Ordenar por 'Fecha Real Incidente' y convertir 'Duración Incidente' a int64
    df_limpio.sort_values(by=ordenar, inplace=True)

    return df_separado, df_limpio





def aplicar_tipo(df, columna, tipo):
    '''
    Aplica un tipo de dato específico a una columna del DataFrame.
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna a la que se le aplicará el tipo de dato
        tipo: tipo de dato a aplicar (por ejemplo, 'int64', 'float64', 'datetime64', etc.)
    Return:
        df: DataFrame modificado con la columna convertida al tipo de dato especificado
    '''
    df = df.astype({columna: tipo})
    return df





def convertir_fecha_a_ciclica(df,columna):
    '''
    Convierte una columna de tipo fecha a un formato conveniente:
        - Lunes a viernes (1-7).
        - Días del mes (1-31).
    Convierte las columnas de formato conveniente a sen y cos para análisis temporal (-1 a 1).
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna de tipo fecha a convertir
    
    Return:
        df: DataFrame modificado con las columnas de fecha en Codificación Cíclica (sen y cos) tanto semanal como mensual.
    '''
    columnaSemanal = columna + ' Semanal'
    columnaMensual = columna + ' Mensual'

    # Convertir fechas a formato conveniente
    df[columnaSemanal] = df[columna].dt.dayofweek + 1
    df[columnaMensual] = df[columna].dt.day

    # Convertir formato conveniente a sen y cos (Codificación cíclica)
    df[columnaSemanal + ' sen'] = np.sin(2 * np.pi * df[columnaSemanal] / 7)
    df[columnaSemanal + ' cos'] = np.cos(2 * np.pi * df[columnaSemanal] / 7)
    df[columnaMensual + ' sen'] = np.sin(2 * np.pi * df[columnaMensual] / 31)
    df[columnaMensual + ' cos'] = np.cos(2 * np.pi * df[columnaMensual] / 31)

    # Borrar columnas originales de fechas y formatos convenientes
    df.drop(columns=[columna], inplace=True)

    return df





def convertir_texto_a_numero(df, columna, diccionario):
    '''
    Transforma una columna de texto en números enteros según un diccionario de mapeo.
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna de texto a transformar
        diccionario: diccionario de mapeo de texto a números enteros
    Return:
        df: DataFrame modificado con la columna transformada a números enteros
    '''
    df[columna] = df[columna].map(diccionario)
    df = df.astype({columna: 'int64'})
    return df





def OHE(df, columna):
    '''
    Aplica One-Hot Encoding a una columna categórica del DataFrame.
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna categórica a transformar
    Return:
        df: DataFrame modificado con la columna transformada mediante One-Hot Encoding
    '''
    dummies = pd.get_dummies(df[columna], prefix=columna)
    df = pd.concat([df, dummies], axis=1)
    df = df.drop(columns=[columna])
  
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