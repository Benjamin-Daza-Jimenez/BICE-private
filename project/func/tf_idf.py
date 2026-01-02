from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import func.data as data
import pandas as pd
import numpy as np
import nltk

config_tfidf = {
    'Resumen': 800,
    'Descripcion': 3000,
    'Causa': 1500,
    'Solucion': 1500
}

def tfidf_app(df, columnas_texto):
    '''
    Aplica la vectorización TF-IDF a una columna de texto del DataFrame.
    
    Parámetros:
        df: DataFrame a modificar
        columnas_texto: lista de nombres de las columnas de texto a las que se les aplicará TF-IDF
        max_features: número máximo de características a extraer
    Return:
        df: DataFrame modificado con las nuevas columnas TF-IDF añadidas
    '''
    try:
        nltk.download('stopwords', quiet=True)
        stop_words_es = stopwords.words('spanish')
    except Exception as e:
        print(f"Error al descargar stopwords: {e}")
        stop_words_es = None
    
    df_result = df.copy()
  
    for columna in columnas_texto:
        df_result = data.clean_bert(df_result, columna)
        if columna not in config_tfidf:
            continue

        max_features = config_tfidf[columna]

        vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stop_words_es)

        tfidf_matrix = vectorizer.fit_transform(df_result[columna].astype(str))
        feature_names = [f"tfidf_{columna}_{name}" for name in vectorizer.get_feature_names_out()]
        df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names, index=df_result.index)
        df_result = pd.concat([df_result, df_tfidf], axis=1)
        df_result.drop(columns=[columna], inplace=True)
    return df_result