from sklearn.feature_extraction.text import CountVectorizer
import plotly.graph_objects as go
from nltk.corpus import stopwords
from bertopic import BERTopic
import plotly.express as px
import func.data as data
import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import json
import io
import os

def bertopic_app(df, columnas, verbose=True):
    df_temp = df.copy()

    try:
        stop_words_es = stopwords.words('spanish')
    except:
        stop_words_es = []

    stop_words_es.extend(['que', 'el', 'la', 'en', 'de', 'para', 'se', 'no', 'si', 'un', 'con'])
    vectorizer_model = CountVectorizer(stop_words=stop_words_es)

    for columna in columnas:
        print(f"Procesando columna: {columna} con BERTopic")

        df_temp = data.clean_bert(df_temp, columna)
        docs = df_temp['temp_para_modelo'].astype(str).tolist()

        model = BERTopic(language="multilingual", vectorizer_model=vectorizer_model, verbose=verbose)
        topics, _ = model.fit_transform(docs)

        new_topics = topics
        if len(set(topics) - {-1}) > 0 and -1 in topics:
            try:
                new_topics = model.reduce_outliers(docs, topics, strategy="c-tf-idf")
                model.update_topics(docs, new_topics)
            except:
                print("No se pudieron reducir outliers, manteniendo temas originales.")

        topic_info = model.get_topic_info().set_index('Topic')['Name'].to_dict()

        nombres_temas = []
        for t in new_topics:
            nombre = topic_info.get(t, "Sin Clasificar")

            nombre_limpio = nombre.split('_', 1)[-1].replace('_', ' ').title() if '_' in nombre else nombre
            nombres_temas.append(nombre_limpio)
        
        idx_original = df_temp.columns.get_loc(columna)
        nombre_nueva_col = f"Temas_{columna}"

        df_temp.insert(idx_original + 1, nombre_nueva_col, nombres_temas)
        if 'temp_para_modelo' in df_temp.columns:
            df_temp.drop(columns=['temp_para_modelo'], inplace=True)
    
    return df_temp

def Json_Files(df, columna_incio, ruta = "data/JSONs"):
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    df[columna_incio] = pd.to_datetime(df[columna_incio])

    grupos = df.groupby([df[columna_incio].dt.year, df[columna_incio].dt.month])

    for (año, mes), tabla in grupos:
        nombre_archivo = f"tickets_{año}_{mes:02d}.json"
        ruta_archivo = os.path.join(ruta, nombre_archivo)
        data_dict = tabla.to_dict(orient="records")
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4, default=str)

def Json_Zip(df, columna_incio):
    Json_Files(df, columna_incio)

    df[columna_incio] = pd.to_datetime(df[columna_incio])
    zip = io.BytesIO()

    with zipfile.ZipFile(zip, "a", zipfile.ZIP_DEFLATED, False) as zf:
        grupos = df.groupby([df[columna_incio].dt.year, df[columna_incio].dt.month])

        for(año, mes), tabla in grupos:
            json_data = tabla.to_json(orient="records", date_format='iso', force_ascii=False)
            nombre_archivo = f"{año}_{mes:02d}.json"
            zf.writestr(nombre_archivo, json_data)
    
    listo = zip.getvalue()

    # Eliminar archivos temporales
    ruta = "data/JSONs"
    if os.path.exists(ruta):
        for archivo in os.listdir(ruta):
            os.remove(os.path.join(ruta, archivo))
        os.rmdir(ruta)
    
    return listo

