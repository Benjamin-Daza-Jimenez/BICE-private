import func.regresion as regresion
import func.temporal as temporal
import func.bertopic as bertopic
import func.volume as volume
from datetime import date
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
    'Desde (Fecha Inicio)',
    'Hasta (Fecha Inicio)',
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
        if columna in ['Desde (Fecha Inicio)', 'Hasta (Fecha Inicio)']:
            serie_fecha = pd.to_datetime(df["Fecha_Inicio"], errors='coerce')
            f_min = serie_fecha.min().to_pydatetime().date()
            f_max = serie_fecha.max().to_pydatetime().date()

            max_calendar = date(f_max.year, 12, 31)
            min_calendar = date(f_min.year, 1, 1)

            if columna == 'Desde (Fecha Inicio)':
                fecha_sel = st.sidebar.date_input("Desde (Fecha Inicio)", value=f_min, min_value=min_calendar, max_value=max_calendar, format = "DD-MM-YYYY")
                df = df[pd.to_datetime(df['Fecha_Inicio']).dt.date >= fecha_sel]
                print(fecha_sel)
                
            elif columna == 'Hasta (Fecha Inicio)':
                fecha_sel = st.sidebar.date_input("Hasta (Fecha Inicio)", value=f_max, min_value=min_calendar, max_value=max_calendar, format = "DD-MM-YYYY")
                df = df[pd.to_datetime(df['Fecha_Inicio']).dt.date <= fecha_sel]
                print(fecha_sel)
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
    st.sidebar.button("Generación de Gráficos", on_click=cambiar_seccion, args=("Graficos",))
    st.sidebar.button("Volver al menú principal", on_click=cambiar_seccion, args=("Actualizar",))
    
    df = filtros(df_original.copy())
    df_temporal = temporal.temporal_app(df) 

# ------------------------------------ VISUALIZACIÓN -------------------------------------
    if st.session_state.seccion_ma == "Visualizacion":
        df = df.copy()

        st.title("📊 Panel de Visualización y Exportación")
        st.write("---")

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
        st.write("---")

        # --- SECCIÓN 1: ANÁLISIS TEMPORAL ---
        st.subheader("🕒 Análisis de Tendencias Temporales")
        col1, col2 = st.columns(2)
        with col1:
            st.warning("**Evolución Histórica**\n\nVisualice la relación entre el volumen mensual de tickets y su tiempo promedio de atención para identificar tendencias de eficiencia.")
            if st.button("Ver Gráfico de Barra Anual", use_container_width=True):
                cambiar_seccion("Temporal/Anual")
                st.rerun()
        
        with col2:
            st.warning("**Intensidad Operativa**\n\nAnalice la carga de trabajo desde una escala mensual a una diaria para detectar patrones semanales, picos críticos o intermitencias.")
            if st.button("Ver Mapa de Calor Mensual", use_container_width=True):
                cambiar_seccion("Temporal/Mensual")
                st.rerun()
        st.write("")

        # --- SECCIÓN 2: ANÁLISIS DE TEXTO (IA) ---
        st.subheader("⚖️ Métricas de Volumen y Tópicos")
        col3, col4 = st.columns(2)
        with col3:
            st.success("**Concentración de Carga**\n\nVisualice la distribución del volumen diario mediante una Campana de Gauss para identificar patrones de tickets rutinarios, de alto esfuerzo o críticos.")
            if st.button("Ver Gráfico de Campana", use_container_width=True):
                cambiar_seccion("Volumen/General") 
                st.rerun()

        with col4:
            st.success("**Agrupación por Temas**\n\nAnalice mediante un gráfico de Pareto los temas categorizados por IA, evidenciando el 80% de los conceptos que concentran la narrativa de toda la operación.")
            if st.button("Ver Gráfico de Pareto", use_container_width=True):
                cambiar_seccion("Texto/BERTopic")
                st.rerun()
        st.write("")

