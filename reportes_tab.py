import tkinter as tk
from tkinter import ttk
import sqlite3
from db.init_db import DB_PATH

class ReportesTab:
    def __init__(self, root):
        self.root = root
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        notebook = ttk.Notebook(self.frame)
        notebook.pack(expand=True, fill="both")

        self.tab_tabular = ttk.Frame(notebook)
        self.tab_detalles = ttk.Frame(notebook)
        self.tab_resumen = ttk.Frame(notebook)
        self.tab_comparativo = ttk.Frame(notebook)

        notebook.add(self.tab_tabular, text="Tabular")
        notebook.add(self.tab_detalles, text="Detalles")
        notebook.add(self.tab_resumen, text="Resumen")
        notebook.add(self.tab_comparativo, text="Comparativo")

        self.inicializar_tab_tabular()
        self.inicializar_tab_detalles()
        self.inicializar_tab_resumen()
        self.inicializar_tab_comparativo()

    def inicializar_tab_tabular(self):
        self.tree_tabular = ttk.Treeview(
            self.tab_tabular,
            columns=("ID", "Tipo", "Gravedad", "Usuario", "Estado", "Fecha"),
            show="headings"
        )
        for col in self.tree_tabular["columns"]:
            self.tree_tabular.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c, False, self.tree_tabular))
        self.tree_tabular.pack(expand=True, fill="both", pady=10)
        self.cargar_tabular()

    def cargar_tabular(self):
        self.tree_tabular.delete(*self.tree_tabular.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT i.id_incidente, i.tipo, i.gravedad, u.nombre, e.nombre, g.fecha
            FROM Incidentes i
            JOIN Cargan c ON i.id_incidente = c.id_incidente
            JOIN Usuarios u ON c.id_usuario = u.id_usuario
            LEFT JOIN (
                SELECT g1.id_incidente, g1.id_estado, g1.fecha
                FROM Genera g1
                JOIN (
                    SELECT id_incidente, MAX(fecha) AS max_fecha
                    FROM Genera
                    GROUP BY id_incidente
                ) g2 ON g1.id_incidente = g2.id_incidente AND g1.fecha = g2.max_fecha
            ) g ON i.id_incidente = g.id_incidente
            LEFT JOIN Estado e ON g.id_estado = e.id_estado
            ORDER BY g.fecha DESC
        """)
        for row in cursor.fetchall():
            self.tree_tabular.insert("", "end", values=row)
        conn.close()

    def inicializar_tab_detalles(self):
        self.tree_detalles = ttk.Treeview(
            self.tab_detalles,
            columns=("ID", "Estado Anterior", "Estado Actual", "Usuario", "Fecha", "Fecha de Cierre"),
            show="headings"
        )
        for col in self.tree_detalles["columns"]:
            self.tree_detalles.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c, False, self.tree_detalles))
        self.tree_detalles.pack(expand=True, fill="both", pady=10)
        self.cargar_detalles()

    def cargar_detalles(self):
        self.tree_detalles.delete(*self.tree_detalles.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                g_act.id_incidente,
                e_ant.nombre AS estado_anterior,
                e_act.nombre AS estado_actual,
                u.nombre AS usuario,
                g_act.fecha,
                cierre.fecha_cierre
            FROM Genera g_act
            LEFT JOIN Genera g_ant 
                ON g_act.id_incidente = g_ant.id_incidente 
                AND g_ant.fecha = (
                    SELECT MAX(fecha) 
                    FROM Genera 
                    WHERE id_incidente = g_act.id_incidente 
                    AND fecha < g_act.fecha
                )
            JOIN Estado e_act ON g_act.id_estado = e_act.id_estado
            LEFT JOIN Estado e_ant ON g_ant.id_estado = e_ant.id_estado
            JOIN Usuarios u ON g_act.id_usuario = u.id_usuario
            LEFT JOIN (
                SELECT id_incidente, MIN(fecha) AS fecha_cierre
                FROM Genera g
                JOIN Estado e ON g.id_estado = e.id_estado
                WHERE e.nombre = 'Cerrado'
                GROUP BY id_incidente
            ) cierre ON g_act.id_incidente = cierre.id_incidente
            ORDER BY g_act.id_incidente, g_act.fecha
        """)
        for row in cursor.fetchall():
            self.tree_detalles.insert("", "end", values=(
                row[0],
                row[1] if row[1] else "",
                row[2],
                row[3],
                row[4],
                row[5] if row[5] else ""
            ))
        conn.close()

    def inicializar_tab_resumen(self):
        self.tree_resumen = ttk.Treeview(
            self.tab_resumen,
            columns=("Tipo", "Cantidad", "Estados"),
            show="headings"
        )
        for col in self.tree_resumen["columns"]:
            self.tree_resumen.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c, False, self.tree_resumen))
        self.tree_resumen.pack(expand=True, fill="both", pady=10)
        self.cargar_resumen()

    def cargar_resumen(self):
        self.tree_resumen.delete(*self.tree_resumen.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT i.tipo, COUNT(DISTINCT i.id_incidente) as total,
                GROUP_CONCAT(DISTINCT e.nombre) as estados
            FROM Incidentes i
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
            GROUP BY i.tipo
        """)
        for row in cursor.fetchall():
            self.tree_resumen.insert("", "end", values=row)
        conn.close()

    def inicializar_tab_comparativo(self):
        self.tree_comparativo = ttk.Treeview(
            self.tab_comparativo,
            columns=("Tipo", "Total", "Cerrados", "Abiertos"),
            show="headings"
        )
        for col in self.tree_comparativo["columns"]:
            self.tree_comparativo.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c, False, self.tree_comparativo))
        self.tree_comparativo.pack(expand=True, fill="both", pady=10)
        self.cargar_comparativo()

    def cargar_comparativo(self):
        self.tree_comparativo.delete(*self.tree_comparativo.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                i.tipo,
                COUNT(i.id_incidente) AS total,
                SUM(CASE WHEN est.nombre = 'Cerrado' THEN 1 ELSE 0 END) AS cerrados,
                SUM(CASE WHEN est.nombre != 'Cerrado' OR est.nombre IS NULL THEN 1 ELSE 0 END) AS abiertos
            FROM Incidentes i
            LEFT JOIN (
                SELECT g1.id_incidente, g1.id_estado
                FROM Genera g1
                JOIN (
                    SELECT id_incidente, MAX(fecha) AS max_fecha
                    FROM Genera
                    GROUP BY id_incidente
                ) g2 ON g1.id_incidente = g2.id_incidente AND g1.fecha = g2.max_fecha
            ) ult ON i.id_incidente = ult.id_incidente
            LEFT JOIN Estado est ON ult.id_estado = est.id_estado
            GROUP BY i.tipo
            ORDER BY i.tipo
        """)
        for row in cursor.fetchall():
            self.tree_comparativo.insert("", "end", values=row)
        conn.close()

    def ordenar_por_columna(self, col, descendente, tree):
        datos = [(tree.set(k, col), k) for k in tree.get_children('')]
        try:
            datos.sort(key=lambda t: int(t[0]), reverse=descendente)
        except ValueError:
            datos.sort(key=lambda t: t[0], reverse=descendente)
        for index, (val, k) in enumerate(datos):
            tree.move(k, '', index)
        tree.heading(col, command=lambda: self.ordenar_por_columna(col, not descendente, tree))
