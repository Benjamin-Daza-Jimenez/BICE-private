import temporal_analysis.temporal as temporal
import regresion_analysis.regresion as regresion
import BERTopic_analysis.bertopic as bertopic
import func.data as data
import streamlit as st
import pandas as pd

FILTROS = [
    'Prioridad',
    'Equipo',
    'Duracion',
    'Activo_SW',
    'Reporte',
    'Resuelto_con'
]

REGRESION = [
    'Prioridad',
    'Equipo',
    'Fecha_Inicio_Semanal',
    'Fecha_Inicio_Mensual',
    'Fecha_Inicio_Anual',
    'Duracion',
    'Activo_SW',
    'Reporte',
    'Resuelto_con'
]

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
    'Prioridad',
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

st.set_page_config(page_title="Analizador ML Local", layout="wide")

# Inicialización de estado
if 'df' not in st.session_state:
    st.session_state.df = None
if 'seccion' not in st.session_state:
    st.session_state.seccion = "Visualizacion"

def cambiar_seccion(nombre):
    st.session_state.seccion = nombre
 
def cambiar_archivo():
    st.session_state.df = None
    st.session_state.seccion = "Visualizacion"

# --------------------------------- FILTROS DINÁMICOS ---------------------------------
def filtros(df):
    st.sidebar.header("Filtros Activos")
    filtros_a_usar = st.sidebar.multiselect("¿Qué columnas deseas filtrar?", FILTROS)
    for columna in filtros_a_usar:

        if(columna == 'Duracion'):
            min = int(df[columna].min())
            max = int(df[columna].max())

            c1, c2 = st.sidebar.columns(2)
            with c1:
                val_min = st.number_input("Mínimo", min_value=min, max_value=max, value=min)
            with c2:
                val_max = st.number_input("Máximo", min_value=min, max_value=max, value=max)
            
            rango = st.sidebar.slider(f"Ajuste visual {'Duracion'}", min, max, (val_min, val_max))
            
            df = df[(df[columna] >= rango[0]) & (df[columna] <= rango[1])]
        else:
            opciones = st.sidebar.multiselect(f"Selecciona valores para {columna}", df[columna].unique())
            df = df[df[columna].isin(opciones)]
    return df

# -------------------------------------- INTERFAZ PRINCIPAL ---------------------------------------

# -------------------------------------- CARGA -------------------------------------
if st.session_state.df is None:
    st.title("Bienvenido - Carga tu información")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.write("### Requisitos del archivo Excel")
        st.write("Para que el análisis funcione correctamente, tu archivo Excel debe contener una hoja llamada **'Base'** con las siguientes columnas:")
        for col in COLUMNS:
            st.markdown(f"- **{col}**")
    with col2:
        st.write("### Carga tu archivo Excel")
        uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

        if uploaded_file:
            df = pd.read_excel(uploaded_file, sheet_name='Base')
            missing_cols = [col for col in COLUMNS if col not in df.columns]
            if missing_cols:
                st.error(f"El archivo cargado no contiene las siguientes columnas requeridas: {', '.join(missing_cols)}")
            else:
                df = df[COLUMNS_SELECTED]
                df.columns = COLUMNS_RENAMED
                df = df[df['Fecha_Fin'] >= df['Fecha_Inicio']]
                df = data.duracion(df, 'Fecha_Inicio', 'Fecha_Fin', 'Duracion')
                st.session_state.df = df
                
                st.success("Archivo cargado correctamente. ¡Puedes comenzar el análisis!")
                
                st.rerun()

# ------------------------------------ BARRA LATERAL ------------------------------------
else:
    st.sidebar.title("Navegación") 
    st.sidebar.button("Visualización de Datos", on_click=cambiar_seccion, args=("Visualizacion",))
    st.sidebar.button("Análisis Temporal", on_click=cambiar_seccion, args=("Temporal",))
    st.sidebar.button("Análisis de Regresión", on_click=cambiar_seccion, args=("Regresion",))
    st.sidebar.button("Análisis de Texto", on_click=cambiar_seccion, args=("Texto",))
    st.sidebar.button("Cargar nuevo archivo", on_click=cambiar_archivo)
    
    df = filtros(st.session_state.df)
    df_temporal = temporal.temporal_app(df)

# ------------------------------------ VISUALIZACIÓN ------------------------------------
    if st.session_state.seccion == "Visualizacion":
        st.title("Visualización de Datos")

        st.subheader(f"Datos Filtrados: {len(df)} registros")
        st.dataframe(df, width='stretch')

        col1, col2 = st.columns(2)
    
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Excel Filtrado", data=csv, file_name="Filtrado.xlsx")
        with col2:
            if st.button("Cargar nuevo archivo"):
                cambiar_seccion(None)
                st.rerun()

