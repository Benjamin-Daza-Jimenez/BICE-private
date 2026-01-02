from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
import func.data as data

def bertopic_app(df, columnas):
    df_temp = df.copy()

    try:
        stop_words_es = stopwords.words('spanish')
    except:
        stop_words_es = []

    stop_words_es.extend(['que', 'el', 'la', 'en', 'de', 'para', 'se', 'no', 'si', 'un', 'con'])
    vectorizer_model = CountVectorizer(stop_words=stop_words_es)

    for columna in columnas:
        print(f"Procesando columna: {columna} con BERTopic")

        df_temp = data.clean_bert(df_temp, columna)
        df_temp['temp_limpieza'] = df_temp[columna]

        docs = df_temp['temp_limpieza'].astype(str).tolist()

        model = BERTopic(language="multilingual", vectorizer_model=vectorizer_model, verbose=True)
        topics, _ = model.fit_transform(docs)

        new_topics = model.reduce_outliers(docs, topics, strategy="c-tf-idf")

        topic_info = model.get_topic_info().set_index('Topic')['Name'].to_dict()

        nombres_temas = []
        for t in new_topics:
            nombre = topic_info.get(t, "Sin Clasificar")

            nombre_limpio = nombre.split('_', 1)[-1].replace('_', ' ').title() if '_' in nombre else nombre
            nombres_temas.append(nombre_limpio)
        
        idx_original = df_temp.columns.get_loc(columna)
        nombre_nueva_col = f"Temas_{columna}"

        df_temp.insert(idx_original + 1, nombre_nueva_col, nombres_temas)
        df_temp.drop(columns=['temp_limpieza'], inplace=True)
    
    df_temp.to_excel("data/BERTopic_Results.xlsx", index=False)
    return df_temp