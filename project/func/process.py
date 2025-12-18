import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

def distribucion(df, columna):
    """
    Calcula la media, mediana, moda, valor máximo y valor mínimo de una columna numérica en un DataFrame.

    Parámetros:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        columna (str): El nombre de la columna numérica para la cual se calcularán las estadísticas.
    
    Retorna:
        tuple: Una tupla que contiene la media, mediana, moda, valor máximo y valor mínimo de la columna.
    """
    mean = df[columna].mean()
    median = df[columna].median()
    mode = df[columna].mode().iloc[0]
    max = df[columna].max()
    min = df[columna].min()
    return mean, median, mode, max, min

def regresion_lineal(x, y):

    # Dividir los datos en conjuntos de entrenamiento y prueba
    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=42)

    # Crear el modelo de regresión lineal
    modelo = LinearRegression()

    # Entrenar el modelo
    modelo.fit(xTrain, yTrain)

    # Hacer predicciones
    yPred = modelo.predict(xTest)

    # Evaluar el modelo
    mse = mean_squared_error(yTest, yPred)
    r2 = r2_score(yTest, yPred)

    print(f"Mean Squared Error: {mse}")
    print(f"R^2 Score: {r2}\n")

def xgboost_regression(df, x, y):

    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(
        n_estimators=100, 
        max_depth=10, 
        n_jobs=-1,
        random_state=42
    )

    model.fit(xTrain, yTrain)

    yPred = model.predict(xTest)

    mse = mean_squared_error(yTest, yPred)
    r2 = r2_score(yTest, yPred)

    print(f"Mean Squared Error: {mse}")
    print(f"R^2 Score: {r2}\n")
    importancia(model, x)

def importancia(model, x):
    importancias = model.feature_importances_
    nombres = x.columns

    df_importancia = pd.DataFrame({
        'Columna': nombres,
        'Importancia': importancias
    })
    df_importancia = df_importancia.sort_values(by='Importancia', ascending=False).head(5)

    print("Importancia de las características:")
    print(df_importancia)