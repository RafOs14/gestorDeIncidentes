import tkinter as tk
from tkinter import ttk
from usuarios_tab import UsuariosTab
from incidentes_tab import IncidentesTab
from reportes_tab import ReportesTab
from db.init_db import init_db_if_needed

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Incidentes")
        self.root.geometry("400x200")

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True)

        ttk.Label(self.frame, text="Sistema de Gestión de Incidentes", font=("Arial", 14)).pack(pady=10)

        ttk.Button(self.frame, text="Usuarios", command=self.abrir_usuarios).pack(fill="x", pady=5)
        ttk.Button(self.frame, text="Incidentes", command=self.abrir_incidentes).pack(fill="x", pady=5)
        ttk.Button(self.frame, text="Reportes", command=self.abrir_reportes).pack(fill="x", pady=5)

    def abrir_usuarios(self):
        win = tk.Toplevel(self.root)
        UsuariosTab(win)

    def abrir_incidentes(self):
        win = tk.Toplevel(self.root)
        IncidentesTab(win)
        
    def abrir_reportes(self):
        win = tk.Toplevel(self.root)
        ReportesTab(win)

if __name__ == "__main__":
    init_db_if_needed()
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
