import func.data as data
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

MESES = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}

def anual(df):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    rutas_graficos = []

    # Agrupar por año y mes, calculando la mediana de duración y el conteo de tickets
    stats = df.groupby(['Año', 'Mes'])['Duracion'].agg(['median', 'count']).reset_index()
    stats.columns = ['Año', 'Mes', 'Mediana_Duracion', 'Volumen_Tickets']
    
    # Calcular el porcentaje del volumen de tickets por mes respecto al total anual
    stats['Total_anual'] = stats.groupby('Año')['Volumen_Tickets'].transform('sum')
    stats['Porcentaje_Volumen'] = (stats['Volumen_Tickets'] / stats['Total_anual']) * 100
    stats.drop(columns=['Total_anual'], inplace=True)

    # Formatear los resultados para mejor legibilidad
    stats['Mediana_Duracion'] = stats['Mediana_Duracion'].round(2)
    stats['Porcentaje_Volumen'] = stats['Porcentaje_Volumen'].round(2)
    
    años = stats['Año'].unique()

    color_vol = '#f39c12' 
    color_med = '#27ae60'

    for anio in años:
        df_anio = stats[stats['Año'] == anio].sort_values('Mes').copy()
        
        fig, ax1 = plt.subplots(figsize=(16, 8))
        ax2 = ax1.twinx() 
        
        x = np.arange(len(df_anio['Mes']))
        width = 0.38
        
        rects1 = ax1.bar(x - width/2, df_anio['Volumen_Tickets'], width, 
                        label='Volumen Tickets', color=color_vol, alpha=0.85)
        
        rects2 = ax2.bar(x + width/2, df_anio['Mediana_Duracion'], width, 
                        label='Mediana Duración (h)', color=color_med, alpha=0.85)
        
        etiquetas_reales = [MESES[m] for m in df_anio['Mes']]
        ax1.set_xticks(x)
        ax1.set_xticklabels(etiquetas_reales)
        
        ax1.set_ylim(0, df_anio['Volumen_Tickets'].max() * 1.25)
        ax2.set_ylim(0, df_anio['Mediana_Duracion'].max() * 1.25)
        
        # Configuración de Ejes
        ax1.set_ylabel('Cantidad de Tickets (Volumen)', color=color_vol, fontsize=12, fontweight='bold')
        ax2.set_ylabel('Mediana Duración (Horas)', color=color_med, fontsize=12, fontweight='bold')
        
        # --- ETIQUETAS ---
        for i, rect in enumerate(rects1):
            height = rect.get_height()
            pct = df_anio.iloc[i]['Porcentaje_Volumen']
            ax1.annotate(f'{int(height)}\n{pct}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 8),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold', color='#d35400')

        for rect in rects2:
            height = rect.get_height()
            ax2.annotate(f'{height}h',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 8), 
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e8449')

        plt.title(f'Gobernanza de TI BICE - Carga y Eficiencia {anio}', fontsize=16, pad=35, fontweight='bold')
        plt.grid(axis='y', linestyle='--', alpha=0.2)
        
        # Leyenda unificada
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        plt.tight_layout()

        ruta = f'reports/anual_analysis_{anio}.png'
        plt.savefig(ruta)
        rutas_graficos.append(ruta)
        plt.close()

        print(f'Análisis anual {anio} guardado.')

    return rutas_graficos

def mensual(df):
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    rutas_graficos = []

    años = df['Año'].unique()
    colors = ["#ecfaef", "#99ebac", "#efe057", "#e5b115", "#d24a00"]
    paleta = LinearSegmentedColormap.from_list("custom_palette", colors)
    for anio in años:
        df_anio = df[df['Año'] == anio]

        pivot_volume = df_anio.pivot_table(index='Día', columns='Mes', values='Duracion', aggfunc='count')
        pivot_duration = df_anio.pivot_table(index='Día', columns='Mes', values='Duracion', aggfunc='median').round(2)

        plt.figure(figsize=(18, 10))


        ax = sns.heatmap(pivot_volume, 
                annot=pivot_duration, 
                fmt='.2f', 
                cmap=paleta, 
                linewidths=.5,
                annot_kws={"size": 8},
                cbar_kws={'label': 'Intensidad del Color: Cantidad de Tickets (Volumen)'})
        
        ax.invert_yaxis()
        
        meses_presentes = [MESES[int(m)] for m in pivot_volume.columns]
        plt.xticks(ticks=np.arange(len(meses_presentes)) + 0.5, labels=meses_presentes, rotation=0)

        plt.title(f'BICE {anio}: Mapa de Calor Operativo\n(Color: Volumen de Tickets | Texto: Mediana Duración h)', fontsize=16, pad=25, fontweight='bold')
        plt.xlabel('Mes', fontsize=12, fontweight='bold')
        plt.ylabel('Día del Mes', fontsize=12, fontweight='bold')

        ruta = f'reports/mensual_analysis_{anio}.png'
        plt.savefig(ruta)
        rutas_graficos.append(ruta)
        plt.close()

        print(f'Análisis mensual {anio} guardado.')
        
    return rutas_graficos

def temporal_app(df_original):
    # Crear un nuevo DataFrame solo con las columnas de fecha
    df = df_original[['Fecha_Inicio', 'Duracion']].copy()

    # Limpiar el DataFrame
    df = data.clean(df, ['Fecha_Inicio', 'Duracion'], 'Fecha_Inicio')

    # Extraer características temporales
    df['Año'] = df['Fecha_Inicio'].dt.year 
    df['Mes'] = df['Fecha_Inicio'].dt.month
    df['Día'] = df['Fecha_Inicio'].dt.day
    df['Día_Semanal'] = df['Fecha_Inicio'].dt.dayofweek + 1  # Lunes=1, Domingo=7

    df.to_excel("data/Temporal_Results.xlsx", index=False)
    return df