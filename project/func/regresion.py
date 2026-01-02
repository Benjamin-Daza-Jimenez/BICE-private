import func.data as data
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

COLUMNS = [
    'Prioridad',
    'Equipo',
    'Fecha_Inicio',
    'Duracion',
    'Activo_SW',    
    'Reporte',
    'Resuelto_con'
]

def regresion_data(df_original):
    
    df = df_original[COLUMNS].copy()

    # Aplicar codificación cíclica a las fechas
    df = data.cyclical_encoding(df, 'Fecha_Inicio')

    # Convertir texto de Priority a numérico
    diccionario = {'Lowest':1, 'Low':2, 'Medium':3, 'High':4, 'Highest':5}    
    df = data.text_to_number(df, 'Prioridad', diccionario)

    # Aplicar Target Encoding
    df = data.target_encoding(df, ['Activo_SW', 'Reporte', 'Equipo'], 'Duracion')

    # Aplicar One-Hot Encoding
    df = data.OHE(df, 'Resuelto_con')

    return df

def tree_regression(x, y):

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

    imp = importancia(model, x)

    return mse, r2, imp

def importancia(model, x):
    importancias = model.feature_importances_
    nombres = x.columns

    df_importancia = pd.DataFrame({
        'Columna': nombres,
        'Importancia (%)': (importancias * 100).round(2)
    })
    df_importancia = df_importancia.sort_values(by='Importancia (%)', ascending=False)

    return df_importancia