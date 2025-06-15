import sqlite3
import os

DB_PATH = "db/incidentes.db"

def init_db_if_needed():
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Tabla Usuario con atributo enumerado 'rol'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id_usuario INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (rol IN ('Administrador', 'Supervisor', 'Tecnico', 'Jefe', 'Analista', 'Auditor'))
        )
    """)

    # Tabla Incidente con tipo, estado y gravedad como atributos enumerados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Incidente (
            id_incidente INTEGER PRIMARY KEY,
            tipo TEXT NOT NULL CHECK (tipo IN (
                'Phishing', 'Malware', 'Acceso no autorizado', 'Ransomware', 'Ingeniería social',
                'Fuga de datos', 'Ataque de denegación de servicio (DDoS)', 'Suplantación de identidad',
                'Explotación de vulnerabilidades', 'Uso indebido de credenciales', 'Ataque interno (Insider Threat)',
                'Acceso físico no autorizado', 'Pérdida o robo de dispositivo', 'Intrusión en red',
                'Modificación no autorizada de archivos'
            )),
            estado TEXT NOT NULL CHECK (estado IN ('Abierto', 'En Proceso', 'Cerrado', 'Cancelado')),
            id_usuario INTEGER NOT NULL,
            descripcion TEXT,
            fecha TEXT,
            gravedad TEXT CHECK (gravedad IN ('Alta', 'Media', 'Baja')),
            FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario) ON DELETE RESTRICT
        )
    """)

    # Insertar usuarios si no existen
    cursor.execute("SELECT COUNT(*) FROM Usuario")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO Usuario (nombre, rol) VALUES (?, ?)", [
            ('Rafael Lacuesta', 'Analista'),
            ('Sofía Méndez', 'Tecnico'),
            ('Carlos Marquez', 'Supervisor'),
            ('Lucía Fernández', 'Auditor'),
            ('Jorge Morales', 'Administrador')
        ])

    # Insertar algunos incidentes de ejemplo si no existen
    cursor.execute("SELECT COUNT(*) FROM Incidente")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Incidente (tipo, estado, id_usuario, descripcion, fecha, gravedad)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ('Phishing', 'Abierto', 1, 'Correo sospechoso recibido por un empleado.', '2025-05-01', 'Alta'),
            ('Malware', 'En Proceso', 2, 'Detección de software malicioso en una estación de trabajo.', '2025-05-02', 'Media'),
            ('Acceso no autorizado', 'Cerrado', 3, 'Intento de acceso fuera de horario detectado.', '2025-05-03', 'Alta'),
            ('Ransomware', 'Cancelado', 4, 'Simulación de ataque cancelada.', '2025-05-04', 'Baja'),
            ('Fuga de datos', 'Abierto', 5, 'Posible filtración de información confidencial.', '2025-05-05', 'Alta')
        ])

    conn.commit()
    conn.close()