def bertopic_graph_plotly(df):
    config = [
        ('Resumen', 'Temas_Resumen', px.colors.sequential.Teal),
        ('Descripcion', 'Temas_Descripcion', px.colors.sequential.Greens),
        ('Causa', 'Temas_Causa', px.colors.sequential.OrRd),
        ('Solucion', 'Temas_Solucion', px.colors.sequential.Purples)
    ]

    for col, tema, color_scale in config:
        print(f"Gráfico {tema} guardado.")
        with st.expander(f"🔍 Explorar gráfico de {col}", expanded=False):
            if tema not in df.columns:
                continue
        
            
            counts = df[tema].value_counts().reset_index()
            counts.columns = ['Tema', 'Cantidad']
            counts = counts.sort_values(by=['Cantidad', 'Tema'], ascending=[False, True]).reset_index(drop=True)

            total_tickets = counts['Cantidad'].sum()
            counts['Porcentaje'] = (counts['Cantidad'] / total_tickets) * 100
            counts['Acumulado'] = counts['Porcentaje'].cumsum()

            # --- LÓGICA DE TRANSICIÓN SUAVE (Colchón de Visibilidad) ---
            max_perc = counts['Porcentaje'].max()
            limite_otros_valor = max_perc * 1.15 
            
            # 1. Punto donde se cruza el 80%
            indice_80 = counts[counts['Acumulado'] >= 80].index[0] if any(counts['Acumulado'] >= 80) else len(counts)
            
            # 2. Añadir un colchón de 5 categorías para que no sea abrupto
            indice_colchon = min(indice_80 + 5, len(counts))
            
            # 3. Agrupar lo que sobra DESPUÉS del colchón, respetando el límite de altura
            otros_indices = []
            suma_otros_perc = 0
            
            for i in range(len(counts)-1, indice_colchon, -1):
                if suma_otros_perc + counts.iloc[i]['Porcentaje'] <= limite_otros_valor:
                    suma_otros_perc += counts.iloc[i]['Porcentaje']
                    otros_indices.append(i)
                else:
                    break
            
            if otros_indices:
                otros_indices.sort()
                df_main = counts.drop(otros_indices).copy()
                otros_cant = counts.iloc[otros_indices]['Cantidad'].sum()
                otros_temas_nombres = counts.iloc[otros_indices]['Tema'].tolist()
                
                df_otros = pd.DataFrame({
                    'Tema': [f'OTRAS {len(otros_indices)} CATEGORÍAS'], 
                    'Cantidad': [otros_cant], 
                    'Porcentaje': [(otros_cant/total_tickets)*100]
                })
                df_plot = pd.concat([df_main, df_otros], ignore_index=True)
            else:
                df_plot = counts.copy()

            df_plot['Acumulado_Final'] = df_plot['Porcentaje'].cumsum()

            if df_plot.empty:
                st.warning(f"No hay datos para generar el gráfico de {col}.")
                continue

            n_temas_principales = len(df_plot) - (1 if 'CATEGORÍAS' in df_plot['Tema'].iloc[-1] else 0)
            colors = px.colors.sample_colorscale(color_scale[::-1], np.linspace(0, 1, n_temas_principales))
            
            if 'CATEGORÍAS' in df_plot['Tema'].iloc[-1]:
                colors.append('rgb(100, 100, 100)') 

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=df_plot['Tema'],
                y=df_plot['Porcentaje'],
                marker=dict(color=colors),
                customdata=df_plot['Cantidad'],
                hovertemplate="<b>Tema:</b> %{x}<br><b>Cantidad:</b> %{customdata} tickets<br><b>% Individual:</b> %{y:.1f}%<extra></extra>"
            ))

            fig.add_trace(go.Scatter(
                x=df_plot['Tema'],
                y=df_plot['Acumulado_Final'],
                yaxis='y2',
                line=dict(color='#FFB347', width=4),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate="<b>Acumulado:</b> %{y:.1f}%<extra></extra>"
            ))

            fig.update_layout(
                title=dict(
                    text=f"Pareto Estratégico: {col}<br><span style='font-size:14px; color:#AAB7B8;'>Análisis con colchón de visibilidad post-80%</span>",
                    x=0.5, font=dict(size=24), xanchor='center'
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8F9FA'),
                height=700,
                margin=dict(t=120, b=150, l=60, r=60),
                hoverlabel=dict(bgcolor="#1F2428", font_size=18),
                xaxis=dict(tickangle=-45, showgrid=False, showticklabels=True, tickfont=dict(size=11)),
                yaxis=dict(title="Impacto Individual (%)", ticksuffix="%", range=[0, max(df_plot['Porcentaje']) * 1.15]),
                yaxis2=dict(title="Total Acumulado (%)", ticksuffix="%", overlaying='y', side='right', range=[0, 105], showgrid=False),
                showlegend=False,
                hovermode="x unified"
            )

            fig.add_shape(type="line", x0=-0.5, x1=len(df_plot)-0.5, y0=80, y1=80, yref='y2', 
                        line=dict(color="rgba(255, 0, 0, 0.6)", dash="dash", width=2))

            st.plotly_chart(fig, use_container_width=True)



            # --- NUEVA SECCIÓN: TABLA DE DETALLE CORPORATIVO ---
            df_temp = df.copy()
            df_temp['Recuento'] = 1
            
            tabla_detalle = df_temp.groupby(tema).agg({
                'Recuento': 'count',
                'Equipo': lambda x: ", ".join(sorted(set(x.dropna().astype(str)))),
                'Activo_SW': lambda x: ", ".join(sorted(set(x.dropna().astype(str))))
            }).reset_index()

            tabla_detalle.columns = ['Tema', 'Tickets', 'Equipos Involucrados', 'Activos de SW']
            tabla_detalle = tabla_detalle.sort_values(by=['Tickets', 'Tema'], ascending=[False, True])
            
            tabla_detalle['% del Total'] = (tabla_detalle['Tickets'] / total_tickets * 100).round(1).astype(str) + '%'
            tabla_detalle['% Pareto'] = (tabla_detalle['Tickets'].cumsum() / total_tickets * 100).round(1).astype(str) + '%'

            tabla_detalle = tabla_detalle[['Tema', 'Tickets', '% del Total', '% Pareto', 'Equipos Involucrados', 'Activos de SW']]

            st.markdown(f"#### 📋 Detalle Ejecutivo: {col} | Cantidad total de registros: {len(tabla_detalle)}") 

            st.dataframe(
                tabla_detalle, 
                width='stretch',
                hide_index=True,
                column_config={
                    "Tickets": st.column_config.NumberColumn("Tickets"),
                    "Equipos Involucrados": st.column_config.TextColumn("Equipos Involucrados", width="medium"),
                    "Activos de SW": st.column_config.TextColumn("Activos de SW", width="medium"),
                }
            )

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                tabla_detalle.to_excel(writer, index=False, sheet_name='Base')
            
            st.download_button(
                label="Descargar Excel",
                data=buffer.getvalue(),
                file_name=f"Volumen_{col}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )