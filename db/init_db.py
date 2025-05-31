import sqlite3
import os

DB_PATH = "db/incidentes.db"

def init_db_if_needed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Creamos las tablas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id_rol INTEGER PRIMARY KEY,
            descripcion TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            id_rol INTEGER NOT NULL,
            FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TipoIncidente (
            id_tipo INTEGER PRIMARY KEY,
            nombre_tipo TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Estado (
            id_estado INTEGER PRIMARY KEY,
            nombre_estado TEXT NOT NULL
        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Incidente (
        id_incidente INTEGER PRIMARY KEY,
        id_tipo INTEGER,
        id_estado INTEGER,
        id_usuario INTEGER,
        descripcion TEXT,
        fecha TEXT,
        gravedad TEXT,
        FOREIGN KEY(id_tipo) REFERENCES TipoIncidente(id_tipo),
        FOREIGN KEY(id_estado) REFERENCES Estado(id_estado),
        FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario) ON DELETE RESTRICT
        )
    """)

    # Se insertan los valores a las tablas
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO roles (descripcion) VALUES (?)", [
            ('Administrador',), ('Supervisor',), ('Tecnico',), ('Jefe',), ('Analista',), ('Auditor',)
        ])

    cursor.execute("SELECT COUNT(*) FROM Usuario")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Usuario (nombre, id_rol) VALUES (?, ?)", [
            ('Rafael Lacuesta', 5),
            ('Sofía Méndez', 3),
            ('Carlos Marquez', 2),
            ('Lucía Fernández', 6),
            ('Jorge Morales', 1)
        ])

    cursor.execute("SELECT COUNT(*) FROM TipoIncidente")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO TipoIncidente (nombre_tipo) VALUES (?)", [
            ('Phishing',),
            ('Malware',),
            ('Acceso no autorizado',),
            ('Ransomware',),
            ('Ingeniería social',),
            ('Fuga de datos',),
            ('Ataque de denegación de servicio (DDoS)',),
            ('Suplantación de identidad',),
            ('Explotación de vulnerabilidades',),
            ('Uso indebido de credenciales',),
            ('Ataque interno (Insider Threat)',),
            ('Acceso físico no autorizado',),
            ('Pérdida o robo de dispositivo',),
            ('Intrusión en red',),
            ('Modificación no autorizada de archivos',)
        ])


    cursor.execute("SELECT COUNT(*) FROM Estado")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Estado (nombre_estado) VALUES (?)", [
            ('Abierto',), ('En Proceso',), ('Cerrado',), ('Cancelado',)
        ])

    conn.commit()
    conn.close()
