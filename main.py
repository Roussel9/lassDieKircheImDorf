# main.py
import tkinter as tk
from gui import GameGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Lass die Kirche im Dorf")
    root.geometry("800x850") # Un peu plus grand pour être sûr
    app = GameGUI(root)
    root.mainloop()