import func.bertopic as bertopic
from datetime import datetime
import func.data as data
import func.jira as jira
import streamlit as st
import pandas as pd
import management
import operation
import glob
import sys
import io
import os

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

st.set_page_config(page_title="Selector de Proceso", layout="wide")

# Inicialización de estado
if 'df' not in st.session_state:
    st.session_state.df = None
    st.session_state.automatico = True
if 'seccion' not in st.session_state:
    st.session_state.seccion = "Eleccion"
if 'seccion_ma' not in st.session_state:
    st.session_state.seccion_ma = "Visualizacion"
if 'seccion_op' not in st.session_state:
    st.session_state.seccion_op = "Visualizacion"

def cambiar_seccion(nombre):
    st.session_state.seccion = nombre

def get_local_file():
    archivos = glob.glob("data/Jira_*.xlsx")
    if not archivos:
        return None, None
    archivo_reciente = max(archivos, key=os.path.getctime)
    try:
        nombre_base = os.path.basename(archivo_reciente)
        fecha_str = nombre_base.replace("Jira_", "").replace(".xlsx", "")
        fecha_archivo = datetime.strptime(fecha_str, "%Y-%m-%d")
        return archivo_reciente, fecha_archivo
    except:
        return None, None


# X----------------------------------- INTERFAZ PRINCIPAL ---------------------------------X

# ------------------------------------------ CARGA -----------------------------------------
if st.session_state.df is None:
    st.title("Bienvenido a BICE Insight")
    st.write("A continuación, cargaremos los datos desde Jira o desde un archivo local si está disponible y es reciente.")
    
    if st.session_state.automatico:
        try:
            ruta_local, fecha_file = get_local_file()
            es_antiguo = (datetime.now() - fecha_file).days > 7 if fecha_file else True

            if es_antiguo:
                with st.status("Descargando desde Jira...", expanded=True) as status:
                    df = jira.jira_get()
                    necesita_transformacion = True
                    status.update(label="Descarga completada.", state="complete", expanded=False)
            else:
                with st.spinner("Cargando base de datos local..."):
                    df = pd.read_excel(ruta_local, sheet_name='Base')
                necesita_transformacion = not any(col in df.columns for col in TEMAS)

        except Exception as e:
            st.error(f"Error al cargar archivo local: {e}")
            st.info("Por favor, cargue el archivo manualmente para continuar con el análisis.")
            archivo_subido = st.file_uploader("Sube tu archivo Excel de Jira", type=['xlsx'])
            if archivo_subido is not None:
                with st.spinner("Procesando archivo subido..."):
                    df = pd.read_excel(archivo_subido, sheet_name='Base')
                    necesita_transformacion = not any(col in df.columns for col in TEMAS)
                    st.success("Archivo cargado con éxito.")
                    st.session_state.automatico = True
            else:
                st.info("Por favor, sube un archivo para continuar.")
                st.stop()
    else:
        archivo_subido = st.file_uploader("Sube tu archivo Excel de Jira", type=['xlsx'])
        if archivo_subido is not None:
            with st.spinner("Procesando archivo subido..."):
                df = pd.read_excel(archivo_subido, sheet_name='Base')
                necesita_transformacion = not any(col in df.columns for col in TEMAS)
                st.success("Archivo cargado con éxito.")
                st.session_state.automatico = True
        else:
            st.info("Por favor, sube un archivo para continuar.")
            st.stop()
    
    if necesita_transformacion:
        with st.status("Transformando datos...", expanded=True) as status:
            # Tipos de datos
            columnas_texto = [
                "Resumen", "Descripción", "Causa Raíz / Origen", 
                "Descripción de la Solución:", "Activo de SW", 
                "Equipo Resolutor", "Servicio Reportado", "Resuelto con:"
            ]
            df['Fecha Real Incidente'] = pd.to_datetime(df['Fecha Real Incidente'], errors='coerce', utc=True).dt.tz_localize(None)
            df['Fecha Resolución Real Incidente'] = pd.to_datetime(df['Fecha Resolución Real Incidente'], errors='coerce', utc=True).dt.tz_localize(None)
            df['Duración Incidente'] = pd.to_numeric(df['Duración Incidente'], errors='coerce')
            for col in columnas_texto:
                if col in df.columns:
                    df[col] = df[col].astype(str)

            df = df[COLUMNS_SELECTED]
            df.columns = COLUMNS_RENAMED

            df = data.duracion(df, 'Fecha_Inicio', 'Fecha_Fin', 'Duracion')
            st.write("Generando tópicos con BERTopic, esto puede tardar varios minutos...")

            columnas = ['Resumen', 'Descripcion', 'Causa', 'Solucion']

            for col in columnas:
                df[col] = df[col].fillna("Sin Información").astype(str).str.strip()
                df[col] = df[col].replace("", "Sin Información")
                df[col] = df[col].replace("nan", "Sin Información")
                df[col] = df[col].replace("NaT", "Sin Información")
                df[col] = df[col].replace("None", "Sin Información")

            df = bertopic.bertopic_app(df.copy(), columnas)
            df = data.clean(df, COLUMNS_RENAMED, 'Fecha_Inicio')
            df['Equipo'] = df['Equipo'].str.strip().dropna()
            
            if not os.path.exists('data'): os.makedirs('data')

            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            ruta_nueva = f"data/Jira_{fecha_hoy}.xlsx"
            df.to_excel(ruta_nueva, index=False, sheet_name='Base')
            status.update(label=f"Proceso finalizado. Archivo guardado: {ruta_nueva}", state="complete", expanded=False)

    st.session_state.df = df
    st.success("¡Datos listos para el análisis!")
    st.rerun()

