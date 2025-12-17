import pandas as pd
from functions.patrones_texto import extraer_patrones_texto

RUTA_DATA = 'DB/Incidentes_Separado.xlsx'

def main():
    # Cargar datos desde el archivo Excel
    df_general = pd.read_excel(RUTA_DATA, sheet_name='Sheet1')
    df_general = df_general.dropna(subset=['Descripción de la Solución:'])

    # ----- ADECUAR KEYWORDS A La LÓGICA DEL NEGOCIO -----
    keywords = ['carga', 'cliente', 'error', 'pago', 'sistema', 'ticket', 'usuario']

    patrones = extraer_patrones_texto(df_general, 'Descripción de la Solución:', keywords)

if __name__ == "__main__":
    main()