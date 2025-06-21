import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db.init_db import DB_PATH

class UsuariosTab:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Usuarios")
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Rol"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Rol", text="Rol")
        self.tree.pack(fill="both", expand=True, pady=10)

        entry_frame = ttk.Frame(self.frame)
        entry_frame.pack(pady=10)

        # Etiqueta y entrada para Nombre
        ttk.Label(entry_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=2)
        self.nombre_entry = ttk.Entry(entry_frame)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=2)

        # Etiqueta y entrada para Rol
        ttk.Label(entry_frame, text="Rol:").grid(row=1, column=0, padx=5, pady=2)
        self.rol_entry = ttk.Entry(entry_frame)
        self.rol_entry.grid(row=1, column=1, padx=5, pady=2)

        # Botón Agregar
        ttk.Button(entry_frame, text="Agregar", command=self.agregar_usuario).grid(row=2, column=0, columnspan=2, pady=5)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, rol FROM Usuarios")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def agregar_usuario(self):
        nombre = self.nombre_entry.get().strip()
        rol = self.rol_entry.get().strip()

        if not nombre or not rol:
            messagebox.showwarning("Atención", "Completa ambos campos.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Usuarios (nombre, rol) VALUES (?, ?)", (nombre, rol))
        conn.commit()
        conn.close()

        self.nombre_entry.delete(0, tk.END)
        self.rol_entry.delete(0, tk.END)
        self.cargar_usuarios()
