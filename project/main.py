import func.data as data
import func.process as process
import func.visualize as visualize
import pandas as pd
import numpy as np

PATH_DATA = 'db/Jira_BD.xlsx'

COLUMNS = [
    'Tipo de Incidencia',               # Eliminar 
    'Clave',                            # Eliminar 
    'Resumen',                          # Patrones     
    'Prioridad',                        # Numerica 
    'Equipo Resolutor',                 # Clasificacion
    'Fecha Real Incidente',             # Numerica (anual, mensual, semanal) 
    'Fecha Resolución Real Incidente',  # Calculo de Duración 
    'Duración Incidente',               # Numerica 
    'Activo de SW',                     # Clasificacion
    'Servicio Reportado',               # Clasificacion
    'Descripción',                      # Patrones
    'Causa Raíz / Origen',              # Patrones
    'Descripción de la Solución:',      # Patrones
    'Resuelto con:'                     # Clasificacion OHE
]

COLUMNS_SELECTED = [
    'Resumen',                          # Resumen     
    'Prioridad',                        # Prioridad
    'Equipo Resolutor',                 # Equipo
    'Fecha Real Incidente',             # Fecha_Inicio
    'Fecha Resolución Real Incidente',  # Fecha_Fin
    'Duración Incidente',               # Duracion
    'Activo de SW',                     # Activo_SW
    'Servicio Reportado',               # Reporte
    'Descripción',                      # Descripcion
    'Causa Raíz / Origen',              # Causa
    'Descripción de la Solución:',      # Solucion
    'Resuelto con:'                     # Resuelto_con
]

COLUMNS_RENAMED = [
    'Resumen',          
    'Priority',
    'Equipo',      
    'Fecha_Inicio', 
    'Fecha_Fin', 
    'Duracion', 
    'Activo_SW',    
    'Reporte',
    'Descripcion',     
    'Causa', 
    'Solucion', 
    'Resuelto_con'
]

def renamed(df):
    df.drop(columns=['Tipo de Incidencia', 'Clave'], inplace=True)
    df.columns = COLUMNS_RENAMED
    return df

def main():
    df = pd.read_excel(PATH_DATA, sheet_name='Base')
    df = renamed(df)
    
    # Calcular la duración entre fechas
    df = data.clean(df, ['Fecha_Inicio', 'Fecha_Fin', 'Activo_SW'], 'Fecha_Inicio')
    df = data.duracion(df, 'Fecha_Inicio', 'Fecha_Fin', 'Duracion')

    # Rellenar columnas vacias
    df['Reporte'] = df['Reporte'].fillna('')
    df['Descripcion'] = df['Descripcion'].fillna('')
    df['Causa'] = df['Causa'].fillna('')
    df['Solucion'] = df['Solucion'].fillna('')
    df['Resuelto_con'] = df['Resuelto_con'].fillna('')

    # Aplicar codificación cíclica a las fechas
    df = data.cyclical_encoding(df, 'Fecha_Inicio')

    # Convertir texto de Priority a numérico
    diccionario = {'Lowest':1, 'Low':2, 'Medium':3, 'High':4, 'Highest':5}    
    df = data.text_to_number(df, 'Priority', diccionario)

    # Aplicar One-Hot Encoding a la columna 'Resuelto_con'
    df = data.OHE(df, 'Resuelto_con')

    # Aplicamos Target Encoding a la columna 'Activo_SW' y 'Reporte'
    df = data.target_encoding(df, ['Activo_SW', 'Reporte', 'Equipo'], 'Duracion')

    # Aplicar tfidf a las columnas de texto
    columnas_texto = ['Resumen', 'Descripcion', 'Causa', 'Solucion']
    df = data.tfidf(df, columnas_texto)

    # Columnas tfidf generadas
    cols_tfidf = [c for c in df.columns if c.startswith('tfidf_')]

    # Guardar el DataFrame limpio en un archivo Excel
    #df.to_excel('db/Jira_BD_Limpio.xlsx', index=False)

    

    # ---------------------------------- Regresión lineal 1 --------------------------------
    print("\n------ Árbol de Regresión 1 ------\n")
    '''
    Primera prueba: 
    - Usando columnas numéricas y categóricas (Target Encoding)
    - Se limita duración entre 10 y 110 horas para evitar outliers
    '''
    df1 = df[df['Duracion'] < 110]
    df1 = df1[df1['Duracion'] > 10]
    
    features = ['Priority',
                'Equipo',
                'Activo_SW', 
                'Reporte', 
                'Fecha_Inicio_Semanal_Sen', 
                'Fecha_Inicio_Semanal_Cos',
                'Fecha_Inicio_Mensual_Sen', 
                'Fecha_Inicio_Mensual_Cos'
    ] 

    x = df1[features] 
    y = df1['Duracion']
    process.xgboost_regression(df1, x, y)
    # -------------------------------- Fin Árbol de Regresión 1 -------------------------------
    # ------------------------- Análisis Causa Raìz y Solución TF-IDF -------------------------
    print("\n------ TF-IDF Causa / Solución ------\n")

    df2 = df[df['Duracion'] < 400]
    umbral = df2['Duracion'].quantile(0.80)
    df2 = df2[df2['Duracion'] >= umbral]
    
    cols_causa = [c for c in df.columns if c.startswith('tfidf_Causa_')]
    causas = df2[cols_causa].sum().sort_values(ascending=False).head(10)

    cols_solucion = [c for c in df.columns if c.startswith('tfidf_Solucion_')]
    soluciones = df2[cols_solucion].sum().sort_values(ascending=False).head(10)

    print("Top causas raíz por TF-IDF en incidentes largos (mayores al percentil 80):")
    print(causas)
    print("\nTop soluciones por TF-IDF en incidentes largos (mayores al percentil 80):")
    print(soluciones)
    # ----------------------- Fin Análisis Causa Raìz y Solución TF-IDF -----------------------

if __name__ == "__main__":
    main()