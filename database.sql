-- Tabla de Roles
CREATE TABLE roles (
    id_rol INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL
);

-- Tabla de Usuarios
CREATE TABLE Usuario (
    id_usuario INTEGER PRIMARY KEY ,
    nombre TEXT NOT NULL,
    id_rol INTEGER NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- Tabla de Tipos de Incidente
CREATE TABLE TipoIncidente (
    id_tipo INTEGER PRIMARY KEY ,
    nombre_tipo TEXT NOT NULL
);

-- Tabla de Estados
CREATE TABLE Estado (
    id_estado INTEGER PRIMARY KEY,
    nombre_estado TEXT NOT NULL
);

-- Tabla de Incidentes
CREATE TABLE Incidente (
    id_incidente INTEGER PRIMARY KEY,
    id_tipo INTEGER NOT NULL,
    id_estado INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    descripcion TEXT,
    fecha TEXT,
    gravedad TEXT,
    FOREIGN KEY (id_tipo) REFERENCES TipoIncidente(id_tipo),
    FOREIGN KEY (id_estado) REFERENCES Estado(id_estado),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);
