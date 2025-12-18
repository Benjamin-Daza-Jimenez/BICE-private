'''
Manejo de los datos del proyecto, funciones para procesar y guardar datos.
'''
import pandas as pd
import numpy as np
from category_encoders import TargetEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords

def duracion(df, fecha_inicio_col, fecha_fin_col, nueva_col):
    '''
    Calcula la duración entre dos columnas de fechas y crea una nueva columna con el resultado.
    
    Parámetros:
        df: DataFrame a modificar
        fecha_inicio_col: nombre de la columna con la fecha de inicio
        fecha_fin_col: nombre de la columna con la fecha de fin
        nueva_col: nombre de la nueva columna donde se almacenará la duración en horas
    Return:
        df: DataFrame modificado con la nueva columna de duración añadida
    '''
    df[nueva_col] = (df[fecha_fin_col] - df[fecha_inicio_col]) // np.timedelta64(1, 'h')
    df[nueva_col] = df[nueva_col].astype('int64')
    df.drop(columns=[fecha_fin_col], inplace=True)
    return df

def clean(df, columnas_seleccionadas, ordenar):
    '''
    Limpia el DataFrame de incidentes:
    - Limpia los datos eliminando filas con valores nulos, duplicados y ordena.

    Parámetros:
        df: DataFrame original con todos los datos de incidentes
        columnas_seleccionadas: lista de columnas relevantes a seleccionar
        ordenar: columna por la cual ordenar el DataFrame limpio
    Return:
        df_limpio: DataFrame limpio
    '''
    # Limpieza de datos: eliminar filas con valores nulos y duplicados
    df_limpio = df.dropna(subset=columnas_seleccionadas)
    df_limpio = df_limpio.drop_duplicates()
    # Ordenar por 'Fecha Real Incidente' y convertir 'Duración Incidente' a int64
    df_limpio.sort_values(by=ordenar, inplace=True)
    return df_limpio

def cyclical_encoding(df, columna):
    '''
    Convierte una columna de tipo fecha a un formato conveniente:
        - Lunes a viernes (1-7).
        - Días del mes (1-31).
        - Mes del año (1-12).
    Convierte las columnas de formato conveniente a sen y cos para análisis temporal (-1 a 1).
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna de tipo fecha a convertir
    Return:
        df: DataFrame modificado con las nuevas columnas sen y cos añadidas
    '''
    columnWeek = columna + '_Semanal'
    columnMonth = columna + '_Mensual'
    columnYear = columna + '_Anual'

    # Extraer día de la semana y día del mes
    df[columnWeek] = df[columna].dt.dayofweek + 1
    df[columnMonth] = df[columna].dt.day
    df[columnYear] = df[columna].dt.month

    # Aplicar codificación cíclica
    df[columnWeek + '_Sen'] = np.sin(2 * np.pi * df[columnWeek] / 7)
    df[columnWeek + '_Cos'] = np.cos(2 * np.pi * df[columnWeek] / 7)
    df[columnMonth + '_Sen'] = np.sin(2 * np.pi * df[columnMonth] / 31)
    df[columnMonth + '_Cos'] = np.cos(2 * np.pi * df[columnMonth] / 31)
    df[columnYear + '_Sen'] = np.sin(2 * np.pi * df[columnYear] / 12)
    df[columnYear + '_Cos'] = np.cos(2 * np.pi * df[columnYear] / 12)
    df.drop(columns=[columna], inplace=True)
    return df

def text_to_number(df, columna, diccionario):
    '''
    Convierte una columna de texto en números asignando un número único a cada valor de texto.
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna de texto a convertir
    Return:
        df: DataFrame modificado con la columna convertida a números
    '''
    df[columna] = df[columna].map(diccionario)
    df = df.astype({columna: 'int64'})
    return df

def OHE(df, columna):
    '''
    Aplica One-Hot Encoding a una columna categórica del DataFrame.
    
    Parámetros:
        df: DataFrame a modificar
        columna: nombre de la columna categórica a la que se le aplicará One-Hot Encoding
    Return:
        df: DataFrame modificado con las nuevas columnas One-Hot Encoding añadidas
    '''
    dummies = pd.get_dummies(df[columna], prefix=columna, dtype='int64')
    df = pd.concat([df, dummies], axis=1)
    df.drop(columns=[columna], inplace=True)
    return df

def target_encoding(df, columnas, target_col):
    '''
    Aplica Target Encoding a las columnas categóricas especificadas del DataFrame.

    Parámetros:
        df: DataFrame a modificar
        columnas: lista de nombres de las columnas categóricas a las que se les aplicará Target Encoding
        target_col: nombre de la columna objetivo utilizada para el encoding
    Return:
        df: DataFrame modificado con las columnas Target Encoding añadidas
    '''
    encoder = TargetEncoder(cols=columnas, smoothing=10)
    df[columnas] = encoder.fit_transform(df[columnas], df[target_col], dtype='float64')
    return df

def tfidf(df, columnas_texto, max_features=50):
    '''
    Aplica la vectorización TF-IDF a una columna de texto del DataFrame.
    
    Parámetros:
        df: DataFrame a modificar
        columna_texto: nombre de la columna de texto a la que se le aplicará TF-IDF
        max_features: número máximo de características a extraer
    Return:
        df: DataFrame modificado con las nuevas columnas TF-IDF añadidas
    '''
    try:
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        print(f"Error al descargar stopwords: {e}")
    
    df_result = df.copy()

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stopwords.words('spanish'), dtype=np.float64)
    for columna in columnas_texto:
        tfidf_matrix = vectorizer.fit_transform(df_result[columna].astype(str))

        feature_names = [f"tfidf_{columna}_{name}" for name in vectorizer.get_feature_names_out()]

        df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names, index=df_result.index)

        df_result = pd.concat([df_result, df_tfidf], axis=1)
        df_result.drop(columns=[columna], inplace=True)
    
    return df_result
def save_data(df, path):
    '''
    Guarda el DataFrame en un archivo CSV en la ruta especificada.
    
    Parámetros:
        df: DataFrame a guardar
        path: ruta donde se guardará el archivo CSV
    Return:
        None
    '''
    try: 
        df.to_csv(path, index=False)
        print(f'DataFrame guardado exitosamente en {path}')
    except Exception as e:
        print(f'Error al guardar el DataFrame: {e}')

def carga_equipos(df):
    df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
    df['Fecha_Fin'] = pd.to_datetime(df['Fecha_Fin'])
    df = df[df['Fecha_Fin'] >= df['Fecha_Inicio']].copy()

    inicio = df['Fecha_Inicio'].values
    fin = df['Fecha_Fin'].values
    equipos = df['Equipo'].values

    mismo_equipo = equipos[:, None] == equipos[None, :]
    empezo_antes_o_igual = inicio[None, :] <= inicio[:, None]  # inicio[j] <= inicio[i]
    no_ha_terminado = fin[None, :] >= inicio[:, None]          # fin[j] >= inicio[i]

    carga_vectorizada = np.sum(mismo_equipo & empezo_antes_o_igual & no_ha_terminado, axis=1) -1
    
    # Restar 1 para no contar el ticket consigo mismo
    df['Carga_Equipo'] = carga_vectorizada

    return df