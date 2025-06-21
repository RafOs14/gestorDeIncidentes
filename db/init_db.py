import sqlite3
import os

DB_PATH = "db/incidentes.db"

def init_db_if_needed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Crear tabla Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            rol TEXT NOT NULL
        )
    """)

    # Crear tabla Tipos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tipos (
            id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            gravedad TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
    """)

    # Crear tabla Incidentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Incidentes (
            id_incidente INTEGER PRIMARY KEY AUTOINCREMENT,
            id_tipo INTEGER NOT NULL,
            FOREIGN KEY (id_tipo) REFERENCES Tipos(id_tipo)
        )
    """)

    # Crear tabla Cargan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cargan (
            id_usuario INTEGER,
            id_incidente INTEGER,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            PRIMARY KEY (id_usuario, id_incidente),
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
            FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente)
        )
    """)

    # Crear tabla Estado
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Estado (
            id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    # Crear tabla Genera
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genera (
            id_incidente INTEGER,
            id_estado INTEGER,
            id_usuario INTEGER,
            fecha TEXT,
            PRIMARY KEY (id_incidente, id_estado, id_usuario, fecha),
            FOREIGN KEY (id_incidente) REFERENCES Incidentes(id_incidente),
            FOREIGN KEY (id_estado) REFERENCES Estado(id_estado),
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
        )
    """)

    # Insertar estados por defecto si no existen
    estados_defecto = ["Pendiente", "En progreso", "Resuelto", "Cerrado"]
    for estado in estados_defecto:
        cursor.execute("INSERT OR IGNORE INTO Estado (nombre) VALUES (?)", (estado,))

    # Insertar usuario admin si no existe
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Usuarios (nombre, rol) VALUES (?, ?)", ("admin", "Administrador"))

    # Insertar algunos tipos de incidente si no existen
    cursor.execute("SELECT COUNT(*) FROM Tipos")
    if cursor.fetchone()[0] == 0:
        tipos = [
            ("Falla eléctrica", "Alta", "Corte o sobrecarga de energía"),
            ("Problema de red", "Media", "Conectividad intermitente o caída total"),
            ("Error de software", "Baja", "Bug en el sistema reportado por el usuario")
        ]
        cursor.executemany("INSERT INTO Tipos (tipo, gravedad, descripcion) VALUES (?, ?, ?)", tipos)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db_if_needed()
    print("Base de datos inicializada con valores por defecto.")
