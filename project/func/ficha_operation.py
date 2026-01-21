import streamlit as st
import pandas as pd
import numpy as np

def ficha_tecnica(df, col):
    st.markdown("## 🏥 Ficha Técnica Unificada")
    st.caption("Resumen estratégico para toma de decisiones rápida.")

    col_counts = df[col].value_counts()
    lista_col = col_counts.index.tolist()

    selector = st.selectbox(f"Seleccione {col} para ver su ficha técnica", lista_col, index=None, placeholder="Seleccione una opción")

    if selector:
        df_ficha = df[df[col] == selector].copy()
        total_casos = len(df_ficha)

        if pd.api.types.is_datetime64_any_dtype(df_ficha['Fecha_Inicio']):
            rango_dias = (df_ficha['Fecha_Inicio'].max() - df_ficha['Fecha_Inicio'].min()).days
            meses_antiguedad = max(rango_dias / 30, 1)
            promedio = total_casos / meses_antiguedad
            frecuencia = f"{promedio:.0f} tickets"
        else:
            frecuencia = "N/A"
        
        if 'Duracion' in df_ficha.columns and pd.api.types.is_numeric_dtype(df_ficha['Duracion']):
            duracion = df_ficha['Duracion'].mean()
            duracion_promedio = f"{duracion:.0f} hrs"
        else:
            duracion_promedio = "N/A (Datos no disponibles)"
        
        prioridad_top = df_ficha['Prioridad'].mode()[0] if 'Prioridad' in df_ficha.columns else "Desconocida"

        # Diseño
        st.divider()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            with st.container(border=True):
                st.metric("Total Incidentes", total_casos)
        with kpi2:
            with st.container(border=True):
                st.metric("Frecuencia Mensual", frecuencia, help="Promedio tickets/mes")
        with kpi3:
            with st.container(border=True):
                st.metric("Tiempo Resolución", duracion_promedio, help="Tiempo promedio de arreglo (MTTR)")
        with kpi4:
            with st.container(border=True):
                st.metric("Prioridad Típica", prioridad_top, delta_color="off")

        st.markdown("---")

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


