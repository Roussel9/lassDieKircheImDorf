# main.py
import tkinter as tk
from gui import GameGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lass die Kirche im Dorf")
    root.geometry("800x850") # Un peu plus grand pour être sûr
    
    # S'assurer que la fenêtre n'est pas transparente
    try:
        root.attributes('-alpha', 1.0)  # Opacité complète (1.0 = non transparent)
    except:
        pass  # Certains systèmes ne supportent pas cet attribut
    
    app = GameGUI(root)
    root.mainloop()