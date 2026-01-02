import func.temporal as temporal
import func.regresion as regresion
import func.bertopic as bertopic
import func.tf_idf as tfidf
import func.data as data
import streamlit as st
import pandas as pd
import io

FILTROS = [
    'Prioridad',
    'Equipo',
    'Fecha_Inicio',
    'Fecha_Fin',
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

TEMAS = [
    'Temas_Resumen', 
    'Temas_Descripcion', 
    'Temas_Causa', 
    'Temas_Solucion'
    ]

buffer = io.BytesIO()

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
        if columna in ['Fecha_Inicio', 'Fecha_Fin']:
            serie_fecha = pd.to_datetime(df[columna], errors='coerce')
            f_min = serie_fecha.min().to_pydatetime().date()
            f_max = serie_fecha.max().to_pydatetime().date()
            if columna == 'Fecha_Inicio':
                fecha_sel = st.sidebar.date_input("Desde (Fecha Inicio)", value=f_min, min_value=f_min, max_value=f_max)
                df = df[pd.to_datetime(df['Fecha_Inicio']).dt.date >= fecha_sel]
                
            elif columna == 'Fecha_Fin':
                fecha_sel = st.sidebar.date_input("Hasta (Fecha Fin)", value=f_max, min_value=f_min, max_value=f_max)
                df = df[pd.to_datetime(df['Fecha_Fin']).dt.date <= fecha_sel]
        elif(columna == 'Duracion'):
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
    st.sidebar.button("Bot", on_click=cambiar_seccion, args=("Bot",))
    st.sidebar.button("Cargar nuevo archivo", on_click=cambiar_archivo)
    
    df = filtros(st.session_state.df)
    df_temporal = temporal.temporal_app(df.copy())

# ------------------------------------ VISUALIZACIÓN ------------------------------------
    if st.session_state.seccion == "Visualizacion":
        st.title("Visualización de Datos")

        df = df.copy()
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
        df = df.copy()
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

# ---------------------------------------- TEXTO ----------------------------------------
    elif st.session_state.seccion == "Texto":
        st.title("Análisis de Texto")
        col1, col2 = st.columns(2)

        with col1:
            st.write("El TF-IDF es un filtro inteligente que resalta las palabras más 'especiales' de un texto: premia a las palabras que aparecen mucho en un ticket, pero castiga a las que aparecen en todos lados y no dicen nada (como 'el', 'de' o 'problema'). Es una herramienta de conteo de importancia, no de lectura; sirve para saber de qué palabras se habla más, pero no entiende el contexto ni el orden de las ideas, por lo que no sabe distinguir entre 'el sistema falló por el usuario' y 'el usuario falló por el sistema'.")
            if st.button("Análisis con TF-IDF"):
                cambiar_seccion("Texto/TFIDF")
                st.rerun()
        with col2:
            if st.button("Análisis con BERTopic"):
                cambiar_seccion("Texto/BERTopic")
                st.rerun()
    
# ---------------------------------------- TF-IDF ----------------------------------------
    elif st.session_state.seccion == "Texto/TFIDF":
        st.title("Análisis de Texto con TF-IDF")
        
        columnas = ['Resumen', 'Descripcion', 'Causa', 'Solucion']
        df_tfidf = df[columnas].copy()

        df_tfidf = tfidf.tfidf_app(df_tfidf, columnas)
        
        cols_causa = [c for c in df_tfidf.columns if c.startswith('tfidf_Causa_')]
        causas = df_tfidf[cols_causa].sum().sort_values(ascending=False).head(10)

        cols_solucion = [c for c in df_tfidf.columns if c.startswith('tfidf_Solucion_')]
        soluciones = df_tfidf[cols_solucion].sum().sort_values(ascending=False).head(10)

        cols_resumen = [c for c in df_tfidf.columns if c.startswith('tfidf_Resumen_')]
        resumen = df_tfidf[cols_resumen].sum().sort_values(ascending=False).head(10)

        cols_descripcion = [c for c in df_tfidf.columns if c.startswith('tfidf_Descripcion_')]
        descripcion = df_tfidf[cols_descripcion].sum().sort_values(ascending=False).head(10)

        st.subheader("Top 10 Palabras en Causa Raíz")
        st.dataframe(causas, width='stretch')
        st.subheader("Top 10 Palabras en Solución")
        st.dataframe(soluciones, width='stretch')
        st.subheader("Top 10 Palabras en Resumen")
        st.dataframe(resumen, width='stretch')
        st.subheader("Top 10 Palabras en Descripción")
        st.dataframe(descripcion, width='stretch')

# --------------------------------------- BERTopic ---------------------------------------
    elif st.session_state.seccion == "Texto/BERTopic":
        st.title("Análisis de Texto con BERTopic")

        if st.button("Ejecutar Procesamiento BERTopic"):

            with st.spinner("Limpiando texto y generando tópicos, esto puede tardar varios minutos..."):
                columnas = ['Resumen', 'Descripcion', 'Causa', 'Solucion']
                df_bert = bertopic.bertopic_app(df.copy(), columnas)
                st.session_state.df = df_bert
                st.rerun()
        
        if all(col in st.session_state.df.columns for col in TEMAS):
            st.success("Temas generados correctamente.")
            st.dataframe(st.session_state.df, width='stretch') 
            col1, col2 = st.columns(2)
            
            with col1:
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    st.session_state.df.to_excel(writer, index=False, sheet_name='Datos')
                st.download_button(
                    label="Descargar Excel",
                    data=buffer.getvalue(),
                    file_name="Temas.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            with col2:
                if st.button("Usar este DataFrame para el análisis"):
                    st.session_state.df = df_bert
                    df = df_bert
                    cambiar_seccion("Visualizacion")
                    st.rerun()
        else:
            st.info("Presiona el botón para ejecutar el procesamiento de BERTopic y generar los temas.")

# ------------------------------------------ Bot ------------------------------------------ 
    elif st.session_state.seccion == "Bot":
        st.title("Análisis de Texto con BERTopic")
       