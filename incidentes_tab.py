import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from db.init_db import DB_PATH

# Tipos enumerados como diccionario
TIPOS_DE_INCIDENTE = {
    "Falla eléctrica": {"gravedad": "Alta", "descripcion": "Corte o sobrecarga de energía", "estado": "Nuevo"},
    "Problema de red": {"gravedad": "Media", "descripcion": "Conectividad intermitente o caída total", "estado": "Pendiente"},
    "Error de software": {"gravedad": "Baja", "descripcion": "Bug en el sistema reportado por el usuario", "estado": "En progreso"},
    "Fuga de datos": {"gravedad": "Alta", "descripcion": "Exposición no autorizada de información sensible", "estado": "Resuelto"},
    "Incidente físico": {"gravedad": "Media", "descripcion": "Daño o robo de hardware", "estado": "Pendiente"},
    "Problema de seguridad": {"gravedad": "Alta", "descripcion": "Amenaza o vulnerabilidad detectada", "estado": "Nuevo"},
}

class IncidentesTab:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Incidentes")

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Tipo", "Gravedad", "Descripción", "Usuario", "Estado"),
            show="headings"
        )
        column_widths = {
            "ID": 50,
            "Tipo": 100,
            "Gravedad": 100,
            "Descripción": 300,
            "Usuario": 120,
            "Estado": 120,
        }
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c, False))
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center", stretch=True)
        self.tree.pack(fill="both", expand=True, pady=10)

        form_frame = ttk.Frame(self.frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, sticky="e")
        self.tipo_cb = ttk.Combobox(form_frame, state="readonly")
        self.tipo_cb["values"] = list(TIPOS_DE_INCIDENTE.keys())
        self.tipo_cb.grid(row=0, column=1, padx=5)
        self.tipo_cb.bind("<<ComboboxSelected>>", self.actualizar_info_tipo)

        ttk.Label(form_frame, text="Gravedad:").grid(row=1, column=0, sticky="e")
        self.gravedad_var = tk.StringVar()
        self.gravedad_entry = ttk.Entry(form_frame, textvariable=self.gravedad_var, state="readonly")
        self.gravedad_entry.grid(row=1, column=1, padx=5)

        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky="ne")
        self.descripcion_text = tk.Text(form_frame, height=4, width=40, wrap="word", state="disabled")
        self.descripcion_text.grid(row=2, column=1, padx=5)

        ttk.Label(form_frame, text="Usuario:").grid(row=3, column=0, sticky="e")
        self.usuario_cb = ttk.Combobox(form_frame, state="readonly")
        self.usuario_cb.grid(row=3, column=1, padx=5)

        ttk.Label(form_frame, text="Estado:").grid(row=4, column=0, sticky="e")
        self.estado_cb = ttk.Combobox(form_frame, state="readonly")
        self.estado_cb.grid(row=4, column=1, padx=5)

        ttk.Button(form_frame, text="Registrar Incidente", command=self.agregar_incidente).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(self.frame, text="Cambiar Estado del Incidente Seleccionado", command=self.cambiar_estado).pack(pady=5)

        self.usuarios = {}
        self.estados = {}

        self.cargar_desplegables()
        self.cargar_incidentes()

    def actualizar_info_tipo(self, event):
        tipo = self.tipo_cb.get()
        datos = TIPOS_DE_INCIDENTE.get(tipo)
        if datos:
            self.gravedad_var.set(datos["gravedad"])
            self.descripcion_text.configure(state="normal")
            self.descripcion_text.delete("1.0", tk.END)
            self.descripcion_text.insert(tk.END, datos["descripcion"])
            self.descripcion_text.configure(state="disabled")
            self.estado_cb.set(datos["estado"])

    def cargar_desplegables(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id_usuario, nombre FROM Usuarios")
        self.usuarios = {nombre: id_usuario for id_usuario, nombre in cursor.fetchall()}
        self.usuario_cb["values"] = list(self.usuarios.keys())

        cursor.execute("SELECT id_estado, nombre FROM Estado")
        self.estados = {nombre: id_estado for id_estado, nombre in cursor.fetchall()}
        self.estado_cb["values"] = list(self.estados.keys())

        conn.close()

    def ordenar_por_columna(self, col, descendente):
        datos = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            datos.sort(key=lambda t: int(t[0]), reverse=descendente)
        except ValueError:
            datos.sort(key=lambda t: t[0], reverse=descendente)
        for index, (val, k) in enumerate(datos):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.ordenar_por_columna(col, not descendente))

    def cargar_incidentes(self):
        self.tree.delete(*self.tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id_incidente, 
                i.tipo, 
                i.gravedad, 
                i.descripcion, 
                u.nombre,
                e.nombre
            FROM Incidentes i
            JOIN Cargan c ON i.id_incidente = c.id_incidente
            JOIN Usuarios u ON c.id_usuario = u.id_usuario
            LEFT JOIN (
                SELECT g1.id_incidente, g1.id_estado
                FROM Genera g1
                JOIN (
                    SELECT id_incidente, MAX(fecha) AS max_fecha
                    FROM Genera
                    GROUP BY id_incidente
                ) g2 ON g1.id_incidente = g2.id_incidente AND g1.fecha = g2.max_fecha
            ) ult ON i.id_incidente = ult.id_incidente
            LEFT JOIN Estado e ON ult.id_estado = e.id_estado
            ORDER BY i.id_incidente ASC
        """)
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def agregar_incidente(self):
        tipo = self.tipo_cb.get()
        datos_tipo = TIPOS_DE_INCIDENTE.get(tipo)
        if not datos_tipo:
            messagebox.showwarning("Atención", "Selecciona un tipo válido.")
            return

        gravedad = datos_tipo["gravedad"]
        descripcion = datos_tipo["descripcion"]
        estado = datos_tipo["estado"]
        usuario = self.usuario_cb.get()

        if not (tipo and usuario):
            messagebox.showwarning("Atención", "Completa todos los campos.")
            return

        id_usuario = self.usuarios[usuario]
        id_estado = self.estados[estado]
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Incidentes (tipo, gravedad, descripcion) VALUES (?, ?, ?)",
                       (tipo, gravedad, descripcion))
        id_incidente = cursor.lastrowid

        cursor.execute("INSERT INTO Cargan (id_usuario, id_incidente, fecha_inicio) VALUES (?, ?, ?)",
                       (id_usuario, id_incidente, fecha_actual))

        cursor.execute("INSERT INTO Genera (id_incidente, id_estado, id_usuario, fecha) VALUES (?, ?, ?, ?)",
                       (id_incidente, id_estado, id_usuario, fecha_actual))

        conn.commit()
        conn.close()

        self.tipo_cb.set("")
        self.gravedad_var.set("")
        self.descripcion_text.configure(state="normal")
        self.descripcion_text.delete("1.0", tk.END)
        self.descripcion_text.configure(state="disabled")
        self.usuario_cb.set("")
        self.estado_cb.set("")

        self.cargar_incidentes()

    def cambiar_estado(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Selecciona un incidente.")
            return

        item = self.tree.item(selected[0])
        id_incidente = item["values"][0]
        usuario = item["values"][4]

        nuevo_estado = self.estado_cb.get()
        if not nuevo_estado:
            messagebox.showwarning("Atención", "Selecciona un nuevo estado.")
            return

        id_usuario = self.usuarios.get(usuario)
        id_estado = self.estados[nuevo_estado]
        resultado = self._cambiar_estado_incidente(id_incidente, id_estado, id_usuario)

        messagebox.showinfo("Estado actualizado",
            f"Estado anterior: {resultado['estado_anterior'] or 'N/A'}\n"
            f"Nuevo estado: {resultado['estado_nuevo']}\n"
            f"Fecha del cambio: {resultado['fecha_cambio']}"
        )
        self.cargar_incidentes()

    def _cambiar_estado_incidente(self, id_incidente, nuevo_id_estado, id_usuario):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT g.id_estado, e.nombre, g.fecha
            FROM Genera g
            JOIN Estado e ON g.id_estado = e.id_estado
            WHERE g.id_incidente = ?
            ORDER BY g.fecha DESC
            LIMIT 1
        """, (id_incidente,))
        resultado = cursor.fetchone()
        estado_anterior = resultado[1] if resultado else None
        fecha_anterior = resultado[2] if resultado else None

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO Genera (id_incidente, id_estado, id_usuario, fecha)
            VALUES (?, ?, ?, ?)
        """, (id_incidente, nuevo_id_estado, id_usuario, fecha_actual))

        cursor.execute("SELECT nombre FROM Estado WHERE id_estado = ?", (nuevo_id_estado,))
        nuevo_nombre_estado = cursor.fetchone()[0]
        if nuevo_nombre_estado.lower() == "cerrado":
            cursor.execute("""
                UPDATE Cargan
                SET fecha_fin = ?
                WHERE id_incidente = ? AND id_usuario = ?
            """, (fecha_actual, id_incidente, id_usuario))

        conn.commit()
        conn.close()

        return {
            "estado_anterior": estado_anterior,
            "estado_nuevo": nuevo_nombre_estado,
            "fecha_anterior": fecha_anterior,
            "fecha_cambio": fecha_actual
        }
