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

    # Crear tabla Incidentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Incidentes (
            id_incidente INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            gravedad TEXT NOT NULL,
            descripcion TEXT NOT NULL
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
    estados_defecto = ["Nuevo", "Pendiente", "En progreso", "Resuelto", "Cerrado"]
    for estado in estados_defecto:
        cursor.execute("INSERT OR IGNORE INTO Estado (nombre) VALUES (?)", (estado,))

    # Insertar usuarios por defecto si no existen
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios = [
            ("admin", "Administrador"),
            ("Rafael Lacuesta", "Supervisor"),
            ("Adrian Chiriff", "Supervisor"),
            ("Carlos Lopez", "Supervisor"),
            ("Juan Perez", "Analista"),
            ("Maria Gomez", "Analista"),
            ("Laura Martinez", "Jefe"),
            ("Luis Fernandez", "Jefe"),
            ("Ana Torres", "Tecnico"),
            ("Pedro Sanchez", "Tecnico")            
        ]
        cursor.executemany("INSERT INTO Usuarios (nombre, rol) VALUES (?, ?)", usuarios)

    # Insertar incidentes de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM Incidentes")
    if cursor.fetchone()[0] == 0:
        incidentes = [
            ("Falla eléctrica", "Alta", "Corte o sobrecarga de energía"),
            ("Problema de red", "Media", "Conectividad intermitente o caída total"),
            ("Error de software", "Baja", "Bug en el sistema reportado por el usuario"),
            ("Fuga de datos", "Alta", "Exposición no autorizada de información sensible"),
            ("Incidente físico", "Media", "Daño o robo de hardware"),
            ("Problema de seguridad", "Alta", "Amenaza o vulnerabilidad detectada")
        ]
        cursor.executemany("INSERT INTO Incidentes (tipo, gravedad, descripcion) VALUES (?, ?, ?)", incidentes)
        conn.commit()  # Commit para obtener IDs de incidentes

        # Obtener IDs de los incidentes recién insertados
        cursor.execute("SELECT id_incidente FROM Incidentes")
        ids_incidentes = [row[0] for row in cursor.fetchall()]

        # Obtener id del usuario admin
        cursor.execute("SELECT id_usuario FROM Usuarios WHERE nombre = 'admin'")
        id_usuario_admin = cursor.fetchone()[0]

        # Obtener id del estado 'Nuevo'
        cursor.execute("SELECT id_estado FROM Estado WHERE nombre = 'Nuevo'")
        id_estado_nuevo = cursor.fetchone()[0]

        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar relaciones en Cargan y Genera para cada incidente
        for id_incidente in ids_incidentes:
            cursor.execute("""
                INSERT INTO Cargan (id_usuario, id_incidente, fecha_inicio)
                VALUES (?, ?, ?)
            """, (id_usuario_admin, id_incidente, fecha_actual))

            cursor.execute("""
                INSERT INTO Genera (id_incidente, id_estado, id_usuario, fecha)
                VALUES (?, ?, ?, ?)
            """, (id_incidente, id_estado_nuevo, id_usuario_admin, fecha_actual))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db_if_needed()
    print("Base de datos inicializada con valores por defecto y relaciones creadas.")
