import tkinter as tk
from tkinter import ttk
import sqlite3
from db.init_db import DB_PATH

class ReportesTab:
    def __init__(self, frame_reportes):
        self.frame_reportes = frame_reportes
        self.build_reportes_tab()

    def build_reportes_tab(self):
        ttk.Button(self.frame_reportes, text="Reporte Tabular", command=self.reporte_tabular).pack(pady=5)
        ttk.Button(self.frame_reportes, text="Reporte Resumen", command=self.reporte_resumen).pack(pady=5)
        ttk.Button(self.frame_reportes, text="Reporte Detallado", command=self.reporte_detallado).pack(pady=5)
        ttk.Button(self.frame_reportes, text="Reporte Comparativo", command=self.reporte_comparativo).pack(pady=5)

        self.text_reportes = tk.Text(self.frame_reportes, height=25)
        self.text_reportes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 1. TABULAR
    def reporte_tabular(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, t.nombre_tipo, e.nombre_estado, u.nombre, i.descripcion, i.fecha, i.gravedad
            FROM Incidente i
            JOIN TipoIncidente t ON i.id_tipo = t.id_tipo
            JOIN Estado e ON i.id_estado = e.id_estado
            JOIN Usuario u ON i.id_usuario = u.id_usuario
            ORDER BY i.id_incidente
        """)
        incidentes = cursor.fetchall()
        conn.close()

        reporte = "Reporte Tabular de Incidentes\n\n"
        reporte += f"{'ID':<5} {'Tipo':20} {'Estado':15} {'Usuario':15} {'Fecha':10} {'Gravedad':8}\n"
        reporte += "-"*80 + "\n"
        for inc in incidentes:
            reporte += f"{inc[0]:<5} {inc[1]:20} {inc[2]:15} {inc[3]:15} {inc[5]:10} {inc[6]:8}\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    # 2. RESUMEN / AGREGADO
    def reporte_resumen(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT gravedad, COUNT(*)
            FROM Incidente
            GROUP BY gravedad
        """)
        gravedad = cursor.fetchall()

        cursor.execute("""
            SELECT t.nombre_tipo, COUNT(*)
            FROM Incidente i
            JOIN TipoIncidente t ON i.id_tipo = t.id_tipo
            GROUP BY t.nombre_tipo
        """)
        tipo = cursor.fetchall()
        conn.close()

        reporte = "Reporte Resumen de Incidentes\n\n"
        reporte += "Cantidad por Gravedad:\n"
        for nivel, cantidad in gravedad:
            reporte += f"- {nivel}: {cantidad}\n"

        reporte += "\nCantidad por Tipo:\n"
        for tipo_inc, cantidad in tipo:
            reporte += f"- {tipo_inc}: {cantidad}\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    # 3. DETALLE (del primer incidente)
    def reporte_detallado(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, t.nombre_tipo, e.nombre_estado, u.nombre, i.descripcion, i.fecha, i.gravedad
            FROM Incidente i
            JOIN TipoIncidente t ON i.id_tipo = t.id_tipo
            JOIN Estado e ON i.id_estado = e.id_estado
            JOIN Usuario u ON i.id_usuario = u.id_usuario
            ORDER BY i.id_incidente ASC
        """)
        incidentes = cursor.fetchall()
        conn.close()

        if not incidentes:
            reporte = "No hay incidentes registrados."
        else:
            reporte = "Reporte Detallado de Incidentes\n\n"
            for inc in incidentes:
                reporte += f"ID: {inc[0]}\n"
                reporte += f"Tipo: {inc[1]}\n"
                reporte += f"Estado: {inc[2]}\n"
                reporte += f"Usuario: {inc[3]}\n"
                reporte += f"Descripción: {inc[4]}\n"
                reporte += f"Fecha: {inc[5]}\n"
                reporte += f"Gravedad: {inc[6]}\n"
                reporte += "-"*40 + "\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    def reporte_comparativo(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, t.nombre_tipo, e.nombre_estado, COUNT(*) OVER (PARTITION BY t.nombre_tipo, e.nombre_estado) AS cantidad
            FROM Incidente i
            JOIN TipoIncidente t ON i.id_tipo = t.id_tipo
            JOIN Estado e ON i.id_estado = e.id_estado
            ORDER BY i.id_incidente, t.nombre_tipo, e.nombre_estado
        """)
        datos = cursor.fetchall()
        conn.close()

        reporte = "Reporte de Incidentes con Estado Actual\n\n"
        reporte += f"{'ID':5} {'Tipo de Incidente':30} {'Estado':15} {'Cantidad':8}\n"
        reporte += "-"*65 + "\n"

        for id_inc, tipo, estado, cantidad in datos:
            reporte += f"{id_inc:<5} {tipo:30} {estado:15} {cantidad:<8}\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)
