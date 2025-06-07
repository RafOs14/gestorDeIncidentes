# Importamos las librerias, y el archivo con la base de datos
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from db.init_db import DB_PATH

class UsuariosTab: #Definimos la clase usuario y la ventana
    def __init__(self, frame, main_app):
        self.frame = frame
        self.main_app = main_app
        self.roles = {}  # id_rol: descripcion
        self.build_users_tab()

    def build_users_tab(self):
        # Campo de texto para cargar el nombre del usuario
        ttk.Label(self.frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_nombre = ttk.Entry(self.frame)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Select con los roles existentes en la base de datos
        ttk.Label(self.frame, text="Rol:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.combo_rol = ttk.Combobox(self.frame, state="readonly")
        self.combo_rol.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Frame para contener y centrar los botones
        boton_frame = ttk.Frame(self.frame)
        boton_frame.grid(row=2, column=0, columnspan=2, pady=10)

        btn_agregar = ttk.Button(boton_frame, text="Agregar Usuario", command=self.agregar_usuario)
        btn_agregar.pack(pady=5)

        btn_eliminar = ttk.Button(boton_frame, text="Eliminar Usuario", command=self.eliminar_usuario)
        btn_eliminar.pack(pady=5)

        # Tabla para mostrar los usuarios existentes
        self.tree_usuarios = ttk.Treeview(self.frame, columns=("ID", "Nombre", "Rol"), show="headings")
        for col in self.tree_usuarios["columns"]:
            self.tree_usuarios.heading(col, text=col)
        self.tree_usuarios.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)

        # Expandir
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # Cargamos los roles y los usuarios llamando a las funciones correspondientes
        self.cargar_roles()
        self.cargar_usuarios()

    #Funcion para cargar roles
    def cargar_roles(self):
        self.roles = {}
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_rol, descripcion FROM roles")
        for id_rol, desc in cursor.fetchall():
            self.roles[desc] = id_rol 
        conn.close()
        self.combo_rol['values'] = list(self.roles.keys())

    #Funcion para cargar usuarios
    def cargar_usuarios(self):
        for row in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, r.descripcion 
            FROM Usuario u
            JOIN roles r ON u.id_rol = r.id_rol
        """)
        for usuario in cursor.fetchall():
            self.tree_usuarios.insert("", tk.END, values=usuario)
        conn.close()

    # Funcion para agregar usuarios a la base
    def agregar_usuario(self):
        nombre = self.entry_nombre.get()
        rol_desc = self.combo_rol.get()

        if not (nombre and rol_desc):
            messagebox.showwarning("Atención", "Debes completar todos los campos")
            return

        id_rol = self.roles.get(rol_desc)
        if not id_rol:
            messagebox.showerror("Error", "Rol seleccionado no es válido.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Usuario (nombre, id_rol) VALUES (?, ?)", (nombre, id_rol))
        conn.commit()
        conn.close()

        self.entry_nombre.delete(0, tk.END)
        self.combo_rol.set("")
        self.cargar_usuarios()
        
    # Actualizar combo de usuarios en Incidentes
        if self.main_app.incidentes_tab:
            self.main_app.incidentes_tab.cargar_combobox_incidentes()
    
    def eliminar_usuario(self):
        selected_item = self.tree_usuarios.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Debes seleccionar un usuario para eliminar.")
            return

        user_id = self.tree_usuarios.item(selected_item, "values")[0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar si el usuario tiene incidentes asociados
        cursor.execute("SELECT COUNT(*) FROM incidenteHistorico WHERE id_usuario = ?", (user_id,))
        incidentes_asociados = cursor.fetchone()[0]

        if incidentes_asociados > 0:
            messagebox.showerror("Error", "No se puede eliminar el usuario porque tiene incidentes asociados.")
            conn.close()
            return

        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar este usuario?")
        if not confirm:
            conn.close()
            return

        try:
            cursor.execute("DELETE FROM Usuario WHERE id_usuario = ?", (user_id,))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el usuario: {e}")
        finally:
            conn.close()

        self.cargar_usuarios()

    # Actualizar combo de usuarios en Incidentes
        if self.main_app.incidentes_tab:
            self.main_app.incidentes_tab.cargar_combobox_incidentes()
