import streamlit as st
import pandas as pd

TEMAS = [
    'Temas_Resumen', 
    'Temas_Descripcion', 
    'Temas_Causa', 
    'Temas_Solucion'
    ]

def ficha_tecnica(df, col):

    mask_procesados = df[TEMAS].ne("No Aplica (Ticket Incompleto)").all(axis=1)
    total = len(df)
    no_cat = len(df[~mask_procesados])

    col_counts = df[col].value_counts()
    lista_col = col_counts.index.tolist()

    selector = st.selectbox(f"Seleccione {col} para ver su ficha técnica", lista_col, index=None, placeholder="Seleccione una opción")

    if selector:
        df_ficha = df[df[col] == selector].copy()
        total_casos = len(df_ficha)

        if pd.api.types.is_datetime64_any_dtype(df_ficha['Fecha_Inicio']):
            fecha_min = df_ficha['Fecha_Inicio'].min()
            fecha_max = df_ficha['Fecha_Inicio'].max()

            txt_fechas = f"{fecha_min.strftime('%d-%m-%Y')} al {fecha_max.strftime('%d-%m-%Y')}"

            rango_dias = (fecha_max - fecha_min).days
            meses_antiguedad = max(rango_dias / 30, 1)
        else:
            txt_fechas = "Fechas no disponibles"
            meses_antiguedad = 1
        
        orden_prioridad = ['Highest', 'High', 'Medium', 'Low', 'Lowest']

        if 'Prioridad' in df_ficha.columns:
            grupo = df_ficha.groupby('Prioridad').agg(
                Conteo=('Fecha_Inicio', 'count'),
                Duracion_Prom=('Duracion', 'mean') if 'Duracion' in df_ficha.columns else ('Fecha_Inicio', lambda x: 0)
            )
            grupo = grupo.reindex(orden_prioridad).fillna(0)
        else:
            grupo = pd.DataFrame(index=orden_prioridad, data={'Conteo':0, 'Duracion_Prom':0})

        # Diseño
        st.divider()

        st.markdown(f"### Resumen de Ficha Técnica para **{selector}**", help=f"Análisis detallado de los casos asociados a {col}: {selector}.")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            with st.container(border=True):
                st.markdown(f"#### **📋 Total de Casos**", help=f"Número total de casos para el {col} seleccionado.")
                st.markdown(f"## {total_casos}")
                st.write("&nbsp;")
                st.markdown(f"#### **🚫 Sin Categoría**", help=f"Número de casos sin categoría para el {col} seleccionado.")
                st.markdown(f"## {len(df_ficha[~mask_procesados])}")
        with kpi2:
            with st.container(border=True):
                st.markdown("#### **📊 Casos x Prioridad**", help=f"Número de casos por prioridad para el {col} seleccionado.")
                st.write("&nbsp;")
                for p in orden_prioridad:
                    val = int(grupo.loc[p, 'Conteo'])
                    if val > 0:
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**{val}**")
                    else:
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**-**")
        with kpi3:
            with st.container(border=True):
                st.markdown("#### **⏱️ Tiempo Resolución**", help=f"Duración promedio de resolución por prioridad para el {col} seleccionado.")
                st.write("&nbsp;")
                for p in orden_prioridad:
                    val = grupo.loc[p, 'Conteo']
                    if val > 0:
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**{grupo.loc[p, 'Duracion_Prom']:.0f}h**")
                    else:
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**-**")

        with kpi4:
            with st.container(border=True):
                st.markdown("#### **📅 Casos Mensuales**", help=f"Cantidad de casos por mes para el {col} seleccionado.")
                st.write(f"Período: {txt_fechas}")
                for p in orden_prioridad:
                    if grupo.loc[p, 'Conteo'] > 0:
                        mensual = grupo.loc[p, 'Conteo'] / meses_antiguedad
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**{mensual:.0f}**")
                    else:
                        c_lab, c_val = st.columns([2, 1])
                        c_lab.write(p)
                        c_val.write(f"**-**")

        st.write("&nbsp;")
        st.markdown("---")
        st.write("&nbsp;")
        
        
        st.markdown(f"### Análisis de Causa, Solución y Asignación de Equipo", help=f"Esta información es en base a los tickets categorizados ({total - no_cat} tickets).")
        st.write("&nbsp;")

        df_ficha = df_ficha[mask_procesados].copy()

        c_causa, c_solucion = st.columns(2)
        c_equipo, c_resuelto = st.columns(2)

        top_causas_series = df_ficha['Temas_Causa'].value_counts(normalize=True).head(3)
        top_causas_nombres = top_causas_series.index.tolist()
        df_top_causas = df_ficha[df_ficha['Temas_Causa'].isin(top_causas_nombres)]

        with c_causa:
            with st.container(border=True):
                st.subheader("🎯 Top 3 Causas")
                st.write("&nbsp;")
                
                if not top_causas_series.empty:
                    for causa, pct in top_causas_series.items():

                        col_pct, col_txt = st.columns([1, 6])
                        col_pct.markdown(f"**{pct*100:.0f}%**")
                        col_txt.markdown(f"{causa}")

                        st.progress(float(pct))
                        st.write("") 
                else:
                    st.info("Sin datos de causa.")

        with c_solucion:
            with st.container(border=True):
                st.subheader("💡 Top 3 Soluciones")
                st.caption("Asociadas a las causas principales")
                
                if not df_top_causas.empty:
                    top_sols = df_top_causas['Temas_Solucion'].value_counts(normalize=True).head(3)
                    for sol, pct in top_sols.items():

                        col_pct, col_txt = st.columns([1, 6])
                        col_pct.markdown(f"**{pct*100:.0f}%**")
                        col_txt.markdown(f"{sol}")
                        
                        st.progress(float(pct))
                        st.write("")
                else:
                    st.info("Sin soluciones para estas causas.")


        with c_equipo:
            with st.container(border=True):
                st.subheader("👥 Equipo")
                top_equipos = df_ficha['Equipo'].value_counts(normalize=True).head(3)
                
                if not top_equipos.empty:
                    equipo_lider = top_equipos.index[0]
                    pct_lider = top_equipos.values[0]

                    if pct_lider > 0.6:
                        st.success(f"**Asignación Recomendada:** Existe una alta especialización en **{equipo_lider}** ({pct_lider*100:.0f}%). Se sugiere asignar directamente para optimizar el tiempo de resolución.")
                    elif pct_lider > 0.4:
                        st.warning(f"**Asignación Sugerida:** El equipo **{equipo_lider}** concentra la mayoría de los casos, aunque existe dispersión. Se recomienda validar la causa técnica antes de derivar.")
                    else:
                        st.error(f"**Revisión Necesaria:** No hay un equipo dominante definido. Por favor, consulte la matriz de escalamiento detallada para evitar rebotes entre áreas.")
                    st.caption("Distribución de carga:")
                    for eq, pct in top_equipos.items():
                        col_pct, col_txt = st.columns([1, 6])
                        col_pct.markdown(f"**{pct*100:.0f}%**")
                        col_txt.markdown(f"{eq}")
                        st.progress(float(pct))
                else:
                    st.info("Sin datos de equipos.")
        
        with c_resuelto:
            with st.container(border=True):
                st.subheader("🛠️ Resuelto con")
                resuelto_counts = df_ficha['Resuelto_con'].value_counts()
                
                if not resuelto_counts.empty:
                    
                    # Listado de los 8-9 elementos
                    for modo, cant in resuelto_counts.items():
                        r1, r2 = st.columns([3, 1])
                        # Usamos un estilo limpio sin bullets
                        r1.markdown(f"<span style='font-size:0.9rem'>{modo}</span>", unsafe_allow_html=True)
                        r2.markdown(f"**{cant}**")
                else:
                    st.info("Sin datos de resolución.")
        


