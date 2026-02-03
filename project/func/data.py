import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import TargetEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import spacy
import streamlit as st

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
    df = df.dropna(subset=[fecha_inicio_col, fecha_fin_col])
    df = df[df[fecha_fin_col] >= df[fecha_inicio_col]]
    
    df.loc[:, nueva_col] = (df[fecha_fin_col] - df[fecha_inicio_col]) // np.timedelta64(1, 'h')
    df.loc[:, nueva_col] = df[nueva_col].astype('int64')
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

    df = clean(df, [columna], columna)

    columnWeek = columna + '_Semanal'
    columnMonth = columna + '_Mensual'
    columnYear = columna + '_Anual'

    # Extraer día de la semana y día del mes
    df[columnWeek] = df[columna].dt.dayofweek + 1
    df[columnMonth] = df[columna].dt.day
    df[columnYear] = df[columna].dt.month

    # Aplicar codificación cíclica
    df[columnWeek + '_Sen'] = np.sin(2 * np.pi * (df[columnWeek]-1) / 7)
    df[columnWeek + '_Cos'] = np.cos(2 * np.pi * (df[columnWeek]-1) / 7)
    df[columnMonth + '_Sen'] = np.sin(2 * np.pi * (df[columnMonth]-1) / 31)
    df[columnMonth + '_Cos'] = np.cos(2 * np.pi * (df[columnMonth]-1) / 31)
    df[columnYear + '_Sen'] = np.sin(2 * np.pi * (df[columnYear]-1) / 12)
    df[columnYear + '_Cos'] = np.cos(2 * np.pi * (df[columnYear]-1) / 12)
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
    df = df.dropna(subset=[columna])
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
    encoder = TargetEncoder(target_type='continuous', smooth="auto")
    X = df[columnas]
    y = df[target_col]
    df[columnas] = encoder.fit_transform(X, y)
    return df

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

def clean_bert(df, columna):

    nlp = obtener_modelo_spacy()

    def ejecutar_regex(texto):
        if pd.isna(texto) or not isinstance(texto, str):
            return ""

        texto = texto.lower()
        texto = re.sub(r'mailto:\S+', ' ', texto)
        texto = re.sub(r'\b(type|content|paragraph|mediasingle|attrs|expand|media)\b', ' ', texto, flags=re.I)
        texto = re.sub(r'\{[^{}]*\}', ' ', texto)
        texto = re.sub(r'http[s]?://\S+|www\.\S+', ' ', texto) 
        texto = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', texto)
        texto = re.sub(r'\b\d{1,2}(?:\.?\d{3}){2}-?[\dkK]\b', ' ', texto)
        texto = re.sub(r'!.*?!', ' ', texto)
        texto = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', texto)
        texto = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', texto)
        texto = re.sub(r'[^a-zñáéíóú\s]', ' ', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto

    def remover_nombres(texto):
        if pd.isna(texto) or not isinstance(texto, str): 
            return ""
        doc = nlp(texto)
        tokens_sin_nombres = [token.text for token in doc if token.ent_type_ != 'PER']
        texto_sin_nombres = " ".join(tokens_sin_nombres)
        return ejecutar_regex(texto_sin_nombres)

    df['temp_para_modelo'] = df[columna].apply(remover_nombres)
    df[columna] = df[columna].apply(ejecutar_regex)

    df = df[df['temp_para_modelo'] != ""].copy()

    return df

@st.cache_resource
def obtener_modelo_spacy():
    """
    Esta función se ejecuta SOLO UNA VEZ en toda la vida de la app.
    La próxima vez que se llame, Streamlit devolverá el modelo guardado en RAM.
    """
    try:
        return spacy.load("es_core_news_md")
    except OSError:
        try:
            return spacy.load("es_core_news_sm")
        except OSError:
            from spacy.cli import download
            download("es_core_news_md")
            return spacy.load("es_core_news_md")