import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm
import pandas as pd
import streamlit as st

def grafico_gauss(df):
    print(f"Gráfico de Campana de Gauss guardado.")
    df['Fecha_Inicio'] = pd.to_datetime(df['Fecha_Inicio'])
    df_laboral = df[df['Fecha_Inicio'].dt.weekday < 5].copy()
    df_diario = df_laboral.groupby(df_laboral['Fecha_Inicio'].dt.date).size().reset_index(name='Volumen')
    datos = df_diario['Volumen']

    if len(datos) < 5:
        st.warning("Insuficientes datos para el análisis.")
        return

    mu, sigma = datos.mean(), datos.std()
    sigma_calc = sigma if sigma > 0 else 0.001
    x = np.linspace(0, datos.max() * 1.3, 300)
    y = norm.pdf(x, mu, sigma_calc)

    fig = go.Figure()

    # --- PALETA DE COLORES AJUSTADA ---
    COLOR_BARRAS = '#607D8B'    
    COLOR_MODELO = '#FFB347'    
    RANGO_68 = 'rgba(46, 204, 113, 0.35)'  
    RANGO_95 = 'rgba(241, 196, 15, 0.25)'  
    RANGO_99 = 'rgba(231, 76, 60, 0.2)'    

    # 3. CAPAS DE SOMBREADO (Se grafican primero para quedar atrás)
    # 99.7%
    x3 = np.linspace(max(0, mu - 3*sigma_calc), mu + 3*sigma_calc, 150)
    fig.add_trace(go.Scatter(
        x=np.concatenate([x3, x3[::-1]]),
        y=np.concatenate([norm.pdf(x3, mu, sigma_calc), np.zeros_like(x3)]),
        fill='toself', fillcolor=RANGO_99, line=dict(color='rgba(0,0,0,0)'),
        name='Exigencia Máxima (99.7%)', hoverinfo='skip'
    ))

    # 95%
    x2 = np.linspace(max(0, mu - 2*sigma_calc), mu + 2*sigma_calc, 150)
    fig.add_trace(go.Scatter(
        x=np.concatenate([x2, x2[::-1]]),
        y=np.concatenate([norm.pdf(x2, mu, sigma_calc), np.zeros_like(x2)]),
        fill='toself', fillcolor=RANGO_95, line=dict(color='rgba(0,0,0,0)'),
        name='Capacidad Nominal (95%)', hoverinfo='skip'
    ))

    # 68%
    x1 = np.linspace(max(0, mu - 1*sigma_calc), mu + 1*sigma_calc, 150)
    fig.add_trace(go.Scatter(
        x=np.concatenate([x1, x1[::-1]]),
        y=np.concatenate([norm.pdf(x1, mu, sigma_calc), np.zeros_like(x1)]),
        fill='toself', fillcolor=RANGO_68, line=dict(color='rgba(0,0,0,0)'),
        name='Operación Rutinaria (68%)', hoverinfo='skip'
    ))

    # 4. HISTOGRAMA REAL
    fig.add_trace(go.Histogram(
        x=datos, histnorm='probability density', name='Días Reales',
        marker=dict(color=COLOR_BARRAS, opacity=0.5, line=dict(color=None, width=0.5)),
        nbinsx=25, hovertemplate="<b>Volumen:</b> %{x} tickets<br><b>Densidad:</b> %{y:.4f}<extra></extra>"
    ))

    # 5. LÍNEA GAUSS
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='lines', name='Curva Gauss',
        line=dict(color=COLOR_MODELO, width=4),
        hovertemplate="<b>Modelo:</b> %{x:.1f} tickets<br><b>Densidad:</b> %{y:.4f}<extra></extra>"
    ))

    # 6. LAYOUT CON MARGEN Y ESPACIADO
    fig.update_layout(
        title=dict(
            text=f'ANÁLISIS DE CAPACIDAD OPERATIVA<br><span style="font-size:15px; color:#AAB7B8;">Media: {mu:.1f} | Desviación (σ): {sigma:.1f} | Muestra: {len(datos)} días</span><br> ',
            x=0.5, xanchor="center", font=dict(size=22, color=None)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=None),
        hoverlabel=dict(bgcolor="#2C3E50", font_size=13, font_color=None),
        xaxis=dict(
            title='Cantidad de Tickets por Día', range=[0, datos.max() * 1.25],
            gridcolor='rgba(255,255,255,0.05)', zeroline=True, zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(title='Densidad', showticklabels=True, gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        height=650,
        margin=dict(l=50, r=50, t=150, b=50) 
    )

    # Línea de la Media
    fig.add_vline(x=mu, line_dash="dash", line_color="white", opacity=0.6)

    st.plotly_chart(fig, use_container_width=True)

    # Guía de interpretación
    st.markdown("---") 
    st.subheader("Guía de Interpretación Operativa")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"### 🟢 68%")
        st.write("**Operación Rutinaria**")
        st.markdown("Volumen habitual. El equipo maneja esta carga con eficiencia estándar y cumplimiento total.")

    with col2:
        st.markdown(f"### 🟡 95%")
        st.write("**Capacidad Nominal**")
        st.markdown("Límite de compromiso. Es el máximo esfuerzo esperado del equipo antes de entrar en zona de estrés.")

    with col3:
        st.markdown(f"### 🔴 99.7%")
        st.write("**Evento Crítico**")
        st.markdown("Anomalía estadística. Volúmenes excepcionales que requieren planes de contingencia o justificación técnica.")