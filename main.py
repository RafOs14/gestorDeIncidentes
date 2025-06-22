import tkinter as tk
from tkinter import ttk
from usuarios_tab import UsuariosTab
from incidentes_tab import IncidentesTab
from reportes_tab import ReportesTab
from db.init_db import init_db_if_needed

#Clase principal, esto abre la ventana principal con el acceso a las ventanas del programa
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Incidentes")
        self.root.geometry("400x200")

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True)

        ttk.Label(self.frame, text="Sistema de Gestión de Incidentes", font=("Arial", 14)).pack(pady=10)
        
        # Botones para abrir las diferentes pestañas
        ttk.Button(self.frame, text="Usuarios", command=self.abrir_usuarios).pack(fill="x", pady=5)
        ttk.Button(self.frame, text="Incidentes", command=self.abrir_incidentes).pack(fill="x", pady=5)
        ttk.Button(self.frame, text="Reportes", command=self.abrir_reportes).pack(fill="x", pady=5)

    # Método para abrir la ventana de gestión de usuarios
    def abrir_usuarios(self):
        win = tk.Toplevel(self.root)
        UsuariosTab(win)
    # Método para abrir la ventana de gestión de incidentes
    def abrir_incidentes(self):
        win = tk.Toplevel(self.root)
        IncidentesTab(win)
    # Método para abrir la ventana de reportes
    def abrir_reportes(self):
        win = tk.Toplevel(self.root)
        ReportesTab(win)

# Método para inicializar la base de datos si es necesario y el programa no se ha ejecutado antes ademas 
#ejecuta el programa
if __name__ == "__main__":
    init_db_if_needed()
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
