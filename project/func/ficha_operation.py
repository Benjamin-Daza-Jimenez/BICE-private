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

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            with st.container(border=True):
                st.metric("Total Incidentes", total_casos)
                st.markdown(f"{len(df_ficha[~mask_procesados])} no categorizados")
                st.caption(f"📅 **Rango:**\n{txt_fechas}")
        with kpi2:
            with st.container(border=True):
                st.markdown("**📊 Por Prioridad**")
                txt_prio = ""
                for prio in orden_prioridad:
                    val = int(grupo.loc[prio, 'Conteo'])
                    if val > 0:
                        txt_prio += f"- **{prio}:** {val}\n"
                
                if not txt_prio: txt_prio = "Sin datos"
                st.markdown(txt_prio)
        with kpi3:
            with st.container(border=True):
                st.markdown("**⏱️ Tiempo Resolución**", help="Duración promedio por prioridad")
                txt_time = ""
                for prio in orden_prioridad:
                    val = grupo.loc[prio, 'Conteo']
                    if val > 0:
                        horas = grupo.loc[prio, 'Duracion_Prom']
                        txt_time += f"- **{prio}:** {horas:.0f} h\n"
                
                if not txt_time: txt_time = "N/A"
                st.markdown(txt_time)
        with kpi4:
            with st.container(border=True):
                st.markdown("**📅 Frec. Mensual**")
                txt_freq = ""
                for prio in orden_prioridad:
                    val = grupo.loc[prio, 'Conteo']
                    if val > 0:
                        mensual = val / meses_antiguedad
                        fmt = f"{mensual:.0f}"
                        txt_freq += f"- **{prio}:** {fmt}\n"
                
                if not txt_freq: txt_freq = "N/A"
                st.markdown(txt_freq)

        st.markdown("---")
        
        st.markdown(f"### Análisis de Causa, Solución y Asignación de Equipo", help=f"Esta información es en base a los tickets categorizados ({total - no_cat} tickets).")
        df_ficha = df_ficha[mask_procesados].copy()

        c_causa, c_solucion, c_equipo = st.columns(3)
        top_causas_series = df_ficha['Temas_Causa'].value_counts(normalize=True).head(3)
        top_causas_nombres = top_causas_series.index.tolist()
        df_top_causas = df_ficha[df_ficha['Temas_Causa'].isin(top_causas_nombres)]

        with c_causa:
            with st.container(border=True):
                st.subheader("Top 3 Causas")
                st.caption("Causas más frecuentes:")
                if not top_causas_series.empty:
                    for causa, pct in top_causas_series.items():
                        st.markdown(f"**{pct*100:.1f}%** - {causa}")
                        st.progress(float(pct))
                else:
                    st.info("Sin datos de causa.")

        with c_solucion:
            with st.container(border=True):
                st.subheader("Top 3 Soluciones")
                st.caption("Para las causas listadas a la izquierda:")
                if not df_top_causas.empty:
                    top_sols = df_top_causas['Temas_Solucion'].value_counts(normalize=True).head(3)
                    for sol, pct in top_sols.items():
                        st.markdown(f"**{pct*100:.1f}%** - {sol}")
                        st.progress(float(pct)) 
                else:
                    st.info("No hay soluciones registradas para estas causas.")


        with c_equipo:
            with st.container(border=True):
                st.subheader("Asignación de Equipos")
                top_equipos = df_ficha['Equipo'].value_counts(normalize=True).head(3)
                if not top_equipos.empty:
                    equipo_lider = top_equipos.index[0]
                    pct_lider = top_equipos.values[0]

                    if pct_lider > 0.6:
                        st.success(f"✅ **Recomendación:** Asignar directamente a **{equipo_lider}**.")
                    elif pct_lider > 0.4:
                        st.warning(f"⚠️ **Recomendación:** Probablemente **{equipo_lider}**, pero revisar causa.")
                    else:
                        st.error("❓ **Recomendación:** Asignación dispersa. Revisar matriz detallada.")

                    st.caption("Distribución histórica:")
                    for eq, pct in top_equipos.items():
                        st.write(f"• **{eq}**: {pct*100:.1f}%")
                else:
                    st.write("Sin información de equipos.")