else:
    df = st.session_state.df

# ---------------------------------------- ELECCIÓN -----------------------------------------
    if st.session_state.seccion == "Eleccion":
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        with col1:
            st.button("📊 Gestión", on_click=cambiar_seccion, args=["Gestion"], width='stretch')
        with col2:
            st.button("⚙️ Operación", on_click=cambiar_seccion, args=["Operacion"], width='stretch')
        with col3:
            st.button("🔄 Actualizar Datos de Jira", on_click=cambiar_seccion, args=["Actualizar"], width='stretch')
        with col4:
            st.button("🔄 Actualizar Datos de Jira Manual", on_click=cambiar_seccion, args=["Actualizar/Manual"], width='stretch')

# ---------------------------------------- GESTIÓN -----------------------------------------
    elif st.session_state.seccion == "Gestion":
        df = df.copy()
        management.management_app(df)

# ---------------------------------------- OPERACIÓN -----------------------------------------
    elif st.session_state.seccion == "Operacion":
        df = df.copy()
        operation.operation_app(df)

# -------------------------------------- ACTUALIZACIÓN ---------------------------------------  
    elif st.session_state.seccion == "Actualizar":
        st.title("Actualización de Datos desde Jira")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Iniciar Actualización de Datos", width='stretch'):
                st.session_state.df = None
                st.session_state.seccion_op = "Visualizacion"
                st.session_state.seccion = "Eleccion"
                st.session_state.automatico = True
                # Borrar excel
                archivos = glob.glob("data/Jira_*.xlsx")
                for archivo in archivos:
                    os.remove(archivo)
                st.rerun()
        with col2:
            if st.button("Volver al menú principal", width='stretch'):
                st.session_state.seccion_ma = "Visualizacion"
                st.session_state.seccion = "Eleccion"
                st.rerun()
    
    elif st.session_state.seccion == "Actualizar/Manual":
        st.title("Actualización de Datos desde Jira de forma Manual")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Iniciar Actualización de Datos", width='stretch'):
                st.session_state.df = None
                st.session_state.automatico = False
                st.session_state.seccion_op = "Visualizacion"
                st.session_state.seccion = "Eleccion"
                # Borrar excel
                archivos = glob.glob("data/Jira_*.xlsx")
                for archivo in archivos:
                    os.remove(archivo)
                st.rerun()
        
        with col2:
            if st.button("Volver al menú principal", width='stretch'):
                st.session_state.seccion_ma = "Visualizacion"
                st.session_state.seccion = "Eleccion"
                st.rerun()



