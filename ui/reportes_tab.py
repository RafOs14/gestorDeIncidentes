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
        ttk.Button(self.frame_reportes, text="Reporte Histórico de Cambios", command=self.reporte_historico_cambios).pack(pady=5)

        self.text_reportes = tk.Text(self.frame_reportes, height=25, wrap=tk.NONE)
        self.text_reportes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Añadir scroll horizontal para evitar corte de texto largo
        x_scroll = ttk.Scrollbar(self.frame_reportes, orient=tk.HORIZONTAL, command=self.text_reportes.xview)
        x_scroll.pack(fill=tk.X, side=tk.BOTTOM)
        self.text_reportes.configure(xscrollcommand=x_scroll.set)

    # 1. TABULAR
    def reporte_tabular(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id_incidente,
                t.nombre_tipo,
                e.nombre_estado,
                u.nombre,
                i.descripcion,
                i.fechaCreacion,
                g.nivel
            FROM Incidente i
            JOIN incidenteHistorico h ON h.id_incidente = i.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            JOIN Estado e ON h.id_estado = e.id_estado
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Gravedad g ON h.id_gravedad = g.id_gravedad
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
            ORDER BY i.id_incidente
        """)
        incidentes = cursor.fetchall()
        conn.close()

        columnas = ["ID", "Tipo", "Estado", "Usuario", "Fecha", "Gravedad", "Descripción"]

        datos_str = [
            [str(inc[0]), str(inc[1]), str(inc[2]), str(inc[3]), str(inc[5]), str(inc[6]), str(inc[4])]
            for inc in incidentes
        ]

        # Calcular anchos máximos por columna (títulos vs datos)
        anchos = []
        for col_idx in range(len(columnas)):
            max_titulo = len(columnas[col_idx])
            max_dato = max((len(fila[col_idx]) for fila in datos_str), default=0)
            anchos.append(max(max_titulo, max_dato) + 2)  # espacio extra

        def fila_formateada(fila):
            return "".join(f"{texto:<{anchos[i]}}" for i, texto in enumerate(fila))

        reporte = "Reporte Tabular de Incidentes\n\n"
        if not incidentes:
            reporte += "No hay incidentes para mostrar."
        else:
            reporte += fila_formateada(columnas) + "\n"
            reporte += "-" * sum(anchos) + "\n"
            for fila in datos_str:
                reporte += fila_formateada(fila) + "\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)


    # 2. RESUMEN / AGREGADO
    def reporte_resumen(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.nivel, COUNT(*)
            FROM Incidente i
            JOIN incidenteHistorico h ON h.id_incidente = i.id_incidente
            JOIN Gravedad g ON h.id_gravedad = g.id_gravedad
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
            GROUP BY g.nivel
        """)
        gravedad = cursor.fetchall()

        cursor.execute("""
            SELECT t.nombre_tipo, COUNT(*)
            FROM Incidente i
            JOIN incidenteHistorico h ON h.id_incidente = i.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
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

    # 3. DETALLE (todos los incidentes con datos actuales)
    def reporte_detallado(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                i.id_incidente,
                t.nombre_tipo,
                e.nombre_estado,
                u.nombre,
                i.descripcion,
                i.fechaCreacion,
                g.nivel
            FROM Incidente i
            JOIN incidenteHistorico h ON h.id_incidente = i.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            JOIN Estado e ON h.id_estado = e.id_estado
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Gravedad g ON h.id_gravedad = g.id_gravedad
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
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
                reporte += f"Fecha Creación: {inc[5]}\n"
                reporte += f"Gravedad: {inc[6]}\n"
                reporte += "-"*40 + "\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    # 4. COMPARATIVO
    def reporte_comparativo(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.nombre_tipo, e.nombre_estado, COUNT(*) as cantidad
            FROM Incidente i
            JOIN incidenteHistorico h ON h.id_incidente = i.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            JOIN Estado e ON h.id_estado = e.id_estado
            WHERE h.id_hist = (
                SELECT MAX(id_hist) FROM incidenteHistorico WHERE id_incidente = i.id_incidente
            )
            GROUP BY t.nombre_tipo, e.nombre_estado
            ORDER BY t.nombre_tipo, e.nombre_estado
        """)
        datos = cursor.fetchall()
        conn.close()

        reporte = "Reporte Comparativo de Incidentes por Tipo y Estado\n\n"
        reporte += f"{'Tipo de Incidente':<30} {'Estado':<15} {'Cantidad':<8}\n"
        reporte += "-"*55 + "\n"

        for tipo, estado, cantidad in datos:
            reporte += f"{tipo:<30} {estado:<15} {cantidad:<8}\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

    # 5. HISTÓRICO DE CAMBIOS
    def reporte_historico_cambios(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                h.id_hist,
                i.id_incidente,
                t.nombre_tipo,
                e.nombre_estado,
                u.nombre,
                h.fecha,
                g.nivel
            FROM incidenteHistorico h
            JOIN Incidente i ON h.id_incidente = i.id_incidente
            JOIN TipoIncidente t ON h.id_tipo = t.id_tipo
            JOIN Estado e ON h.id_estado = e.id_estado
            JOIN Usuario u ON h.id_usuario = u.id_usuario
            JOIN Gravedad g ON h.id_gravedad = g.id_gravedad
            ORDER BY h.id_hist, h.fecha DESC
        """)
        cambios = cursor.fetchall()
        conn.close()

        # Columnas y títulos
        columnas = ["ID Hist", "ID Incidente", "Tipo", "Estado", "Usuario", "Fecha", "Gravedad"]

        # Armo una lista con los datos (como strings)
        datos_str = [
            [str(c[0]), str(c[1]), str(c[2]), str(c[3]), str(c[4]), str(c[5]), str(c[6])]
            for c in cambios
        ]

        # Calculo ancho máximo por columna comparando con título y datos
        anchos = []
        for col_idx in range(len(columnas)):
            max_titulo = len(columnas[col_idx])
            max_dato = max((len(fila[col_idx]) for fila in datos_str), default=0)
            anchos.append(max(max_titulo, max_dato) + 2)  # +2 para espacio extra

        # Función para construir una fila formateada
        def fila_formateada(fila):
            return "".join(f"{texto:<{anchos[i]}}" for i, texto in enumerate(fila))

        reporte = "Reporte Histórico de Cambios en Incidentes\n\n"
        if not cambios:
            reporte += "No hay registros históricos de cambios."
        else:
            reporte += fila_formateada(columnas) + "\n"
            reporte += "-" * sum(anchos) + "\n"
            for fila in datos_str:
                reporte += fila_formateada(fila) + "\n"

        self.text_reportes.delete("1.0", tk.END)
        self.text_reportes.insert(tk.END, reporte)

