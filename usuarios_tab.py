import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db.init_db import DB_PATH

class UsuariosTab:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Usuarios")

        # Crear el frame principal
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        # Tabla para mostrar usuarios
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Rol"), show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.ordenar_por_columna("ID", False, self.tree))
        self.tree.heading("Nombre", text="Nombre", command=lambda: self.ordenar_por_columna("Nombre", False, self.tree))
        self.tree.heading("Rol", text="Rol", command=lambda: self.ordenar_por_columna("Rol", False, self.tree))
        self.tree.pack(fill="both", expand=True, pady=10)

        # Frame para los campos de entrada y botón
        entry_frame = ttk.Frame(self.frame)
        entry_frame.pack(pady=10)

        # Etiqueta y campo de entrada para el nombre del usuario
        ttk.Label(entry_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2)
        self.nombre_entry = ttk.Entry(entry_frame)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=2)

        # Etiqueta y campo de entrada para el rol del usuario
        ttk.Label(entry_frame, text="Rol:").grid(row=1, column=0, padx=5, pady=2)
        self.rol_entry = ttk.Entry(entry_frame)
        self.rol_entry.grid(row=1, column=1, padx=5, pady=2)

        # Botón para agregar un nuevo usuario
        ttk.Button(entry_frame, text="Agregar", command=self.agregar_usuario).grid(row=2, column=0, columnspan=2, pady=5)

        # Cargar los usuarios existentes desde la base de datos
        self.cargar_usuarios()

    def cargar_usuarios(self):
        """Carga los usuarios desde la base de datos y los muestra en el Treeview."""
        self.tree.delete(*self.tree.get_children())  # Limpiar el Treeview actual
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, rol FROM Usuarios")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)  # Insertar cada usuario en la tabla
        conn.close()
    
    def ordenar_por_columna(self, col, descendente, tree=None):
        """Ordena el contenido del Treeview por la columna seleccionada"""
        tree = tree or self.tree

        datos = [(tree.set(k, col), k) for k in tree.get_children('')]

        try:
            datos.sort(key=lambda t: int(t[0]), reverse=descendente)
        except ValueError:
            datos.sort(key=lambda t: t[0], reverse=descendente)

        for index, (val, k) in enumerate(datos):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.ordenar_por_columna(col, not descendente, tree))

    def agregar_usuario(self):
        """Agrega un nuevo usuario a la base de datos desde los campos de entrada."""
        nombre = self.nombre_entry.get().strip()
        rol = self.rol_entry.get().strip()

        # Validar que ambos campos estén completos
        if not nombre or not rol:
            messagebox.showwarning("Atención", "Completa ambos campos.")
            return

        # Insertar el nuevo usuario en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Usuarios (nombre, rol) VALUES (?, ?)", (nombre, rol))
        conn.commit()
        conn.close()

        # Limpiar los campos de entrada y recargar los datos en la tabla
        self.nombre_entry.delete(0, tk.END)
        self.rol_entry.delete(0, tk.END)
        self.cargar_usuarios()
