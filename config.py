# config.py
ROWS = 7
COLS = 7
CELL_SIZE = 80  # Un peu plus grand pour voir les détails
OFFSET = 40
WINDOW_SIZE = ROWS * CELL_SIZE
LINE_WIDTH = 2

# --- NOMS DES JOUEURS (C'est ici que tu changes le texte !) ---
NAME_P1 = "Weiss"   # Ou "Hell", "Sable"
NAME_P2 = "Schwarz" # Ou "Dunkel", "Noyer"

# --- PALETTE STYLE "BOIS" ---
COLOR_BG = '#F5F5DC'        # Beige clair (Table)
COLOR_GRID = '#8B4513'      # Brun cuir (Grille)

# Joueur 1 (Bois Clair)
COLOR_P1 = '#E3C699'        # Couleur "Hêtre" ou "Sable"
COLOR_P1_BORDER = '#B8860B' # Contour doré foncé

# Joueur 2 (Bois Fonce)
COLOR_P2 = '#5D4037'        # Couleur "Noyer" ou "Chocolat"
COLOR_P2_BORDER = '#3E2723' # Contour très foncé

# Interface & Pfarrer
COLOR_PFARRER = '#F1C40F'   # Or (Indispensable pour le dessin du prêtre)
COLOR_HIGHLIGHT = '#32CD32' # Vert Lime pour bien voir la sélection
COLOR_SHADOW = '#888888'    # Gris pour l'ombre

# Polices d'écriture (Indispensables pour l'interface)
FONT_MAIN = ('Helvetica', 12, 'bold')
FONT_TITLE = ('Helvetica', 16, 'bold')