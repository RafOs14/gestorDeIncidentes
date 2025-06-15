import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from db.init_db import DB_PATH

class IncidentesTab:
    def __init__(self, parent):
        self.frame = parent
        self.crear_widgets()
        self.cargar_combobox_incidentes()
        self.cargar_incidentes()

    def crear_widgets(self):
        self.label_desc = ttk.Label(self.frame, text="Descripción:")
        self.label_desc.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_desc = ttk.Entry(self.frame, width=50)
        self.entry_desc.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        self.label_tipo = ttk.Label(self.frame, text="Tipo:")
        self.label_tipo.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.combo_tipo = ttk.Combobox(self.frame, state="readonly", width=45)
        self.combo_tipo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.label_estado = ttk.Label(self.frame, text="Estado:")
        self.label_estado.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.combo_estado = ttk.Combobox(self.frame, state="readonly")
        self.combo_estado.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        self.label_usuario = ttk.Label(self.frame, text="Usuario:")
        self.label_usuario.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.combo_usuario = ttk.Combobox(self.frame, state="readonly")
        self.combo_usuario.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        self.label_gravedad = ttk.Label(self.frame, text="Gravedad:")
        self.label_gravedad.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.combo_gravedad = ttk.Combobox(self.frame, values=["Alta", "Media", "Baja"], state="readonly")
        self.combo_gravedad.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        btn_agregar = ttk.Button(self.frame, text="Agregar Incidente", command=self.agregar_incidente)
        btn_agregar.grid(row=5, column=0, pady=10)

        btn_actualizar = ttk.Button(self.frame, text="Actualizar Incidente", command=self.actualizar_incidente)
        btn_actualizar.grid(row=5, column=1, pady=10)

        self.tree_incidentes = ttk.Treeview(
            self.frame,
            columns=("ID", "Tipo", "Estado", "Usuario", "Descripción", "Fecha", "Gravedad"),
            show="headings"
        )
        for col in self.tree_incidentes["columns"]:
            self.tree_incidentes.heading(col, text=col)
            self.tree_incidentes.column(col, anchor="center")

        self.tree_incidentes.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)
        self.tree_incidentes.bind("<Double-1>", self.seleccionar_incidente)

        self.frame.grid_rowconfigure(6, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

    def cargar_combobox_incidentes(self):
        tipos = [
            'Phishing', 'Malware', 'Acceso no autorizado', 'Ransomware',
            'Ingeniería social', 'Fuga de datos', 'Ataque de denegación de servicio (DDoS)',
            'Suplantación de identidad', 'Explotación de vulnerabilidades',
            'Uso indebido de credenciales', 'Ataque interno (Insider Threat)',
            'Acceso físico no autorizado', 'Pérdida o robo de dispositivo',
            'Intrusión en red', 'Modificación no autorizada de archivos'
        ]
        estados = ['Abierto', 'En Proceso', 'Cerrado', 'Cancelado']

        self.combo_tipo['values'] = tipos
        self.combo_estado['values'] = estados

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre FROM Usuario")
        usuarios = cursor.fetchall()
        self.combo_usuario['values'] = [f"{u[0]} - {u[1]}" for u in usuarios]
        conn.close()

    def cargar_incidentes(self):
        for row in self.tree_incidentes.get_children():
            self.tree_incidentes.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, i.tipo, i.estado, u.nombre, i.descripcion, i.fecha, i.gravedad
            FROM Incidente i
            JOIN Usuario u ON i.id_usuario = u.id_usuario
            ORDER BY i.id_incidente ASC
        """)
        for row in cursor.fetchall():
            self.tree_incidentes.insert("", tk.END, values=row)
        conn.close()

    def agregar_incidente(self):
        desc = self.entry_desc.get()
        gravedad = self.combo_gravedad.get()
        tipo = self.combo_tipo.get()
        estado = self.combo_estado.get()
        usuario_val = self.combo_usuario.get()

        if not (desc and gravedad and tipo and estado and usuario_val):
            messagebox.showwarning("Atención", "Debes completar todos los campos")
            return

        id_usuario = int(usuario_val.split(" - ")[0])
        fecha = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Incidente(tipo, estado, id_usuario, descripcion, fecha, gravedad)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tipo, estado, id_usuario, desc, fecha, gravedad))
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, tk.END)
        self.combo_gravedad.set("")
        self.combo_tipo.set("")
        self.combo_estado.set("")
        self.combo_usuario.set("")

        self.cargar_incidentes()
        messagebox.showinfo("Éxito", "Incidente agregado correctamente")

    def seleccionar_incidente(self, event):
        selected_item = self.tree_incidentes.selection()
        if not selected_item:
            return

        values = self.tree_incidentes.item(selected_item, "values")
        self.id_incidente_actual = values[0]

        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[4])
        self.combo_gravedad.set(values[6])
        self.combo_tipo.set(values[1])
        self.combo_estado.set(values[2])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario FROM Usuario WHERE nombre = ?", (values[3],))
        row = cursor.fetchone()
        conn.close()

        self.combo_usuario.set(f"{row[0]} - {values[3]}" if row else "")

    def actualizar_incidente(self):
        if not hasattr(self, 'id_incidente_actual'):
            messagebox.showwarning("Atención", "Debes seleccionar un incidente para actualizar.")
            return

        desc = self.entry_desc.get()
        gravedad = self.combo_gravedad.get()
        tipo = self.combo_tipo.get()
        estado = self.combo_estado.get()
        usuario_val = self.combo_usuario.get()

        if not (desc and gravedad and tipo and estado and usuario_val):
            messagebox.showwarning("Atención", "Debes completar todos los campos")
            return

        id_usuario = int(usuario_val.split(" - ")[0])

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Incidente
            SET tipo = ?, estado = ?, id_usuario = ?, descripcion = ?, gravedad = ?
            WHERE id_incidente = ?
        """, (tipo, estado, id_usuario, desc, gravedad, self.id_incidente_actual))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Incidente actualizado correctamente")
        self.cargar_incidentes()

        self.entry_desc.delete(0, tk.END)
        self.combo_gravedad.set("")
        self.combo_tipo.set("")
        self.combo_estado.set("")
        self.combo_usuario.set("")
        del self.id_incidente_actual
