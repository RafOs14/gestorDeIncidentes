import tkinter as tk
from tkinter import ttk
import sqlite3
from db.init_db import DB_PATH

class ReportesTab:
    def __init__(self, root):
        self.root = root

        # Crear el contenedor principal con padding
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(expand=True, fill="both")

        # Crear un notebook (pestañas)
        notebook = ttk.Notebook(self.frame)
        notebook.pack(expand=True, fill="both")

        # Crear cada pestaña: Tabular, Detalles y Resumen
        self.tab_tabular = ttk.Frame(notebook)
        self.tab_detalles = ttk.Frame(notebook)
        self.tab_resumen = ttk.Frame(notebook)
        self.tab_comparativo = ttk.Frame(notebook)

        # Agregar pestañas al notebook
        notebook.add(self.tab_tabular, text="Tabular")
        notebook.add(self.tab_detalles, text="Detalles")
        notebook.add(self.tab_resumen, text="Resumen")
        notebook.add(self.tab_comparativo, text="Comparativo")
        

        # Inicializar contenido de cada pestaña
        self.inicializar_tab_tabular()
        self.inicializar_tab_detalles()
        self.inicializar_tab_resumen()
        self.inicializar_tab_comparativo()

    def inicializar_tab_tabular(self):
        # Crear tabla con columnas para la vista tabular
        self.tree_tabular = ttk.Treeview(
            self.tab_tabular,
            columns=("ID", "Tipo", "Gravedad", "Usuario", "Estado", "Fecha"),
            show="headings"
        )
        for col in self.tree_tabular["columns"]:
            self.tree_tabular.heading(col, text=col)
        self.tree_tabular.pack(expand=True, fill="both", pady=10)

        # Cargar datos desde la base
        self.cargar_tabular()

    def cargar_tabular(self):
        """Carga datos de incidentes con estado más reciente"""
        self.tree_tabular.delete(*self.tree_tabular.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener información del incidente, tipo, usuario que lo cargó y su estado más reciente
        cursor.execute("""
            SELECT i.id_incidente, t.tipo, t.gravedad, u.nombre, e.nombre, g.fecha
            FROM Incidentes i
            JOIN Tipos t ON i.id_tipo = t.id_tipo
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
        # Crear tabla con columnas para mostrar los cambios de estado
        self.tree_detalles = ttk.Treeview(
            self.tab_detalles,
            columns=("ID", "Estado Anterior", "Estado Actual", "Usuario", "Fecha", "Fecha de Cierre"),
            show="headings"
        )
        for col in self.tree_detalles["columns"]:
            self.tree_detalles.heading(col, text=col)
        self.tree_detalles.pack(expand=True, fill="both", pady=10)

        # Cargar los detalles de estado
        self.cargar_detalles()

    def cargar_detalles(self):
        """Carga historial de cambios de estado por incidente, mostrando también la fecha de cierre si aplica"""
        self.tree_detalles.delete(*self.tree_detalles.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener cambios de estado, usuario y fecha. Se incluye el estado anterior (si existe)
        # y la fecha de cierre si el estado final es 'Cerrado'
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
        rows = cursor.fetchall()

        # Insertar datos en el Treeview, mostrando vacío si no hay estado anterior o fecha de cierre
        for row in rows:
            fecha_cierre = row[5] if row[5] is not None else ""
            self.tree_detalles.insert("", "end", values=(
                row[0],                          # ID Incidente
                row[1] if row[1] else "",        # Estado Anterior
                row[2],                          # Estado Actual
                row[3],                          # Usuario
                row[4],                          # Fecha
                fecha_cierre                     # Fecha de Cierre (si aplica)
            ))
        conn.close()

    def inicializar_tab_resumen(self):
        # Crear tabla para mostrar resumen por tipo de incidente
        self.tree_resumen = ttk.Treeview(
            self.tab_resumen,
            columns=("Tipo", "Cantidad", "Estados"),
            show="headings"
        )
        for col in self.tree_resumen["columns"]:
            self.tree_resumen.heading(col, text=col)
        self.tree_resumen.pack(expand=True, fill="both", pady=10)

        # Cargar el resumen
        self.cargar_resumen()

    def cargar_resumen(self):
        """Muestra resumen de incidentes por tipo: cantidad y estados actuales"""
        self.tree_resumen.delete(*self.tree_resumen.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener por tipo: cantidad total y estado más reciente
        cursor.execute("""
            SELECT t.tipo, COUNT(DISTINCT i.id_incidente) as total,
                GROUP_CONCAT(DISTINCT e.nombre) as estados
            FROM Incidentes i
            JOIN Tipos t ON i.id_tipo = t.id_tipo
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
            GROUP BY t.tipo
        """)
        for row in cursor.fetchall():
            self.tree_resumen.insert("", "end", values=row)
        conn.close()
        
    def inicializar_tab_comparativo(self):
        # Crear tabla para comparar incidentes abiertos y cerrados por tipo
        self.tree_comparativo = ttk.Treeview(
            self.tab_comparativo,
            columns=("Tipo", "Total", "Cerrados", "Abiertos"),
            show="headings"
        )
        for col in self.tree_comparativo["columns"]:
            self.tree_comparativo.heading(col, text=col)
        self.tree_comparativo.pack(expand=True, fill="both", pady=10)

        # Cargar datos comparativos
        self.cargar_comparativo()

    def cargar_comparativo(self):
        """Muestra cantidad total, abiertos y cerrados por tipo de incidente"""
        self.tree_comparativo.delete(*self.tree_comparativo.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                t.tipo,
                COUNT(i.id_incidente) AS total,
                SUM(CASE WHEN est.nombre = 'Cerrado' THEN 1 ELSE 0 END) AS cerrados,
                SUM(CASE WHEN est.nombre != 'Cerrado' OR est.nombre IS NULL THEN 1 ELSE 0 END) AS abiertos
            FROM Incidentes i
            JOIN Tipos t ON i.id_tipo = t.id_tipo
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
            GROUP BY t.tipo
            ORDER BY t.tipo
        """)

        for row in cursor.fetchall():
            self.tree_comparativo.insert("", "end", values=row)

        conn.close()
