# Sistema de Gestión de Incidentes de Ciberseguridad

Este sistema permite registrar, visualizar, editar y reportar incidentes de ciberseguridad. La aplicación cuenta con una interfaz gráfica desarrollada en **Tkinter** y utiliza **SQLite** como base de datos relacional.

## 📌 Funcionalidades principales

- Registro de nuevos incidentes
- Edición de incidentes existentes (estado, descripción, gravedad)
- Visualización de incidentes en diferentes formatos:
  - Tabular
  - Resumen / Agregado
  - Detallado
  - Comparativo por tipo y estado
- Uso de roles de usuario (Administrador, Técnico, Analista, etc.)
- Listado de incidentes filtrado por tipo o estado

## 🛠️ Tecnologías utilizadas

- Python 3
- Tkinter (interfaz gráfica)
- SQLite3 (base de datos)
- `ttk` para componentes visuales estilizados

## ▶️ Cómo ejecutar el sistema

1. Asegúrate de tener Python 3 instalado.
2. Clona el repositorio o descarga los archivos.
3. Ejecuta el archivo principal desde la terminal:

python main.py
La base de datos se crea automáticamente al iniciar la aplicación si no existe.

📊 Reportes disponibles

Tabular: Lista de todos los incidentes con tipo, estado, usuario, fecha y gravedad.
Resumen: Agrupado por nivel de gravedad y tipo de incidente.
Detallado: Muestra todos los datos de un incidente individual.
Comparativo: Relación entre tipo de incidente y su estado actual.

✏️ Personalización
Puedes modificar o agregar tipos de incidentes, estados y usuarios editando el archivo db/init_db.py.

## 👨‍💻 Autor
- Desarrollado por: Rafael Lacuesta, Adrian Chiriff
- Materia: Introducción a las Bases de Datos
- Año: 2025

## 📂 Estructura del proyecto

```text
📁 proyecto/
│
├── db/
│   └── init_db.py            # Script de creación e inicialización de la base de datos
│
├── ui/
│   ├── incidentes_tab.py     # Pestaña de gestión de incidentes
│   ├── users_tab.py          # Pestaña de gestión de usuarios
│   └── reportes_tab.py       # Pestaña para generación de reportes
│
├── main.py                   # Archivo principal para ejecutar la aplicación
└── README.md                 # Este archivo


