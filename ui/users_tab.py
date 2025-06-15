import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = "db/incidentes.db"

class UsuariosTab(tk.Frame):
    def __init__(self, parent, main_app=None):
        super().__init__(parent)
        self.main_app = main_app

        self.roles_list = [
            'Administrador', 'Supervisor', 'Tecnico', 'Jefe', 'Analista', 'Auditor'
        ]

        # Widgets de entrada
        tk.Label(self, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_nombre = tk.Entry(self)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Rol:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_rol = ttk.Combobox(self, values=self.roles_list, state="readonly")
        self.combo_rol.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(self, text="Agregar Usuario", command=self.agregar_usuario)\
            .grid(row=0, column=4, padx=5, pady=5)

        # Tabla de usuarios
        self.tree_usuarios = ttk.Treeview(self, columns=("id", "nombre", "rol"), show="headings")
        self.tree_usuarios.heading("id", text="ID")
        self.tree_usuarios.heading("nombre", text="Nombre")
        self.tree_usuarios.heading("rol", text="Rol")
        self.tree_usuarios.column("id", width=50, anchor="center")
        self.tree_usuarios.column("nombre", width=200, anchor="w")
        self.tree_usuarios.column("rol", width=150, anchor="center")
        self.tree_usuarios.grid(row=1, column=0, columnspan=5, sticky="nsew", padx=5, pady=5)

        # Expansión de la tabla
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(4, weight=1)

        self.cargar_usuarios()

    def cargar_usuarios(self):
        for row in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(row)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, nombre, rol FROM Usuario ORDER BY id_usuario")
            for usuario in cursor.fetchall():
                self.tree_usuarios.insert("", tk.END, values=usuario)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
        finally:
            conn.close()

    def agregar_usuario(self):
        nombre = self.entry_nombre.get().strip()
        rol = self.combo_rol.get()

        if not nombre or not rol:
            messagebox.showwarning("Atención", "Debes completar todos los campos.")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Verificar si ya existe un usuario con ese nombre
            cursor.execute("SELECT COUNT(*) FROM Usuario WHERE LOWER(nombre) = LOWER(?)", (nombre,))
            if cursor.fetchone()[0] > 0:
                messagebox.showwarning("Duplicado", "Ya existe un usuario con ese nombre.")
                return

            cursor.execute("INSERT INTO Usuario (nombre, rol) VALUES (?, ?)", (nombre, rol))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agregar el usuario: {e}")
        finally:
            conn.close()

        self.entry_nombre.delete(0, tk.END)
        self.combo_rol.set("")
        self.cargar_usuarios()

        # Si hay una pestaña de incidentes, actualizar combobox
        if self.main_app and hasattr(self.main_app, "incidentes_tab"):
            self.main_app.incidentes_tab.cargar_combobox_incidentes()
