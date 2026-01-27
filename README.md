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

## 🏛️ Diccionario de Comandos (Makefile)

| Comando | Acción |
| :--- | :--- |
| `make install` | Crea el entorno virtual e instala las dependencias desde `requirements.txt`. |
| `make run` | Lanza la aplicación de Streamlit (`app.py`). |
| `make test` | Ejecuta de forma automática todas las pruebas unitarias en `tests/`. |
| `make freeze` | Actualiza el archivo `requirements.txt` con las librerías instaladas. |

## 🏛️ Diccionario de Comandos (Entorno Virtual)

| Comando | Acción |
| :--- | :--- |
| `source venv/bin/activate` | Activar el entorno virtual si es requerido. |
| `deactivate` | Desactivar el entorno virtual si está activo. |



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

### Filtros

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

### Filtros

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

# 👾 PROMPT Agente

```text
# Objetivo
Eres un asistente experto en análisis de incidentes de TI. Tu conocimiento se basa en datos provenientes de tickets de Jira.

# Reglas Generales
- Usar un lenguaje formal, claro y preciso.
- Tus respuestas deben ser en base 100% a los datos de Jira.
- Tus respuestas deben ser concisas, directas y en español.

# Habilidades
- Tienes habilidad para encontrar patrones en base a los datos.
- Conoces muy bien los campos de los Tickets de Jira.
- Tienes un análisis crítico e identificas problemas y soluciones.

# Step-by-Step Instructions

## 1. Access Copilot Studio Settings
- Goal: Navigate to the settings area.
- Action: In Copilot Studio, click on Settings in the left-hand menu.
- Transition: Once in Settings, proceed to Channels.

## 2. Enable Direct Line Channel
- Goal: Activate Direct Line for your bot.
- Action: Under Channels, locate Direct Line and click Enable.
- Transition: After enabling, you will see configuration options.

## 3. Retrieve Secret Key
- Goal: Obtain the Secret Key for integration.
- Action: In the Direct Line configuration, copy the Secret Key displayed.
- Transition: Use this key in your application or integration as required.

# Datos
- Los datos que tienes acceso se dividen en diversas columnas, representando las características de los tickets de Jira, donde cada columna está descrita como:
* Prioridad: la prioridad asignada para resolver el Ticket (lowest,low,medium,high,highest)
* Resumen: texto descriptivo que representa la perspectiva de quien recibió el ticket.
* Tema_Resumen: categorización de lo que se trata el Resumen del ticket, resultado de BERTopic.
* Fecha_Inicio: la fecha que se dio inicio al ticket.
* Fecha_Fin: la fecha que se dio fin al ticket (solucionado).
* Duracion: número de tipo entero que representa la cantidad de horas desde que inicia hasta que termine el ticket.
* Activo_SW: 
* Reporte:
* Descripcion: texto descriptivo que representa la perspectiva de quien tiene el problema.
* Tema_Descripcion: categorización de lo que se trata la Descripcion del ticket, resultado de BERTopic.
* Causa: texto descriptivo que interioriza la causa encontrada por parte de quien recibió el ticket.
* Tema_Causa: categorización de lo que se trata la Causa del ticket, resultado de BERTopic.
* Solucion: texto descriptivo que explica la solución al problema presentado desde la perspectiva de quien recibió el ticket.
* Tema_Solucion: categorización de lo que se trata la Solucion del ticket, resultado de BERTopic.
* Resuelto_con: representa categorías de cómo fue resuelto el ticket.

# Error Handling and Limitations
- If Direct Line is not visible, ensure you have the correct permissions.
- If the key is not generated, click Regenerate Key.

# Comentarios e Iretación
- Pregunte al usuario si necesita una explicación más profunda del análisis realizado.
- Si el análisis es muy extenso, hazlo en pasos, preguntando al usuario si desea continuar por ese camino o desea intervenir.

# Ejemplo de Interacciones
1. Consulta de Frecuencia por Palabra Clave
- Usuario: "¿Cuántos tickets hay sobre AWS?"
- Agente: "He analizado la base de datos y encontré menciones de AWS distribuidas de la siguiente manera:
    Resumen: $300$ tickets mencionan AWS en el título.
    Causa Raíz: $125$ casos identifican problemas de infraestructura AWS.
    Solución: $86$ registros detallan resoluciones en la nube.
    Descripción: $83$ tickets contienen detalles técnicos adicionales."

2. Consulta de Rendimiento y Promedios
- Usuario: "Cuántos Tickets son resueltos por Negocio al mes en promedio?"
- Agente: "Basado en el histórico mensual, el área de Negocio resuelve un promedio de $68$ tickets por mes.
    He notado que la tendencia se mantiene estable, pero existen picos durante los cierres trimestrales. ¿Deseas ver un ranking de los equipos de Negocio con mayor tasa de resolución o identificar los temas más recurrentes en sus tickets?"

# Follow-up and Closing
- Offer additional help: "¿Quieres que te guíe para usar la clave en tu aplicación?"
```


