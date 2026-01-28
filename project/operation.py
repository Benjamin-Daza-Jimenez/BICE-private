import func.ficha_operation as ficha
import func.causa_solucion as c_s
import func.bertopic as bertopic
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
    'Fecha_Inicio',
    'Fecha_Fin',
    'Duracion',
]

COLUMNS_SELECTED = [         
    'Prioridad',
    'Equipo',      
    'Fecha_Inicio', 
    'Fecha_Fin', 
    'Duracion', 
    'Activo_SW',    
    'Reporte',
    'Descripcion',
    'Temas_Descripcion',  
    'Causa',
    'Temas_Causa',
    'Solucion',
    'Temas_Solucion',
    'Resumen',
    'Temas_Resumen'
]

TEMAS = [
    'Temas_Resumen', 
    'Temas_Descripcion', 
    'Temas_Causa', 
    'Temas_Solucion'
    ]

def cambiar_seccion(nombre):
    st.session_state.seccion_op = nombre
    st.session_state.items_visibles = 10

# ------------------------------------ FILTROS DINÁMICOS -----------------------------------
def filtros(df):
    st.sidebar.header("Filtros Activos")
    filtros_a_usar = st.sidebar.multiselect("¿Qué columnas deseas filtrar?", FILTROS)
    for columna in filtros_a_usar: 
        if columna in ['Fecha_Inicio', 'Fecha_Fin']:
            serie_fecha = pd.to_datetime(df[columna], errors='coerce')
            f_min = serie_fecha.min().to_pydatetime().date()
            f_max = serie_fecha.max().to_pydatetime().date()

            max_calendar = date(f_max.year, 12, 31)
            min_calendar = date(f_min.year, 1, 1)

            if columna == 'Fecha_Inicio':
                fecha_sel = st.sidebar.date_input("Desde (Fecha Inicio)", value=f_min, min_value=min_calendar, max_value=max_calendar)
                df = df[pd.to_datetime(df['Fecha_Inicio']).dt.date >= fecha_sel]
                
            elif columna == 'Fecha_Fin':
                fecha_sel = st.sidebar.date_input("Hasta (Fecha Fin)", value=f_max, min_value=min_calendar, max_value=max_calendar)
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

# X----------------------------------- INTERFAZ PRINCIPAL ---------------------------------X

# ------------------------------------- BARRA LATERAL -------------------------------------- 
def operation_app(df_original):
    st.set_page_config(page_title="Analizador Operacional", layout="wide")

    st.sidebar.title("Navegación")
    st.sidebar.button("Ver Tablas de Datos", on_click=cambiar_seccion, args=("Visualizacion",))
    st.sidebar.button("Análisis con Activo de Software", on_click=cambiar_seccion, args=("Activo_SW",))
    st.sidebar.button("Análisis con Servicio Reportado", on_click=cambiar_seccion, args=("Reporte",))
    st.sidebar.button("Volver al menú principal", on_click=cambiar_seccion, args=("Actualizar",))
    
    df = filtros(df_original[COLUMNS_SELECTED].copy())

# ------------------------------------ VISUALIZACIÓN --------------------------------------
    if st.session_state.seccion_op == "Visualizacion":
        df = df.copy()

        st.title("📊 Panel de Visualización y Exportación")
        st.markdown("Consulta y descarga los datos procesados para el análisis.")

        st.subheader("Base de Datos Maestra (Jira) | Cantidad total de registros: " + str(len(df)))
        st.dataframe(df, width='stretch', hide_index=True)

        c1, c2, _ = st.columns([1, 1, 2])

        with c1:
            buffer = io.BytesIO()
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

# -------------------------------------- ACTIVO SW ---------------------------------------
    elif st.session_state.seccion_op == "Activo_SW":
        st.subheader("Análisis de Activo de Software")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Ficha Histórica**\n\nVisualice el comportamiento los Activos de Software, a través de su Promedio de tickets mensual, Equipo más frecuente, Causa raíz y más.")
            if st.button("Ver Ficha", use_container_width=True):
                cambiar_seccion("Activo_SW/Ficha")
                st.rerun()
        
        with col2:
            st.info("**Causa y Solución**\n\nTarjetas que muestran las causas raíz y soluciones aplicadas por activo de software y palabras claves en la descripción.")
            if st.button("Ver Causa y Solución", use_container_width=True):
                cambiar_seccion("Activo_SW/Pred")
                st.rerun()
        st.write("")

