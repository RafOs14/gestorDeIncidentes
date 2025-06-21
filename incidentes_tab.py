
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from db.init_db import DB_PATH

class IncidentesTab:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Incidentes")
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Tipo", "Gravedad", "Descripción", "Usuario", "Estado"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, pady=10)

        form_frame = ttk.Frame(self.frame)
        form_frame.pack(pady=10)

        # Tipo
        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0)
        self.tipo_cb = ttk.Combobox(form_frame, state="readonly")
        self.tipo_cb.grid(row=0, column=1, padx=5)
        self.tipo_cb.bind("<<ComboboxSelected>>", self.actualizar_info_tipo)

        # Gravedad (readonly)
        ttk.Label(form_frame, text="Gravedad:").grid(row=1, column=0)
        self.gravedad_var = tk.StringVar()
        self.gravedad_entry = ttk.Entry(form_frame, textvariable=self.gravedad_var, state="readonly")
        self.gravedad_entry.grid(row=1, column=1, padx=5)

        # Descripción (readonly)
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0)
        self.descripcion_var = tk.StringVar()
        self.descripcion_entry = ttk.Entry(form_frame, textvariable=self.descripcion_var, state="readonly")
        self.descripcion_entry.grid(row=2, column=1, padx=5)

        # Usuario
        ttk.Label(form_frame, text="Usuario:").grid(row=3, column=0)
        self.usuario_cb = ttk.Combobox(form_frame, state="readonly")
        self.usuario_cb.grid(row=3, column=1, padx=5)

        # Estado
        ttk.Label(form_frame, text="Estado:").grid(row=4, column=0)
        self.estado_cb = ttk.Combobox(form_frame, state="readonly")
        self.estado_cb.grid(row=4, column=1, padx=5)

        # Botón
        ttk.Button(form_frame, text="Registrar Incidente", command=self.agregar_incidente).grid(row=5, column=0, columnspan=2, pady=10)

        self.tipos = {}
        self.usuarios = {}
        self.estados = {}

        self.cargar_desplegables()
        self.cargar_incidentes()

    def cargar_desplegables(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Tipos
        cursor.execute("SELECT id_tipo, tipo, gravedad, descripcion FROM Tipos")
        self.tipos = {tipo: (id_tipo, gravedad, descripcion) for id_tipo, tipo, gravedad, descripcion in cursor.fetchall()}
        self.tipo_cb["values"] = list(self.tipos.keys())

        # Usuarios
        cursor.execute("SELECT id_usuario, nombre FROM Usuarios")
        self.usuarios = {nombre: id_usuario for id_usuario, nombre in cursor.fetchall()}
        self.usuario_cb["values"] = list(self.usuarios.keys())

        # Estados
        cursor.execute("SELECT id_estado, nombre FROM Estado")
        self.estados = {nombre: id_estado for id_estado, nombre in cursor.fetchall()}
        self.estado_cb["values"] = list(self.estados.keys())

        conn.close()

    def actualizar_info_tipo(self, event):
        tipo = self.tipo_cb.get()
        if tipo in self.tipos:
            _, gravedad, descripcion = self.tipos[tipo]
            self.gravedad_var.set(gravedad)
            self.descripcion_var.set(descripcion)

    def cargar_incidentes(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, t.tipo, t.gravedad, t.descripcion, u.nombre, e.nombre
            FROM Incidentes i
            JOIN Tipos t ON i.id_tipo = t.id_tipo
            JOIN Cargan c ON i.id_incidente = c.id_incidente
            JOIN Usuarios u ON c.id_usuario = u.id_usuario
            LEFT JOIN Genera g ON i.id_incidente = g.id_incidente
            LEFT JOIN Estado e ON g.id_estado = e.id_estado
            GROUP BY i.id_incidente
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def agregar_incidente(self):
        tipo = self.tipo_cb.get()
        usuario = self.usuario_cb.get()
        estado = self.estado_cb.get()

        if not (tipo and usuario and estado):
            messagebox.showwarning("Atención", "Completa todos los campos.")
            return

        id_tipo = self.tipos[tipo][0]
        id_usuario = self.usuarios[usuario]
        id_estado = self.estados[estado]
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Insertar incidente
        cursor.execute("INSERT INTO Incidentes (id_tipo) VALUES (?)", (id_tipo,))
        id_incidente = cursor.lastrowid

        # Insertar en Cargan
        cursor.execute("INSERT INTO Cargan (id_usuario, id_incidente, fecha_inicio) VALUES (?, ?, ?)",
                       (id_usuario, id_incidente, fecha_actual))

        # Insertar en Genera
        cursor.execute("INSERT INTO Genera (id_incidente, id_estado, id_usuario, fecha) VALUES (?, ?, ?, ?)",
                       (id_incidente, id_estado, id_usuario, fecha_actual))

        conn.commit()
        conn.close()

        self.tipo_cb.set("")
        self.usuario_cb.set("")
        self.estado_cb.set("")
        self.gravedad_var.set("")
        self.descripcion_var.set("")
        self.cargar_incidentes()