# -------------------------------------- TEMPORAL --------------------------------------
    elif st.session_state.seccion == "Temporal":
        st.title("Análisis Temporal")

        st.subheader(f"Datos Temporales Procesados: {len(df_temporal)} registros")
        st.dataframe(df_temporal, width='stretch')

        col1, col2, col3 = st.columns(3)

        with col1:
            csv = df_temporal.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Datos Temporales", data=csv, file_name="Temporal.csv")
        with col2:
            if st.button("Análisis Anual"):
                cambiar_seccion("Temporal/Anual")
                st.rerun()
        with col3:
            if st.button("Análisis Mensual"):
                cambiar_seccion("Temporal/Mensual")
                st.rerun()

# ------------------------------------ TEMPORAL/ANUAL ------------------------------------
    elif st.session_state.seccion == "Temporal/Anual":
        st.title("Análisis Anual")
        rutas_anual = temporal.anual(df_temporal)
        for ruta in rutas_anual:
            st.image(ruta)
            with open(ruta, "rb") as file:
                st.download_button(
                    label=f"Descargar Gráfico {ruta.split('_')[-1]}",
                    data=file,
                    file_name=ruta.split('/')[-1],
                    mime="image/png"
                )

# ----------------------------------- TEMPORAL/MENSUAL -----------------------------------
    elif st.session_state.seccion == "Temporal/Mensual":
        st.title("Análisis Mensual")
        rutas_anual = temporal.mensual(df_temporal)
        for ruta in rutas_anual:
            st.image(ruta)
            with open(ruta, "rb") as file:
                st.download_button(
                    label=f"Descargar Gráfico {ruta.split('_')[-1]}",
                    data=file,
                    file_name=ruta.split('/')[-1],
                    mime="image/png"
                ) 
        
# -------------------------------------- REGRESIÓN ---------------------------------------
    elif st.session_state.seccion == "Regresion":
        st.title("Modelo de Regresión")

        if df.empty:
            st.warning("⚠️ El dataset está vacío. Ajusta los filtros laterales para obtener datos.")
        else:
            df_pool = regresion.regresion_data(df)

            col1, col2 = st.columns(2)

            with col1:
                objetivo = st.selectbox(
                "Selecciona variable objetivo (Y):", 
                options=REGRESION,
                index=REGRESION.index('Duracion') if 'Duracion' in REGRESION else 0,
                help="La variable objetivo es la que el modelo intentará predecir basándose en las variables predictoras seleccionadas."
            )
                
            with col2:
                opciones_predictoras = [c for c in REGRESION if c != objetivo]
                predictoras_sel = st.multiselect(
                    "Selecciona variables predictoras (X):", 
                    options=opciones_predictoras,
                    help="Las variables predictoras son las que el modelo utilizará para hacer predicciones sobre la variable objetivo."
                )

            if predictoras_sel and objetivo:
                cols_x = []
                for col in predictoras_sel:
                    if col in ['Fecha_Inicio_Semanal', 'Fecha_Inicio_Mensual', 'Fecha_Inicio_Anual']:
                        componentes = [c for c in df_pool.columns if c.startswith(col) and (c.endswith('_Sen') or c.endswith('_Cos'))]
                        cols_x.extend(componentes)
                    elif col == 'Resuelto_con':
                        categorias_ohe = [c for c in df_pool.columns if c.startswith('Resuelto_con_')]
                        cols_x.extend(categorias_ohe)
                    else:
                        if col in df_pool.columns:
                            cols_x.append(col)
                
                col_y = [c for c in df_pool.columns if c == objetivo][0]

                df_modelo = df_pool[cols_x + [col_y]].copy()
                df_modelo = df_modelo.dropna()

                x = df_modelo[cols_x]
                y = df_modelo[col_y]
                
                mse, r2, importancias = regresion.tree_regression(x, y)

                st.subheader(f"Datos de Regresión Procesados: {len(df_modelo)} registros")
                st.dataframe(df_modelo, width='stretch')

                st.subheader("Resultados del Modelo de Regresión")
                st.markdown(f"- **Mean Squared Error (MSE):** {mse:.4f}",
                            help="Representa qué tan lejos están las predicciones de la realidad. "
                                    "Al estar al cuadrado, castiga con más fuerza las predicciones que fallaron por mucho tiempo. "
                                    "¡Mientras más bajo sea este número, mejor!")
                st.markdown(f"- **Coeficiente de Determinación (R²):** {r2*100:.4f}%",
                            help="Este porcentaje indica cuánto entiende el modelo el comportamiento de los incidentes. "
                                    "Un 100% sería una predicción perfecta, mientras que un 0% sería lo mismo que adivinar al azar.")
                st.subheader("Importancia de las Variables")
                st.dataframe(importancias, width='stretch')

# --------------------------------------- BERTOPIC ---------------------------------------
    elif st.session_state.seccion == "Texto":
        st.title("Análisis de Texto con BERTopic")