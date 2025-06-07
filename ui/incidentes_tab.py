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
        self.combo_gravedad = ttk.Combobox(self.frame, state="readonly")
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id_tipo, nombre_tipo FROM TipoIncidente")
        tipos = cursor.fetchall()
        self.combo_tipo['values'] = [f"{t[0]} - {t[1]}" for t in tipos]

        cursor.execute("SELECT id_estado, nombre_estado FROM Estado")
        estados = cursor.fetchall()
        self.combo_estado['values'] = [f"{e[0]} - {e[1]}" for e in estados]

        cursor.execute("SELECT id_usuario, nombre FROM Usuario")
        usuarios = cursor.fetchall()
        self.combo_usuario['values'] = [f"{u[0]} - {u[1]}" for u in usuarios]

        cursor.execute("SELECT id_gravedad, nivel FROM Gravedad")
        gravedades = cursor.fetchall()
        self.combo_gravedad['values'] = [f"{g[0]} - {g[1]}" for g in gravedades]

        conn.close()

    def cargar_incidentes(self):
        for row in self.tree_incidentes.get_children():
            self.tree_incidentes.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, t.nombre_tipo, e.nombre_estado, u.nombre, i.descripcion, i.fechaCreacion, g.nivel
            FROM Incidente i
            JOIN incidenteHistorico h ON i.id_incidente = h.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            JOIN Estado e ON h.id_estado = e.id_estado
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Gravedad g ON h.id_gravedad = g.id_gravedad
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
            ORDER BY i.id_incidente ASC
        """)
        for row in cursor.fetchall():
            self.tree_incidentes.insert("", tk.END, values=row)
        conn.close()

    def agregar_incidente(self):
        desc = self.entry_desc.get()
        tipo_val = self.combo_tipo.get()
        estado_val = self.combo_estado.get()
        usuario_val = self.combo_usuario.get()
        gravedad_val = self.combo_gravedad.get()

        if not (desc and tipo_val and estado_val and usuario_val and gravedad_val):
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return

        id_tipo = int(tipo_val.split(" - ")[0])
        id_estado = int(estado_val.split(" - ")[0])
        id_usuario = int(usuario_val.split(" - ")[0])
        id_gravedad = int(gravedad_val.split(" - ")[0])
        fecha = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Incidente (descripcion, fechaCreacion) VALUES (?, ?)", (desc, fecha))
        id_incidente = cursor.lastrowid

        cursor.execute("""
            INSERT INTO incidenteHistorico (id_incidente, id_tipo, id_estado, id_gravedad, id_usuario, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_incidente, id_tipo, id_estado, id_gravedad, id_usuario, fecha))

        conn.commit()
        conn.close()

        self.limpiar_campos()
        self.cargar_incidentes()
        messagebox.showinfo("Éxito", "Incidente agregado correctamente.")

    def seleccionar_incidente(self, event):
        selected_item = self.tree_incidentes.selection()
        if not selected_item:
            return
        values = self.tree_incidentes.item(selected_item, "values")
        self.id_incidente_actual = values[0]
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[4])
        self.combo_tipo.set(self.buscar_id_por_valor("TipoIncidente", values[1]))
        self.combo_estado.set(self.buscar_id_por_valor("Estado", values[2]))
        self.combo_usuario.set(self.buscar_id_por_valor("Usuario", values[3]))
        self.combo_gravedad.set(self.buscar_id_por_valor("Gravedad", values[6]))

    def buscar_id_por_valor(self, tabla, valor_nombre):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if tabla == "TipoIncidente":
            id_col = "id_tipo"
            query = "SELECT id_tipo FROM TipoIncidente WHERE nombre_tipo = ?"
        elif tabla == "Estado":
            id_col = "id_estado"
            query = "SELECT id_estado FROM Estado WHERE nombre_estado = ?"
        elif tabla == "Usuario":
            id_col = "id_usuario"
            query = "SELECT id_usuario FROM Usuario WHERE nombre = ?"
        elif tabla == "Gravedad":
            id_col = "id_gravedad"
            query = "SELECT id_gravedad FROM Gravedad WHERE nivel = ?"
        else:
            conn.close()
            return ""

        cursor.execute(query, (valor_nombre,))
        row = cursor.fetchone()
        conn.close()

        if row:
            combo_attr = {
                "TipoIncidente": "combo_tipo",
                "Estado": "combo_estado",
                "Usuario": "combo_usuario",
                "Gravedad": "combo_gravedad"
            }.get(tabla)

            combo = getattr(self, combo_attr)
            for val in combo["values"]:
                if val.startswith(f"{row[0]} -"):
                    return val
        return ""

    def actualizar_incidente(self):
        if not hasattr(self, 'id_incidente_actual'):
            messagebox.showwarning("Atención", "Selecciona un incidente.")
            return

        desc = self.entry_desc.get()
        tipo_val = self.combo_tipo.get()
        estado_val = self.combo_estado.get()
        usuario_val = self.combo_usuario.get()
        gravedad_val = self.combo_gravedad.get()

        if not (desc and tipo_val and estado_val and usuario_val and gravedad_val):
            messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
            return

        id_tipo = int(tipo_val.split(" - ")[0])
        id_estado = int(estado_val.split(" - ")[0])
        id_usuario = int(usuario_val.split(" - ")[0])
        id_gravedad = int(gravedad_val.split(" - ")[0])
        fecha = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("UPDATE Incidente SET descripcion = ? WHERE id_incidente = ?", (desc, self.id_incidente_actual))
        cursor.execute("""
            INSERT INTO incidenteHistorico (id_incidente, id_tipo, id_estado, id_gravedad, id_usuario, fecha)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.id_incidente_actual, id_tipo, id_estado, id_gravedad, id_usuario, fecha))

        conn.commit()
        conn.close()

        self.limpiar_campos()
        self.cargar_incidentes()
        messagebox.showinfo("Éxito", "Incidente actualizado correctamente.")

    def limpiar_campos(self):
        self.entry_desc.delete(0, tk.END)
        self.combo_gravedad.set("")
        self.combo_tipo.set("")
        self.combo_estado.set("")
        self.combo_usuario.set("")
        if hasattr(self, "id_incidente_actual"):
            del self.id_incidente_actual
