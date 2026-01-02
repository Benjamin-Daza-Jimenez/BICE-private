# BICE-private

## Comandos

make install -> Instala todo lo necesario desde tu requirements.txt.

make run -> Lanza aplicación de Streamlit (app).

make test -> Ejecuta todas las pruebas en la carpeta tests/

make freeze -> Actualiza lista de librerías si se instalastó algo nuevo.

## Jerarquía

```text
BICE-Private
├── project/                # Código fuente y entorno de ejecución
│   ├── data/               # Almacena archivos Excel que se manejan
│   ├── func/               # Archivos con la lógica
│   ├── reports/            # Almacena gráficos generados
│   ├── tests/              # Pruebas unitarias
│   ├── venv/               # Entorno virtual
│   ├── app.py              # Interfaz de usuario (Streamlit)
│   ├── Makefile            # Comandos de automatización
│   └── requirements.txt    # Librerías necesarias para el proyecto
├── .gitignore
└── README.md
```


