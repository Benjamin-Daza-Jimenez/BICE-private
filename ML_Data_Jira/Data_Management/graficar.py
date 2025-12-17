import matplotlib.pyplot as plt
import seaborn as sns
import os

def grafico_box(dataframe, columna_x, columna_y, nombre, tipo='box'):
    """
    Función general para graficar la relación entre una variable y la duración.
    
    Parametros:
    - dataframe: El DF que estás usando
    - columna_x: La variable que quieres analizar (ej. 'Priority')
    - columna_y: La variable que quieres analizar en el eje Y (ej. 'Duración Incidente')
    - tipo: 'box' para ver distribución (outliers), 'bar' para promedios, 'scatter' para puntos.
    """
    # Configurar el estilo de Seaborn
    sns.set_style("whitegrid")
    
    plt.figure(figsize=(12, 7))

    # Crear el boxplot con colores
    sns.boxplot(
        data=dataframe, 
        x=columna_x, 
        y=columna_y, 
        hue=columna_x,
        palette="husl",
        legend=False,
        width=0.6,
        linewidth=2.5,
        fliersize=6
    )
    
    plt.title(f'Distribución de {columna_y} por {columna_x}', fontsize=16, fontweight='bold', pad=20)
    
    plt.xlabel(columna_x, fontsize=12, fontweight='bold')
    plt.ylabel(columna_y, fontsize=12, fontweight='bold')

    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout()
    
    ruta = os.path.join('./Graficos_Resultados', f'{nombre}.png')
    plt.savefig(ruta, dpi=300, bbox_inches='tight')
    plt.close()
