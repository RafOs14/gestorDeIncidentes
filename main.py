import tkinter as tk
from ui.main_window import MainApplication

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()