from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

def bertopic_f(df, columnas):
    df_temp = df.copy()

    modelos = {}

    for columna in columnas:
        print(f"Procesando columna: {columna} con BERTopic")

        docs = df_temp[columna].fillna("No informado").astype(str).tolist()

        model = BERTopic(language="multilingual")
        topics, _ = model.fit_transform(docs)

        df_temp[f"Topic_{columna}"] = topics

        topic_info = model.get_topic_info()[['Topic', 'Name']]

        df_temp = df_temp.merge(
            topic_info, 
            left_on=f"Topic_{columna}", 
            right_on="Topic", 
            how="left"
        ).rename(columns={"Name": f"Topic_{columna}_Name"}).drop(columns=["Topic"])

        modelos[columna] = model
    
    # Guardat en excel
    df_temp.to_excel("BERTopic_Results.xlsx", index=False)