# ---------------------------------- ACTIVO SW / FICHA ---------------------------------------
    elif st.session_state.seccion_op == "Activo_SW/Ficha":
        st.markdown("## 🏥 Ficha Técnica Unificada")
        st.caption("Resumen estratégico para toma de decisiones rápida.")
        df = df.copy()
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        st.markdown(f"La información a continuación es en base a {len(df)} registros (tickets), de los cuales {len(df[~mask_procesados])} no fueron categorizados, iniciados entre {df['Fecha_Inicio'].min().date().strftime('%d-%m-%Y')} y {df['Fecha_Inicio'].max().date().strftime('%d-%m-%Y')}.", help="Los tickets no categorizados son aquellos que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
        ficha.ficha_tecnica(df, 'Activo_SW')

# ---------------------------------- ACTIVO SW / PRED ---------------------------------------
    elif st.session_state.seccion_op == "Activo_SW/Pred":
        df = df.copy()
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        df = df[mask_procesados].copy()

        st.title("Causa y Solución por Activo de Software")
        st.markdown(f"La información a continuación es en base a {len(df)} registros (tickets), iniciados entre {df['Fecha_Inicio'].min().date().strftime('%d-%m-%Y')} y {df['Fecha_Inicio'].max().date().strftime('%d-%m-%Y')}.")

        opcion = st.selectbox("Seleccione el Activo de Software para el Análisis", df['Activo_SW'].unique(), index=None, placeholder="Seleccione un Activo de Software")
        if opcion:
            df = df[df['Activo_SW'] == opcion]
            c_s.causa_solucion(df)
            
# --------------------------------------- REPORTE ----------------------------------------
    elif st.session_state.seccion_op == "Reporte":
        st.subheader("Análisis de Servicio Reportado")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**Ficha Histórica**\n\nVisualice el comportamiento los Servicios Reportados, a través de su Promedio de tickets mensual, Equipo más frecuente, Causa raíz y más.")
            if st.button("Ver Ficha", use_container_width=True):
                cambiar_seccion("Reporte/Ficha")
                st.rerun()
        
        with col2:
            st.info("**Causa y Solución**\n\nTarjetas que muestran las causas raíz y soluciones aplicadas por servicio reportado y palabras claves en la descripción.")
            if st.button("Ver Causa y Solución", use_container_width=True):
                cambiar_seccion("Reporte/Pred")
                st.rerun()
        st.write("")

# ---------------------------------- REPORTE / FICHA ---------------------------------------
    elif st.session_state.seccion_op == "Reporte/Ficha":
        st.markdown("## 🏥 Ficha Técnica Unificada")
        st.caption("Resumen estratégico para toma de decisiones rápida.")
        df = df.copy()
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        st.markdown(f"La información a continuación es en base a {len(df)} registros (tickets), de los cuales {len(df[~mask_procesados])} no fueron categorizados, iniciados entre {df['Fecha_Inicio'].min().date().strftime('%d-%m-%Y')} y {df['Fecha_Inicio'].max().date().strftime('%d-%m-%Y')}.", help="Los tickets no categorizados son aquellos que no cuentan con temas asignados en alguna de las siguientes columnas: Resumen, Descripción, Causa, Solución.")
        ficha.ficha_tecnica(df, 'Reporte')

# ---------------------------------- REPORTE / PRED ---------------------------------------
    elif st.session_state.seccion_op == "Reporte/Pred":
        df = df.copy()
        mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
        df = df[mask_procesados].copy()

        st.title("Causa y Solución por Servicio Reportado")
        st.markdown(f"La información a continuación es en base a {len(df)} registros (tickets), iniciados entre {df['Fecha_Inicio'].min().date().strftime('%d-%m-%Y')} y {df['Fecha_Inicio'].max().date().strftime('%d-%m-%Y')}.")
        opcion = st.selectbox("Seleccione el Servicio Reportado para el Análisis", df['Reporte'].unique(), index=None, placeholder="Seleccione un Servicio Reportado")
        if opcion:
            df = df[df['Reporte'] == opcion]
        
            c_s.causa_solucion(df)

# ----------------------------------- ACTUALIZAR DATOS -----------------------------------
    elif st.session_state.seccion_op == "Actualizar":
        st.session_state.seccion_op = "Visualizacion"
        st.session_state.seccion = "Eleccion"
        st.rerun()
        