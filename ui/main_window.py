import tkinter as tk
from tkinter import ttk
from db.init_db import init_db_if_needed
from ui.users_tab import UsuariosTab
from ui.incidentes_tab import IncidentesTab
from ui.reportes_tab import ReportesTab
#from ui.tipoIncidentes_tab import TiposTab

class MainApplication:
    def __init__(self, root):
        init_db_if_needed()
        self.root = root
        self.root.title("Sistema de Gestión de Incidentes")
        self.root.geometry("800x600")

        self.tab_control = ttk.Notebook(root)

        # Crear todos los frames
        self.frame_usuarios = ttk.Frame(self.tab_control)
        self.frame_incidentes = ttk.Frame(self.tab_control)
        self.frame_reportes = ttk.Frame(self.tab_control)
        #self.frame_tipos = ttk.Frame(self.tab_control)  # <-- Agregado correctamente

        # Agregar los tabs
        self.tab_control.add(self.frame_usuarios, text="Usuarios")
        self.tab_control.add(self.frame_incidentes, text="Incidentes")
        self.tab_control.add(self.frame_reportes, text="Reportes")
        #self.tab_control.add(self.frame_tipos, text="Tipos de Incidentes")

        self.tab_control.pack(expand=1, fill="both")

        # Crear instancias de las clases de cada tab
        self.usuarios_tab = UsuariosTab(self.frame_usuarios, self)
        self.usuarios_tab.pack(fill="both", expand=True)
        self.incidentes_tab = IncidentesTab(self.frame_incidentes)
        
        self.reportes_tab = ReportesTab(self.frame_reportes)
        #self.tipos_tab = TiposTab(self.frame_tipos, self)
