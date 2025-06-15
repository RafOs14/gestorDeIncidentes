import tkinter as tk
from tkinter import ttk
import sqlite3
import textwrap
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

    def obtener_incidentes(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT i.id_incidente, i.tipo, i.estado, u.nombre, i.descripcion, i.fecha, i.gravedad
            FROM Incidente i
            JOIN Usuario u ON i.id_usuario = u.id_usuario
            ORDER BY i.id_incidente
        """)
        datos = cursor.fetchall()
        conn.close()
        return datos

    # 1. TABULAR
    def reporte_tabular(self):
        incidentes = self.obtener_incidentes()

        reporte = "Reporte Tabular de Incidentes\n\n"
        reporte += f"{'ID':<5} {'Tipo':20} {'Estado':15} {'Usuario':15} {'Fecha':10} {'Gravedad':8}\n"
        reporte += "-" * 80 + "\n"

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
            SELECT tipo, COUNT(*)
            FROM Incidente
            GROUP BY tipo
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

    # 3. DETALLADO
    def reporte_detallado(self):
        incidentes = self.obtener_incidentes()

        if not incidentes:
            reporte = "No hay incidentes registrados."
        else:
            reporte = "Reporte Detallado de Incidentes\n\n"
            for inc in incidentes:
                reporte += f"ID: {inc[0]}\n"
                reporte += f"Tipo: {inc[1]}\n"
                reporte += f"Estado: {inc[2]}\n"
                reporte += f"Usuario: {inc[3]}\n"
                desc = textwrap.fill(inc[4], width=60)
                reporte += f"Descripción:\n{desc}\n"
                reporte += f"Fecha: {inc[5]}\n"
                reporte += f"Gravedad: {inc[6]}\n"
                reporte += "-" * 40 + "\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    # 4. COMPARATIVO
    def reporte_comparativo(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo, estado, COUNT(*) AS cantidad
            FROM Incidente
            GROUP BY tipo, estado
            ORDER BY tipo, estado
        """)
        datos = cursor.fetchall()
        conn.close()

        reporte = "Reporte Comparativo por Tipo y Estado\n\n"
        reporte += f"{'Tipo de Incidente':30} {'Estado':15} {'Cantidad':8}\n"
        reporte += "-" * 60 + "\n"

        for tipo, estado, cantidad in datos:
            reporte += f"{tipo:30} {estado:15} {cantidad:<8}\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)
