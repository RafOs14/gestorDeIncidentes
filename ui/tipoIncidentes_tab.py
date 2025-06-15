import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3 
from db.init_db import DB_PATH

class TiposTab:
    def __init__(self, frame, main_app):
        self.frame = frame
        self.main_app = main_app
        self.crear_widgets()
        self.cargar_tipos()

    def crear_widgets(self):
        self.label_desc = ttk.Label(self.frame, text="Tipo de incidente:")
        self.label_desc.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.entry_desc = ttk.Entry(self.frame, width=50)
        self.entry_desc.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky='ew')

        btn_agregar = ttk.Button(self.frame, text="Agregar Tipo", command=self.agregar_tipo_incidente)
        btn_agregar.grid(row=1, column=0, pady=10)

        btn_actualizar = ttk.Button(self.frame, text="Actualizar Tipo", command=self.actualizar_tipo)
        btn_actualizar.grid(row=1, column=1, pady=10)

        btn_eliminar = ttk.Button(self.frame, text="Eliminar Tipo", command=self.eliminar_tipo)
        btn_eliminar.grid(row=1, column=2, pady=10)

        self.tree_tipos = ttk.Treeview(
            self.frame,
            columns=("ID", "Tipo"),
            show="headings"
        )
        self.tree_tipos.heading("ID", text="ID")
        self.tree_tipos.heading("Tipo", text="Nombre Tipo")
        self.tree_tipos.column("ID", width=50, anchor="center")
        self.tree_tipos.column("Tipo", anchor="w")

        self.tree_tipos.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=10)
        self.tree_tipos.bind("<Double-1>", self.seleccionar_tipo)

        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

    def cargar_tipos(self):
        for row in self.tree_tipos.get_children():
            self.tree_tipos.delete(row)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id_tipo, nombre_tipo FROM TipoIncidente ORDER BY id_tipo ASC")
        for tipo in cursor.fetchall():
            self.tree_tipos.insert("", tk.END, values=tipo)
        conn.close()

    def agregar_tipo_incidente(self):
        descripcion = self.entry_desc.get().strip()
        if not descripcion:
            messagebox.showwarning("Atención", "La descripción no puede estar vacía.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO TipoIncidente (nombre_tipo) VALUES (?)", (descripcion,))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese tipo ya existe.")
        finally:
            conn.close()

        self.entry_desc.delete(0, tk.END)
        self.cargar_tipos()
        
        messagebox.showinfo("Éxito", "Tipo ingresado correctamente")

        if self.main_app.incidentes_tab:
            self.main_app.incidentes_tab.cargar_combobox_incidentes()

    def seleccionar_tipo(self, event):
        selected_item = self.tree_tipos.selection()
        if not selected_item:
            return
        values = self.tree_tipos.item(selected_item, "values")
        self.id_tipo_actual = values[0]
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[1])

    def actualizar_tipo(self):
        if not hasattr(self, 'id_tipo_actual'):
            messagebox.showwarning("Atención", "Debes seleccionar un tipo para actualizar.")
            return

        desc = self.entry_desc.get().strip()
        if not desc:
            messagebox.showwarning("Atención", "El nombre del tipo no puede estar vacío.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE TipoIncidente SET nombre_tipo = ? WHERE id_tipo = ?", (desc, self.id_tipo_actual))
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, tk.END)
        del self.id_tipo_actual
        self.cargar_tipos()
        messagebox.showinfo("Éxito", "Tipo actualizado correctamente")

        if self.main_app.incidentes_tab:
            self.main_app.incidentes_tab.cargar_combobox_incidentes()

    def eliminar_tipo(self):
        selected_item = self.tree_tipos.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Debes seleccionar un tipo para eliminar.")
            return

        id_tipo = self.tree_tipos.item(selected_item, "values")[0]

        confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar este tipo?")
        if not confirm:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar si el tipo tiene incidentes asociados
        cursor.execute("SELECT COUNT(*) FROM Incidente WHERE id_tipo = ?", (id_tipo,))
        asociados = cursor.fetchone()[0]

        if asociados > 0:
            messagebox.showerror("Error", "No se puede eliminar este tipo porque tiene incidentes asociados.")
            conn.close()
            return

        cursor.execute("DELETE FROM TipoIncidente WHERE id_tipo = ?", (id_tipo,))
        conn.commit()
        conn.close()

        self.entry_desc.delete(0, tk.END)
        if hasattr(self, 'id_tipo_actual'):
            del self.id_tipo_actual
        self.cargar_tipos()

        if self.main_app.incidentes_tab:
            self.main_app.incidentes_tab.cargar_combobox_incidentes()

        messagebox.showinfo("Éxito", "Tipo eliminado correctamente")