# ------------------------------------ TEMPORAL/ANUAL ------------------------------------
    elif st.session_state.seccion_ma == "Temporal/Anual":
        df_temporal = df_temporal.copy()
        st.title("Análisis Anual")
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    st.metric("Registros Base", len(df), help="Cantidad total de tickets en la base de datos luego de aplicar los filtros seleccionados.")
            with col2:
                with st.container(border=True):
                    st.metric("Tickets No Categorizados", len(df[~mask_procesados]), help="Tickets que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
            with col3:
                with st.container(border=True):
                    st.metric("Fecha Inicial Mínima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').min().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más antiguo en la base de datos luego de aplicar los filtros seleccionados.")
            with col4:
                with st.container(border=True):
                    st.metric("Fecha Inicial Máxima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').max().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más reciente en la base de datos luego de aplicar los filtros seleccionados.")
        except:
            st.markdown(f"Filtrando...")    
        temporal.anual_plotly(df_temporal)

# ----------------------------------- TEMPORAL/MENSUAL -----------------------------------
    elif st.session_state.seccion_ma == "Temporal/Mensual":
        df_temporal = df_temporal.copy()
        st.title("Análisis Mensual")
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    st.metric("Registros Base", len(df), help="Cantidad total de tickets en la base de datos luego de aplicar los filtros seleccionados.")
            with col2:
                with st.container(border=True):
                    st.metric("Tickets No Categorizados", len(df[~mask_procesados]), help="Tickets que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
            with col3:
                with st.container(border=True):
                    st.metric("Fecha Inicial Mínima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').min().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más antiguo en la base de datos luego de aplicar los filtros seleccionados.")
            with col4:
                with st.container(border=True):
                    st.metric("Fecha Inicial Máxima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').max().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más reciente en la base de datos luego de aplicar los filtros seleccionados.")
        except:
            st.markdown(f"Filtrando...")   
        temporal.mensual_plotly(df_temporal)
        
# --------------------------------------- BERTopic ---------------------------------------
    elif st.session_state.seccion_ma == "Texto/BERTopic":
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        df = df[mask_procesados].copy()
        st.title("Análisis de Temas para columnas de Texto")
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    st.metric("Registros Base", len(df), help="Cantidad total de tickets en la base de datos luego de aplicar los filtros seleccionados.")
            with col2:
                with st.container(border=True):
                    st.metric("Tickets No Categorizados", len(df[~mask_procesados]), help="Tickets que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
            with col3:
                with st.container(border=True):
                    st.metric("Fecha Inicial Mínima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').min().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más antiguo en la base de datos luego de aplicar los filtros seleccionados.")
            with col4:
                with st.container(border=True):
                    st.metric("Fecha Inicial Máxima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').max().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más reciente en la base de datos luego de aplicar los filtros seleccionados.")
        except:
            st.markdown(f"Filtrando...")
        bertopic.bertopic_graph_plotly(df)

# ----------------------------------- Actualizar Datos -----------------------------------
    elif st.session_state.seccion_ma == "Actualizar":
        st.session_state.seccion_ma = "Visualizacion"
        st.session_state.seccion = "Eleccion"
        st.rerun()
     
# ----------------------------------- Campana de Gauss -----------------------------------
    elif st.session_state.seccion_ma == "Volumen/General":
        df = df.copy()
        

        st.title("Análisis de Volumen de Incidentes")
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container(border=True):
                    st.metric("Registros Base", len(df), help="Cantidad total de tickets en la base de datos luego de aplicar los filtros seleccionados.")
            with col2:
                with st.container(border=True):
                    st.metric("Tickets No Categorizados", len(df[~mask_procesados]), help="Tickets que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
            with col3:
                with st.container(border=True):
                    st.metric("Fecha Inicial Mínima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').min().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más antiguo en la base de datos luego de aplicar los filtros seleccionados.")
            with col4:
                with st.container(border=True):
                    st.metric("Fecha Inicial Máxima", pd.to_datetime(df['Fecha_Inicio'], errors='coerce').max().date().strftime('%d-%m-%Y'), help="Fecha de inicio del ticket más reciente en la base de datos luego de aplicar los filtros seleccionados.")
        except:
            st.markdown(f"Filtrando...")
        volume.grafico_gauss(df)
        