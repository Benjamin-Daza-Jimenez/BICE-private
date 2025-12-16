import pandas as pd

def distribucion(df, columna):
    """
    Calcula la distribución de valores en una columna específica del DataFrame.

    Parámetros:
    df (pd.DataFrame): El DataFrame de entrada.
    columna (str): El nombre de la columna para la cual se calculará la distribución.

    Retorna:
    Una tupla con la media, mediana, moda, valor máximo y valor mínimo de la columna.
    """
    mean = df[columna].mean()
    median = df[columna].median()
    mode = df[columna].mode().iloc[0]
    max = df[columna].max()
    min = df[columna].min()
    return mean, median, mode, max, min