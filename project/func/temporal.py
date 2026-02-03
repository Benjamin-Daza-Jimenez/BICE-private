import plotly.graph_objects as go
import func.data as data
import streamlit as st
import pandas as pd

MESES = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}

def anual_plotly(df):
    stats = df.groupby(['Año', 'Mes'])['Duracion'].agg(['median', 'count']).reset_index()
    stats.columns = ['Año', 'Mes', 'Mediana_Duracion', 'Volumen_Tickets']
    
    stats['Total_anual'] = stats.groupby('Año')['Volumen_Tickets'].transform('sum')
    stats['Porcentaje_Volumen'] = ((stats['Volumen_Tickets'] / stats['Total_anual']) * 100).round(2)
    
    años = sorted(stats['Año'].unique())

    color_vol = "#00D4FF"
    color_med = "#FFB347"

    for anio in años:
        print(f"Gráfico anual {anio} guardado.")
        with st.expander(f"🔍 Explorar gráfico del año {anio}", expanded=False):
            df_anio = stats[stats['Año'] == anio].sort_values('Mes')
            meses_etiquetas = [MESES[m] for m in df_anio['Mes']]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=meses_etiquetas,
                y=df_anio['Volumen_Tickets'],
                name='Volumen Tickets',
                marker_color=color_vol,
                offsetgroup=1,
                text=df_anio['Volumen_Tickets'].astype(str) + "<br>(" + df_anio['Porcentaje_Volumen'].astype(str) + "%)",
                textposition='outside',
                yaxis='y1',
                hovertemplate="<b>Mes:</b> %{x}<br><b>Tickets:</b> %{y}<br><b>Participación:</b> %{text}<extra></extra>"
            ))

            fig.add_trace(go.Bar(
                x=meses_etiquetas,
                y=df_anio['Mediana_Duracion'],
                name='Mediana Duración (h)',
                marker_color=color_med,
                offsetgroup=2,
                text=df_anio['Mediana_Duracion'].astype(str) + "h",
                textposition='outside',
                yaxis='y2',
                hovertemplate="<b>Mes:</b> %{x}<br><b>Mediana:</b> %{y}h<extra></extra>"
            ))

            fig.update_layout(
                title=dict(
                    text=f'Gobernanza TI BICE: Carga y Eficiencia {anio}<br><span style="font-size:14px; color:#AAB7B8;">Volumen Anual vs. Mediana de Tiempo de Respuesta</span>',
                    x=0.5,
                    xanchor='center',
                    font=dict(size=24, color="#FFFFFF")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8F9FA'),
                height=650,

                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.05,
                    xanchor='left',
                    x=0,
                    font=dict(size=14)
                ),
                xaxis=dict(
                    tickfont=dict(size=14, color='#FFFFFF'),
                    showline=False
                ),
                yaxis=dict(
                    title=dict(text='Volumen de Tickets', font=dict(color=color_vol, size=15)),
                    tickfont=dict(color=color_vol),
                    range=[0, df_anio['Volumen_Tickets'].max() * 1.4], 
                    side='left'
                ),
                yaxis2=dict(
                    title=dict(text='Mediana Duración (Horas)', font=dict(color=color_med, size=15)),
                    tickfont=dict(color=color_med),
                    range=[0, df_anio['Mediana_Duracion'].max() * 1.4],
                    side='right',
                    overlaying='y',
                    showgrid=False
                ),
                margin=dict(l=50, r=50, t=150, b=50)
            )

            st.plotly_chart(fig, use_container_width=True)

def mensual_plotly(df):
    colores = [
        [0.0, "#FFFFFF"],
        [0.1, "#C6E5F7"],   
        [0.4, "#3498DB"],   
        [0.7, "#F1C40F"],   
        [1.0, "#D35400"]  
    ]

    años = sorted(df['Año'].unique())

    for anio in años:
        print(f"Gráfico mensual {anio} guardado.")
        with st.expander(f"🔍 Explorar gráfico del año {anio}", expanded=False):
            df_anio = df[df['Año'] == anio]

            pivot_volume = df_anio.pivot_table(index='Día', columns='Mes', values='Duracion', aggfunc='count')
            pivot_duration = df_anio.pivot_table(index='Día', columns='Mes', values='Duracion', aggfunc='median').round(2)
            pivot_volume = pivot_volume.reindex(range(1, 32))
            pivot_duration = pivot_duration.reindex(range(1, 32))
            
            z_data = pivot_volume.fillna(0).values
            text_data = pivot_duration.applymap(lambda x: f"{x}h" if not pd.isna(x) else "").values

            meses_nombres = [MESES[int(m)] for m in pivot_volume.columns]

            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=meses_nombres,
                y=pivot_volume.index,
                colorscale=colores,
                text=text_data,
                texttemplate="%{text}",
                textfont={"size":11},
                hoverinfo='z+text',
                hovertemplate="<b>Mes:</b> %{x}<br><b>Día:</b> %{y}<br><b>Tickets:</b> %{z}<br><b>Mediana:</b> %{text}<extra></extra>",
                colorbar=dict(
                    title="Cantidad de Tickets", 
                    thickness=20,
                    len=0.5,
                    ypad=10,
                    tickfont=dict(color='#F8F9FA')
                ),
            ))

            fig.update_layout(
                title=dict(
                    text=f'Mapa de Calor Operativo BICE {anio}<br><span style="font-size:14px;">Color: Volumen de Tickets | Texto: Mediana Duración (h)</span>',
                    x=0.5,
                    xanchor='center',
                    font=dict(size=22, color="#FFFFFF")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8F9FA'),
                xaxis=dict(title='Mes', side='bottom'),
                yaxis=dict(
                    title='Día del Mes', 
                    autorange=True, 
                    dtick=1
                ),
                height=900,
                margin=dict(l=50, r=50, t=120, b=50)
            )

            st.plotly_chart(fig, use_container_width=True)

def temporal_app(df_original):
    # Crear un nuevo DataFrame solo con las columnas de fecha
    df = df_original[['Fecha_Inicio', 'Duracion']].copy()

    # Limpiar el DataFrame
    df = data.clean(df, ['Fecha_Inicio', 'Duracion'], 'Fecha_Inicio')

    # Extraer características temporales
    df['Año'] = df['Fecha_Inicio'].dt.year 
    df['Mes'] = df['Fecha_Inicio'].dt.month
    df['Día'] = df['Fecha_Inicio'].dt.day
    df['Día_Semanal'] = df['Fecha_Inicio'].dt.dayofweek + 1 

    return df