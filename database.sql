CREATE TABLE
IF NOT EXISTS roles
(
    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL UNIQUE
);

CREATE TABLE
IF NOT EXISTS Usuario
(
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    id_rol INTEGER NOT NULL,
    FOREIGN KEY
(id_rol) REFERENCES roles
(id_rol) ON
DELETE RESTRICT
);

CREATE TABLE
IF NOT EXISTS TipoIncidente
(
    id_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_tipo TEXT NOT NULL UNIQUE
);

CREATE TABLE
IF NOT EXISTS Estado
(
    id_estado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_estado TEXT NOT NULL UNIQUE
);

CREATE TABLE
IF NOT EXISTS Gravedad
(
    id_gravedad INTEGER PRIMARY KEY AUTOINCREMENT,
    nivel TEXT NOT NULL UNIQUE
);

CREATE TABLE
IF NOT EXISTS Incidente
(
    id_incidente INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT,
    fechaCreacion TEXT NOT NULL,
    fechaCierre TEXT
);

CREATE TABLE
IF NOT EXISTS incidenteHistorico
(
    id_hist INTEGER PRIMARY KEY AUTOINCREMENT,
    id_incidente INTEGER NOT NULL,
    id_tipo INTEGER NOT NULL,
    id_estado INTEGER NOT NULL,
    id_gravedad INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    FOREIGN KEY
(id_incidente) REFERENCES Incidente
(id_incidente),
    FOREIGN KEY
(id_tipo) REFERENCES TipoIncidente
(id_tipo),
    FOREIGN KEY
(id_estado) REFERENCES Estado
(id_estado),
    FOREIGN KEY
(id_gravedad) REFERENCES Gravedad
(id_gravedad),
    FOREIGN KEY
(id_usuario) REFERENCES Usuario
(id_usuario)
);
