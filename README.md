# BICE-private | Documentación del Proyecto

Este proyecto es una aplicación desarrollada en Python 3.9+ con una interfaz en Streamlit. Utiliza un Makefile para automatizar las tareas de instalación, ejecución y pruebas.

## ⚠️ Nota Importante para Usuarios de Windows

El sistema de automatización de este proyecto utiliza make, una herramienta nativa de sistemas Unix.

* macOS / Linux: Puede ejecutar los comandos directamente en la terminal.
* Windows: No use PowerShell ni el CMD estándar. Debe utilizar una terminal WSL (Windows Subsystem for Linux) o contar con un entorno emulado como Git Bash con Make instalado para que los comandos funcionen correctamente.

## ⏱️ Requisitos Previos

Asegurarse de tener instaladas las siguientes herramientas antes de comenzar:

* Python 3.9 o superior
* Make (Herramienta de automatización)
* Pip (Gestor de paquetes de Python)
* Virtualenv (Para la gestión del entorno virtual)

## 🚀 Guía de Instalación y Uso

1. **Clonar repositorio**

    Abrir terminal y ejecutar el siguiente comando:

    ```bash
    git clone https://github.com/Benjamin-Daza-Jimenez/BICE-private.git
    cd BICE-private/project/
    ```

2. **Instalación de dependencias**

    Dentro de la carpeta project/, ejecutar el comando de instalación. Este paso creará el entorno virtual e instalará las librerías necesarias de requirements.txt.

    ```bash
    make install
    ```

3. **Ejecutar programa**

    Una vez instaladas las dependencias, lanzar la interfaz de Streamlit con:

    ```bash
    make run
    ```

## 📁 Subida de archivo Excel de Jira (Manual)

Si ocurre un error en la descarga automática o se prefiere subir el archivo manualmente, seguir estos pasos:

1. Descargar el archivo Excel desde Jira con las columnas necesarias ([Filtro: GDI Análisis para ML](https://bicevida.atlassian.net/issues/?filter=20375)).
2. Cambiar el nombre de la hoja a "Base" obligatoriamente.
3. Subir el archivo Excel en la interfaz de la aplicación cuando se solicite.

## 🏛️ Diccionario de Comandos

### Makefile

| Comando | Acción |
| :--- | :--- |
| `make install` | Crea el entorno virtual e instala las dependencias desde `requirements.txt`. |
| `make run` | Lanza la aplicación de Streamlit (`app.py`). |
| `make test` | Ejecuta de forma automática todas las pruebas unitarias en `tests/`. |
| `make freeze` | Actualiza el archivo `requirements.txt` con las librerías instaladas. |

### Entorno Virtual

| Comando | Acción |
| :--- | :--- |
| `source venv/bin/activate` | Activar el entorno virtual si es requerido. |
| `deactivate` | Desactivar el entorno virtual si está activo. |

## Contenido Archivo .env

Se debe crear un archivo .env en la carpeta project con el siguiente contenido:

```text
JIRA_EMAIL = email corporativo de quien generó el token
JIRA_API_TOKEN = token generando desde jira
JIRA_DOMAIN = bicevida.atlassian.net
```

Para generar el Token de Jira: Configuración de la cuenta > Seguridad > Crear y gestionar tokens de API > Crear token de API

## 🗂️ Estructura del Proyecto

```text
BICE-Private
├── project/                # Código fuente y entorno de ejecución
│   ├── data/               # Almacena archivos Excel que se manejan
│   ├── func/               # Archivos con la lógica
│   ├── tests/              # Pruebas unitarias
│   ├── venv/               # Entorno virtual
│   ├── app.py              # Interfaz del menú principal (Streamlit)
│   ├── management.py       # Interfaz de Gestión (Streamlit)
│   ├── operation.py        # Interfaz de Operación (Streamlit)
│   ├── Makefile            # Comandos de automatización
│   └── requirements.txt    # Librerías necesarias para el proyecto
├── .gitignore
└── README.md
```

## 💼 Funcionalidades de Gestión

### Filtros de Gestión

Se pueden incorporar múltiples filtros activos tales como:

* Prioridad: prioridad asignada al ticket (Lowest, Low, Medium, High, Highest).
* Equipo: equipo resolutor del ticket.
* Fecha_Inicio: fecha real que inicia el ticket.
* Fecha_Fin: fecha real que finaliza el ticket.
* Duracion: duración en horas desde que inicia hasta que termina el ticket.
* Activo_SW: activo de software asignado al ticket.
* Reporte: servicio reportado en el ticket.
* Resuelto_con: categoría de resolución del ticket.

### Evolución Histórica | Gráfico de barras Anual

El reporte genera una comparativa mensual mediante gráficos de doble barra, donde la primera columna indica el total de tickets gestionados y la segunda el tiempo promedio de resolución. Esta vista permite contrastar directamente la carga de trabajo contra la rapidez de respuesta de cada mes.

### Intensidad Operativa | Mapa de calor Mensual

Se genera un mapa de calor (heat map) que distribuye la carga de tickets por día y mes, utilizando una escala de colores para resaltar visualmente los periodos de mayor actividad. Esta visualización permite identificar con precisión picos de demanda estacionales y patrones críticos de saturación a lo largo del año. El número de cada recuadro identifica el tiempo medio que demora en terminar los tickets iniciados en tales días.

### Agrupación por Temas | Gráfico de Pareto

El sistema implementa categorización automática mediante modelos de IA para clasificar columnas Resumen, Descripción, Causa y Solución, cuyos resultados se presentan en un gráfico de Pareto. Esta visualización permite identificar el '80/20' de la operación, señalando el pequeño grupo de categorías que genera la gran mayoría de los tickets para priorizar estrategias de resolución.

### Concentración de Carga | Gráfico de Campana de Gauss

Se representa la distribución de la actividad diaria mediante una Campana de Gauss, visualizando la concentración del volumen de tickets a lo largo del tiempo. Este análisis permite identificar el comportamiento estándar del servicio y detectar estadísticamente desviaciones o días con una carga de trabajo fuera de lo normal.

## 🛠️ Funcionalidades de Operación

### Filtros de Operación

Se pueden incorporar múltiples filtros activos tales como:

* Prioridad: prioridad asignada al ticket (Lowest, Low, Medium, High, Highest).
* Equipo: equipo resolutor del ticket.
* Fecha_Inicio: fecha real que inicia el ticket.
* Fecha_Fin: fecha real que finaliza el ticket.
* Duracion: duración en horas desde que inicia hasta que termina el ticket.

### Ficha Histórica

Se proporciona una vista detallada del comportamiento de los Activos de Software o del Servicio Reportado, consolidando métricas clave como el promedio mensual de tickets, los equipos de soporte más frecuentes y las principales causas raíz. Esta visualización integral permite supervisar el rendimiento de cada activo y orientar las estrategias de mantenimiento preventivo basándose en datos históricos.

### Causa y Solución

Se presentan tarjetas informativas que detallan las causas raíz y soluciones aplicadas por cada Activo de Software o Servicio Reportado, integrando un análisis de palabras clave extraídas de las descripciones. Este formato permite consultar rápidamente el historial de resolución y los términos más recurrentes asociados a las fallas de cada componente.
