# gui.py - Korrigierte Version (aktualisierte Farbnamen)
import tkinter as tk
from tkinter import messagebox
import traceback
from config import *
from game_logic import GameState
from ai_engine import AIEngine

# --- POPUP ORIENTATION ---
class RichtungsWaehler(tk.Toplevel):
    def __init__(self, parent, stone_type):
        super().__init__(parent)
        self.title("Ausrichtung")
        self.geometry("280x160")
        x = parent.winfo_x() + 50
        y = parent.winfo_y() + 50
        self.geometry(f"+{x}+{y}")
        self.result = None
        
        tk.Label(self, text=f"Ausrichtung für {stone_type}?", font=('Arial', 11)).pack(pady=15)
        btn_font = ('Arial', 9, 'bold')
        tk.Button(self, text="↕ VERTIKAL", command=lambda: self.set_res('vertikal'), font=btn_font, width=20).pack(pady=5)
        tk.Button(self, text="↔ HORIZONTAL", command=lambda: self.set_res('horizontal'), font=btn_font, width=20).pack(pady=5)
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def set_res(self, res):
        self.result = res
        self.destroy()

# --- MENU DÉMARRAGE ---
class StartMenue(tk.Toplevel):
    def __init__(self, parent, callback_new_game):
        super().__init__(parent)
        self.title("Start")
        self.geometry("300x280")
        self.callback = callback_new_game
        x = parent.winfo_x() + 80
        y = parent.winfo_y() + 80
        self.geometry(f"+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self.master.quit)

        tk.Label(self, text="LASS DIE KIRCHE IM DORF", font=('Arial', 12, 'bold'), fg='#333').pack(pady=15)
        tk.Label(self, text="DEBUG MODUS", fg="red", font=('Arial', 8)).pack()
        tk.Label(self, text="Modus wählen:", font=('Arial', 10)).pack(pady=5)
        
        btn_style = {'font': ('Arial', 9), 'width': 28, 'pady': 4}
        tk.Button(self, text="👤 Mensch vs Mensch", **btn_style, command=lambda: self.start(False, "mittel")).pack(pady=5)
        tk.Label(self, text="- GEGEN KI (MCTS) -", font=('Arial', 8), fg='gray').pack(pady=5)
        tk.Button(self, text="🤖 KI - Einfach", **btn_style, command=lambda: self.start(True, "einfach")).pack(pady=2)
        tk.Button(self, text="🤖 KI - Mittel", **btn_style, command=lambda: self.start(True, "mittel")).pack(pady=2)
        tk.Button(self, text="🧠 KI - Stark (AlphaZero)", **btn_style, bg='#e6f3ff', command=lambda: self.start(True, "stark")).pack(pady=2)

    def start(self, ai, diff):
        self.callback(ai, diff)
        self.destroy()

# --- GUI PRINCIPAL ---
class GameGUI(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)
        self.master = master
        
        # BARRE D'ÉTAT DEBUG (Rouge en bas)
        self.status_var = tk.StringVar()
        self.status_var.set("Bienvenue. En attente du démarrage...")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#ffdddd", fg="red")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # CANVAS JEU
        self.canvas = tk.Canvas(self, width=WINDOW_SIZE + 2*OFFSET, height=WINDOW_SIZE + 2*OFFSET, bg=COLOR_BG)
        self.canvas.pack(side=tk.TOP)
        
        self.game = GameState()
        self.ai = AIEngine()
        self.ki_active = False
        self.ki_difficulty = "mittel"
        self.selected_pos = None
        
        self.create_menu()
        self.draw_grid()
        
        # Binding du clic
        self.canvas.bind("<Button-1>", self.on_click)
        
        self.master.after(100, self.zeige_start_menue)

    def log(self, message):
        """Affiche un message dans la barre rouge"""
        print(message) # Affiche aussi dans la console
        self.status_var.set(message)

    def zeige_start_menue(self):
        StartMenue(self.master, self.new_game)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Spiel", menu=game_menu)
        game_menu.add_command(label="Neues Spiel...", command=self.zeige_start_menue)
        game_menu.add_command(label="Beenden", command=self.master.quit)

    def new_game(self, ai, diff="mittel"):
        try:
            self.game = GameState()
            self.ki_active = ai
            self.ki_difficulty = diff
            self.selected_pos = None
            self.draw_board()
            self.update_title()
            
            msg = f" " + (f" {NAME_P1}." if ai else f" {NAME_P1} ")
            self.log(msg + f" ")
            
        except Exception as e:
            self.master.lift()
            messagebox.showerror("Erreur New Game", str(e), parent=self.master)

    def update_title(self):
        mode = f"KI-{self.ki_difficulty}" if self.ki_active else "PvP"
        turn = NAME_P1 if self.game.turn == 1 else NAME_P2
        if len(self.game.unplaced_pieces[self.game.turn]) > 0:
            p = self.game.unplaced_pieces[self.game.turn][0].typ
            msg = f"Placer: {p}"
        else:
            msg = "Bouger"
        self.master.title(f"LDKID | {turn} | {msg} | {mode}")

    def draw_grid(self):
        self.canvas.delete("grid")
        for i in range(ROWS + 1):
            p = i * CELL_SIZE + OFFSET
            self.canvas.create_line(OFFSET, p, WINDOW_SIZE + OFFSET, p, width=LINE_WIDTH, fill=COLOR_GRID, tags="grid")
            self.canvas.create_line(p, OFFSET, p, WINDOW_SIZE + OFFSET, width=LINE_WIDTH, fill=COLOR_GRID, tags="grid")

    def draw_board(self):
        self.canvas.delete("piece")
        self.canvas.delete("selection")
        
        # 1. DESSIN DU PFARRER
        pr, pc = self.game.pfarrer_pos
        px, py = self._get_coords(pr, pc)
        
        if self.selected_pos == 'pfarrer':
            self.canvas.create_oval(px-35, py-35, px+35, py+35, outline=COLOR_HIGHLIGHT, width=4, tags="selection")

        # Pion Noir (Pfarrer)
        self.canvas.create_polygon(px-12, py+20, px+12, py+20, px, py-10, fill='black', outline='black', tags="piece")
        self.canvas.create_oval(px-10, py-22, px+10, py-2, fill='black', outline='black', tags="piece")
        self.canvas.create_oval(px-4, py-18, px-1, py-15, fill='#555', outline="", tags="piece")

        # 2. DESSIN DES PIÈCES
        for r in range(1, ROWS + 1):
            for c in range(1, COLS + 1):
                s = self.game.board[r-1][c-1]
                if s:
                    x, y = self._get_coords(r, c)
                    
                    # Couleurs basées auf config.py
                    if s.spieler == 1:
                        fill_col = COLOR_P1
                        border_col = COLOR_P1_BORDER
                        arrow_col = "#B8860B"  # Dunkles Gold für Pfeile
                    else:
                        fill_col = COLOR_P2
                        border_col = COLOR_P2_BORDER
                        arrow_col = "#3E2723"  # Sehr dunkelbraun für Pfeile
                    
                    # Sélection
                    if self.selected_pos == (r,c):
                        self.canvas.create_oval(x-40, y-40, x+40, y+40, outline=COLOR_HIGHLIGHT, width=3, tags="selection")

                    rad = 30
                    sh_off = 4 # Décalage ombre
                    
                    points = [] # Points du polygone à dessiner

                    # === LOGIQUE DE FORME ET ROTATION ===

                    # A) MAISON (HAUS) - Pentagone orienté
                    if s.typ == 'Haus':
                        if s.ausrichtung == 'vertikal':
                            # Pointe vers le HAUT
                            points = [
                                x, y-rad,          # Sommet
                                x+rad-5, y-rad+15, # Epaule Droite
                                x+rad-5, y+rad,    # Bas Droite
                                x-rad+5, y+rad,    # Bas Gauche
                                x-rad+5, y-rad+15  # Epaule Gauche
                            ]
                        else: # Horizontal
                            # Pointe vers la DROITE
                            points = [
                                x+rad, y,          # Sommet (Droite)
                                x+rad-15, y+rad-5, # Epaule Bas
                                x-rad, y+rad-5,    # Arrière Bas
                                x-rad, y-rad+5,    # Arrière Haut
                                x+rad-15, y-rad+5  # Epaule Haut
                            ]
                        
                        # Dessin Ombre + Pièce
                        shadow_pts = [p + sh_off for p in points]
                        self.canvas.create_polygon(shadow_pts, fill=COLOR_SHADOW, tags="piece")
                        self.canvas.create_polygon(points, fill=fill_col, outline=border_col, width=2, tags="piece")
                        # Pas de flèche pour la maison !

                    # B) TOUR (TURM) - Triangle orienté
                    elif s.typ == 'Turm':
                        if s.ausrichtung == 'vertikal':
                            # Triangle pointant vers le HAUT
                            points = [
                                x, y-rad-5,    # Sommet
                                x+20, y+rad,   # Bas Droite
                                x-20, y+rad    # Bas Gauche
                            ]
                        else: # Horizontal
                            # Triangle pointant vers la DROITE
                            points = [
                                x+rad+5, y,    # Sommet
                                x-rad, y+20,   # Arrière Bas
                                x-rad, y-20    # Arrière Haut
                            ]

                        # Dessin Ombre + Pièce
                        shadow_pts = [p + sh_off for p in points]
                        self.canvas.create_polygon(shadow_pts, fill=COLOR_SHADOW, tags="piece")
                        self.canvas.create_polygon(points, fill=fill_col, outline=border_col, width=2, tags="piece")
                        # Pas de flèche pour la tour !

                    # C) NEF (SCHIFF) - Cercle (Garde la flèche car un rond n'a pas de sens)
                    elif s.typ == 'Schiff':
                        # Ombre
                        self.canvas.create_oval(x-rad+sh_off, y-rad+sh_off, x+rad+sh_off, y+rad+sh_off, fill=COLOR_SHADOW, outline="", tags="piece")
                        # Pièce
                        self.canvas.create_oval(x-rad, y-rad, x+rad, y+rad, fill=fill_col, outline=border_col, width=2, tags="piece")
                        # Cercle interne déco
                        self.canvas.create_oval(x-rad+6, y-rad+6, x+rad-6, y+rad-6, outline=border_col, width=1, tags="piece")
                        
                        # FLÈCHE (Seulement pour le Schiff)
                        arr_len = 16
                        if s.ausrichtung == 'vertikal':
                            self.canvas.create_line(x, y-arr_len, x, y+arr_len, fill=arrow_col, width=3, arrow=tk.BOTH, arrowshape=(8,10,3), tags="piece")
                        else:
                            self.canvas.create_line(x-arr_len, y, x+arr_len, y, fill=arrow_col, width=3, arrow=tk.BOTH, arrowshape=(8,10,3), tags="piece")

    def _get_coords(self, r, c):
        return (c-0.5)*CELL_SIZE + OFFSET, (r-0.5)*CELL_SIZE + OFFSET

    def _get_grid_pos(self, x, y):
        if x < OFFSET or y < OFFSET: return None, None
        c = int((x - OFFSET) / CELL_SIZE) + 1
        r = int((y - OFFSET) / CELL_SIZE) + 1
        if 1 <= r <= ROWS and 1 <= c <= COLS: return r, c
        return None, None

    def on_click(self, event):
        try:
            if self.game.game_over: return
            if self.ki_active and self.game.turn == 2: return 

            # 1. Obtenir la case cliquée
            r, c = self._get_grid_pos(event.x, event.y)
            if not r: return

            valid_moves = self.game.get_valid_moves(self.game.turn)
            
            # --- CAS 1 : Clic sur le PFARRER (pour activer l'échange) ---
            if (r, c) == self.game.pfarrer_pos:
                # On vérifie si on a déjà sélectionné une pièce bloquée avant
                if self.selected_pos:
                    fr, fc = self.selected_pos
                    # On cherche si un échange est possible depuis la pièce sélectionnée vers ce Pfarrer
                    swap_move = next((m for m in valid_moves if m['type'] == 'pfarrer' and m['from'] == (fr, fc)), None)
                    if swap_move:
                        self.execute_move(swap_move)
                        self.selected_pos = None
                        return
                
                # Sinon, on sélectionne le Pfarrer lui-même
                self.selected_pos = (r, c)
                self.log("")
                self.draw_board()
                # On dessine un cercle de sélection autour du Pfarrer
                x, y = self._get_coords(r, c)
                self.canvas.create_oval(x-35, y-35, x+35, y+35, outline=COLOR_HIGHLIGHT, width=4, tags="selection")
                return

            # --- CAS 2 : PLACEMENT (Phase 1) ---
            place_move = next((m for m in valid_moves if m['type'] == 'place' and m['pos'] == (r,c)), None)
            if place_move:
                stone_type = place_move['stone_type']
                rw = RichtungsWaehler(self.master, stone_type)
                if rw.result:
                    place_move['orientation'] = rw.result
                    self.execute_move(place_move)
                return

            # --- CAS 3 : SÉLECTION D'UNE PIÈCE (Phase 2) ---
            clicked_piece = self.game.board[r-1][c-1]
            if clicked_piece and clicked_piece.spieler == self.game.turn:
                # Si on avait sélectionné le Pfarrer avant, on essaie l'échange
                if self.selected_pos == self.game.pfarrer_pos:
                    # On cherche un move où 'from' est CETTE pièce et 'to' est le Pfarrer
                    swap_move = next((m for m in valid_moves if m['type'] == 'pfarrer' and m['from'] == (r, c)), None)
                    if swap_move:
                        self.execute_move(swap_move)
                        self.selected_pos = None
                        return
                    else:
                        self.log("")
                
                # Sinon on sélectionne juste la pièce normalement
                self.selected_pos = (r, c)
                self.draw_board()
                return
            
            # --- CAS 4 : MOUVEMENT VERS UNE CASE VIDE ---
            if self.selected_pos:
                fr, fc = self.selected_pos
                
                # Est-ce un mouvement normal ?
                move = next((m for m in valid_moves if m['type'] == 'move' and m['from'] == (fr, fc) and m['to'] == (r, c)), None)
                
                if move:
                    self.execute_move(move)
                    self.selected_pos = None
                else:
                    if (r,c) != self.selected_pos:
                        # Ce n'est ni un move, ni un échange...
                        self.log("Mouvement impossible ici.")
                        self.selected_pos = None
                        self.draw_board()

        except Exception as e:
            print(f"Erreur clic: {e}")
            self.master.lift()
            messagebox.showerror("Erreur", str(e), parent=self.master)

    def execute_move(self, move):
        self.log(f" {move['type']}")
        self.game = self.game.apply_move(move)
        self.draw_board()
        self.update_title()
        
        if self.game.game_over:
            w = NAME_P1 if self.game.winner == 1 else NAME_P2
            # Force fenêtre principale au premier plan puis affiche messagebox
            self.master.lift()
            self.master.attributes('-topmost', True)
            self.master.update()
            messagebox.showinfo("Ende", f"{w} gewinnt!", parent=self.master)
            self.master.attributes('-topmost', False)
            return

        if self.ki_active and self.game.turn == 2:
            self.log("")
            self.master.after(100, self.run_ai)
        else:
            self.log("")

    def run_ai(self):
        try:
            self.master.config(cursor="watch")
            self.master.update()
            move = self.ai.get_move(self.game, self.ki_difficulty, 2)
            self.master.config(cursor="")
            
            if move:
                self.game = self.game.apply_move(move)
                self.draw_board()
                self.update_title()
                if self.game.game_over:
                    # Force fenêtre principale au premier plan puis affiche messagebox
                    self.master.lift()
                    self.master.attributes('-topmost', True)
                    self.master.update()
                    messagebox.showinfo("Ende", f"KI ({self.ki_difficulty}) gewinnt!", parent=self.master)
                    self.master.attributes('-topmost', False)
                else:
                    self.log("")
            else:
                self.log("")
        except Exception as e:
            traceback.print_exc()
            self.master.lift()
            messagebox.showerror("Erreur IA", str(e), parent=self.master)