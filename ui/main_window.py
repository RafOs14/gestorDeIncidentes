import tkinter as tk
from tkinter import ttk
from db.init_db import init_db_if_needed
from ui.users_tab import UsuariosTab
from ui.incidentes_tab import IncidentesTab
from ui.reportes_tab import ReportesTab

class MainApplication:
    def __init__(self, root):
        init_db_if_needed()
        self.root = root
        self.root.title("Sistema de Gestión de Incidentes")
        self.root.geometry("800x600")

        self.tab_control = ttk.Notebook(root)

        self.frame_usuarios = ttk.Frame(self.tab_control)
        self.frame_incidentes = ttk.Frame(self.tab_control)
        self.frame_reportes = ttk.Frame(self.tab_control)

        self.tab_control.add(self.frame_usuarios, text="Usuarios")
        self.tab_control.add(self.frame_incidentes, text="Incidentes")
        self.tab_control.add(self.frame_reportes, text="Reportes")

        self.tab_control.pack(expand=1, fill="both")

        # Crear instancias y guardar referencias cruzadas
        self.incidentes_tab = IncidentesTab(self.frame_incidentes)
        self.usuarios_tab = UsuariosTab(self.frame_usuarios, self)
        self.reportes_tab = ReportesTab(self.frame_reportes)
