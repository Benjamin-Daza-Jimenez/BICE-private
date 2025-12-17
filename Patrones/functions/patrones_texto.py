import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

stop_words = [
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 
    'un', 'para', 'con', 'no', 'una', 'su', 'al', 'es', 'lo', 'como',
    'saludos', 'estimados', 'gracias', 'adjunto', 'favor', 'buenos', 'días',
    'tardes', 'noches', 'atentamente', 'cordialmente', 'hola', 'estimado', 'equipo',
    'indica', 'ya', 'sin', 'realiza', 'debe', 'realizar'
]

def extraer_patrones_texto(df, columna_texto, keywords, max_features=10):
    stop_words_es = stop_words + keywords
    # Carga y Limpieza Vectorizada
    df['Clean_Description'] = df[columna_texto].astype(str).replace('nan', '').str.lower()
    df['Clean_Description'] = df['Clean_Description'].str.replace(r'[^a-z0-9\s]', '', regex=True)

    # Extracción de Metadatos y Patrones Numéricos
    df['Text_Length'] = df['Clean_Description'].str.len()
    df['Error_Code'] = df['Clean_Description'].str.extract(r'(\d{3})').fillna(0).astype(int)

    # Clasificación Temática mediante Keywords
    for kw in keywords:
        col_name = f'Has_{kw.replace(" ", "_")}'
        df[col_name] = np.where(df['Clean_Description'].str.contains(kw), 1, 0)
    
    # Vectorización TF-IDF
    vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stop_words_es, min_df=0.05, max_df=0.90)
    tfidf_matrix = vectorizer.fit_transform(df['Clean_Description'])
    tfidf_col = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    # Combinar DataFrames
    df_final = pd.concat([df.reset_index(drop=True), tfidf_col], axis=1)
    df_final.to_excel('DB/Patrones_Texto_Procesados.xlsx', index=False)
    return df_final