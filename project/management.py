import func.regresion as regresion
import func.temporal as temporal
import func.bertopic as bertopic
import func.volume as volume
import func.tf_idf as tfidf
import streamlit as st
import pandas as pd
import sys
import io

if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    sys.path.append(bundle_dir)

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

def cambiar_seccion(nombre):
    st.session_state.seccion_ma = nombre

# ----------------------------------- FILTROS DINÁMICOS -----------------------------------
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

# X---------------------------------- INTERFAZ PRINCIPAL ----------------------------------X

# ------------------------------------- BARRA LATERAL -------------------------------------- 
def management_app(df_original):
    st.set_page_config(page_title="Analizador de Gestión", layout="wide")

    st.sidebar.title("Navegación") 
    st.sidebar.button("Ver Tablas de Datos", on_click=cambiar_seccion, args=("Visualizacion",))
    st.sidebar.button("Análisis y Generación de Gráficos", on_click=cambiar_seccion, args=("Graficos",))
    st.sidebar.button("Análisis de Regresión", on_click=cambiar_seccion, args=("Regresion",))
    st.sidebar.button("Volver al menú principal", on_click=cambiar_seccion, args=("Actualizar",))
    
    df = filtros(df_original.copy())
    df_temporal = temporal.temporal_app(df.copy()) 

# ------------------------------------ VISUALIZACIÓN -------------------------------------
    if st.session_state.seccion_ma == "Visualizacion":
        df = df.copy()

        st.title("📊 Panel de Visualización y Exportación")
        st.markdown("Consulta y descarga los datos procesados para el análisis.")

        st.subheader("Base de Datos Maestra (Jira) | Cantidad total de registros: " + str(len(df)))
        st.dataframe(df, width='stretch', hide_index=True)

        c1, c2, _ = st.columns([1, 1, 2])

        with c1:
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Base')
            st.download_button(
                label="Descargar Excel",
                data=buffer.getvalue(),
                file_name="Jira_BD.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )
        with c2:
            zip_data = bertopic.Json_Zip(df.copy(), 'Fecha_Inicio')
            st.download_button(
                label="Descargar JSONs por Mes",
                data=zip_data,
                file_name="Temas_Jsons.zip",
                mime="application/zip",
                width='stretch'
            )

# -------------------------------------- GRÁFICOS ----------------------------------------
    elif st.session_state.seccion_ma == "Graficos":
        st.title("📊 Centro de Inteligencia y Análisis")
        st.markdown("""
            Bienvenido al panel de visualización. Seleccione la dimensión de análisis que desea explorar 
            para obtener insights detallados sobre la operación.
        """)
        st.write("---")

        # --- SECCIÓN 1: ANÁLISIS TEMPORAL ---
        st.subheader("🕒 Análisis de Tendencias Temporales")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Evolución Histórica**\n\nVisualice el comportamiento de los tickets a lo largo de los años a través de gráficos de barras.")
            if st.button("Ver Gráfico Anual", use_container_width=True):
                cambiar_seccion("Temporal/Anual")
                st.rerun()
        
        with col2:
            st.info("**Intensidad Operativa**\n\nMapa de calor detallado por día y mes para detectar picos de carga.")
            if st.button("Ver Mapa de Calor Mensual", use_container_width=True):
                cambiar_seccion("Temporal/Mensual")
                st.rerun()
        st.write("")

        # --- SECCIÓN 2: ANÁLISIS DE TEXTO (IA) ---
        st.subheader("🏷️ Inteligencia de Texto y Tópicos")
        col3, col4 = st.columns(2)
        with col3:
            st.success("**Relevancia de Palabras**\n\nIdentifique las palabras clave más significativas en las columnas descriptivas.")
            if st.button("Ver Análisis de Palabras", use_container_width=True):
                cambiar_seccion("Texto/TFIDF")
                st.rerun()

        with col4:
            st.success("**Agrupación por Temas**\n\nCategorización automática de incidentes mediante modelos de IA, visualizado en un gráfico de Paretto.")
            if st.button("Ver Gráfico de Pareto", use_container_width=True):
                cambiar_seccion("Texto/BERTopic")
                st.rerun()
        st.write("")

        # --- SECCIÓN 3: VOLUMEN ---
        st.subheader("⚖️ Métricas de Volumen")
        col5, col6 = st.columns(2)
        
        with col5:
            st.warning("**Concentración de Carga**\n\nAnálisis de distribución de volumen de tickets según su actividad diaria mediante gráfico de Campana de Gauss.")
            if st.button("Ver Gráfico de Campana", use_container_width=True):
                cambiar_seccion("Volumen/General") 
                st.rerun()
        
        with col6:
            # Espacio para futuro gráfico o una métrica rápida
            st.write("")

# ------------------------------------ TEMPORAL/ANUAL ------------------------------------
    elif st.session_state.seccion_ma == "Temporal/Anual":
        st.title("Análisis Anual")
        df_temporal = df_temporal.copy()
        temporal.anual_plotly(df_temporal)

# ----------------------------------- TEMPORAL/MENSUAL -----------------------------------
    elif st.session_state.seccion_ma == "Temporal/Mensual":
        st.title("Análisis Mensual")
        df_temporal = df_temporal.copy()
        temporal.mensual_plotly(df_temporal)
        
# -------------------------------------- REGRESIÓN ---------------------------------------
    elif st.session_state.seccion_ma == "Regresion":
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

# ---------------------------------------- TF-IDF ----------------------------------------
    elif st.session_state.seccion_ma == "Texto/TFIDF":
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
    elif st.session_state.seccion_ma == "Texto/BERTopic":
        st.title("Análisis de Temas para columnas de Texto")
        df = df.copy()
        bertopic.bertopic_graph_plotly(df)

# ----------------------------------- Actualizar Datos -----------------------------------
    elif st.session_state.seccion_ma == "Actualizar":
        st.session_state.seccion_ma = "Visualizacion"
        st.session_state.seccion = "Eleccion"
        st.rerun()
     
# ----------------------------------- Campana de Gauss -----------------------------------
    elif st.session_state.seccion_ma == "Volumen/General":
        st.title("Análisis de Volumen de Incidentes")
        df = df.copy()
        volume.grafico_gauss(df)
        