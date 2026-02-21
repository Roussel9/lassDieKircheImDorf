# game_logic.py
import copy
from config import *

class Spielstein:
    def __init__(self, spieler_id, typ, ausrichtung='vertikal'):
        self.spieler = spieler_id
        self.typ = typ
        self.ausrichtung = ausrichtung

    def drehen(self):
        self.ausrichtung = 'horizontal' if self.ausrichtung == 'vertikal' else 'vertikal'
    
    def __repr__(self):
        return f"{self.typ}({self.spieler})"

class GameState:
    def __init__(self):
        self.board = [[None] * COLS for _ in range(ROWS)]
        self.turn = 1
        self.pfarrer_pos = (4, 4)
        self.game_over = False
        self.winner = None
        self.unplaced_pieces = {
            1: self._init_pieces(1),
            2: self._init_pieces(2)
        }

    def _init_pieces(self, pid):
        pieces = [Spielstein(pid, 'Turm'), Spielstein(pid, 'Schiff')]
        pieces.extend([Spielstein(pid, 'Haus') for _ in range(7)])
        return pieces

    def get_valid_moves(self, player_id, matrix=None):
        current_board = matrix if matrix is not None else self.board
        moves = []
        
        # --- PHASE 1: PLACEMENT ---
        if len(self.unplaced_pieces[player_id]) > 0:
            next_piece = self.unplaced_pieces[player_id][0]
            if next_piece.typ in ['Turm', 'Schiff']:
                corners = [(1, 1), (1, 7), (7, 1), (7, 7)]
                partner_map = {(1, 1): (7, 7), (7, 7): (1, 1), (1, 7): (7, 1), (7, 1): (1, 7)}
                for r, c in corners:
                    if current_board[r-1][c-1] is None:
                        pr, pc = partner_map[(r, c)]
                        partner = current_board[pr-1][pc-1]
                        if not (partner and partner.spieler != player_id):
                             moves.append({'type': 'place', 'pos': (r, c), 'stone_type': next_piece.typ})
            else:
                for r in range(1, ROWS + 1):
                    for c in range(1, COLS + 1):
                        if current_board[r-1][c-1] is None and (r, c) != self.pfarrer_pos:
                            if not self._has_own_neighbor(r, c, player_id, current_board):
                                moves.append({'type': 'place', 'pos': (r, c), 'stone_type': 'Haus'})
        
        # --- PHASE 2: MOUVEMENT ---
        else:
            for r in range(1, ROWS + 1):
                for c in range(1, COLS + 1):
                    s = current_board[r-1][c-1]
                    if s and s.spieler == player_id:
                        stone_moves = self._get_moves_for_stone(r, c, s, current_board)
                        if len(stone_moves) > 0:
                            moves.extend(stone_moves)
                        else:
                            # Coup Pfarrer SEULEMENT si bloqué (Ta règle)
                            moves.append({'type': 'pfarrer', 'from': (r, c), 'to': self.pfarrer_pos})
        return moves

    def _get_moves_for_stone(self, r, c, s, board):
        local_moves = []
        if s.ausrichtung == 'vertikal':
            directions = [(0, -1), (0, 1)]
        else:
            directions = [(1, 0), (-1, 0)]
        
        for dx, dy in directions:
            dist = 1
            while True:
                nr, nc = r + dy * dist, c + dx * dist
                if not (1 <= nr <= ROWS and 1 <= nc <= COLS): break
                if (nr, nc) == self.pfarrer_pos or board[nr-1][nc-1] is not None: break
                
                local_moves.append({'type': 'move', 'from': (r, c), 'to': (nr, nc)})
                dist += 1
        return local_moves

    def _has_own_neighbor(self, r, c, pid, board):
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r+dr, c+dc
            if 1 <= nr <= ROWS and 1 <= nc <= COLS:
                s = board[nr-1][nc-1]
                if s and s.spieler == pid: return True
        return False

    def apply_move(self, move):
        new_state = copy.deepcopy(self)
        
        if move['type'] == 'place':
            r, c = move['pos']
            if len(new_state.unplaced_pieces[new_state.turn]) > 0:
                p = new_state.unplaced_pieces[new_state.turn].pop(0)
                if 'orientation' in move: p.ausrichtung = move['orientation']
                new_state.board[r-1][c-1] = p
            
        elif move['type'] == 'move':
            fr, fc = move['from']
            tr, tc = move['to']
            p = new_state.board[fr-1][fc-1]
            new_state.board[fr-1][fc-1] = None
            new_state.board[tr-1][tc-1] = p
            if p: p.drehen()
            
        elif move['type'] == 'pfarrer':
            sr, sc = move['from']
            pr, pc = move['to']
            p = new_state.board[sr-1][sc-1]
            new_state.board[pr-1][pc-1] = p
            new_state.board[sr-1][sc-1] = None
            new_state.pfarrer_pos = (sr, sc)
            if p: p.drehen()

        if new_state.check_win(new_state.turn):
            new_state.game_over = True
            new_state.winner = new_state.turn

        new_state.turn = 1 if new_state.turn == 2 else 2
        return new_state

    def apply_move_fast(self, matrix, move, pid):
        new_matrix = copy.deepcopy(matrix)
        if move['type'] == 'place':
            r, c = move['pos']
            s = Spielstein(pid, move['stone_type'], 'vertikal')
            new_matrix[r-1][c-1] = s
        elif move['type'] == 'move':
            fr, fc = move['from']
            tr, tc = move['to']
            p = new_matrix[fr-1][fc-1]
            new_matrix[fr-1][fc-1] = None
            new_matrix[tr-1][tc-1] = p
            if p: p.drehen()
        elif move['type'] == 'pfarrer':
             sr, sc = move['from']
             pr, pc = move['to']
             p = new_matrix[sr-1][sc-1]
             new_matrix[pr-1][pc-1] = p
             new_matrix[sr-1][sc-1] = None
             if p: p.drehen()
        return new_matrix

    # -------------------------------------------------------------------------
    # MODIFICATION MAJEURE 1 : VICTOIRE STRICTE (EGLISE DANS LE VILLAGE)
    # -------------------------------------------------------------------------
    def check_win(self, pid):
        stones = []
        church_on_edge = False # Drapeau : Est-ce qu'une partie de l'église est sur le bord ?

        for r in range(ROWS):
            for c in range(COLS):
                s = self.board[r][c]
                if s and s.spieler == pid:
                    stones.append((r, c))
                    
                    # SI C'EST UNE PIÈCE D'ÉGLISE (Tour ou Nef)
                    if s.typ in ['Turm', 'Schiff']:
                        # BORD = Ligne 0 ou 6, Colonne 0 ou 6 (Indices Python 0 à 6)
                        if r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
                            church_on_edge = True

        # CONDITIONS D'ÉCHEC
        if len(stones) < 9: return False # Pas assez de pierres
        if church_on_edge: return False  # L'église n'est pas "dans le village" !

        # CONDITIONS DE RÉUSSITE : Connexité
        queue = [stones[0]]
        visited = {stones[0]}
        count = 0
        while queue:
            curr = queue.pop(0)
            count += 1
            cr, cc = curr
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = cr+dr, cc+dc
                if (nr, nc) in stones and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        
        return count == len(stones)

    # -------------------------------------------------------------------------
    # MODIFICATION MAJEURE 2 : IA STRATÉGIQUE (Liberté, Connexité, Blocage)
    # -------------------------------------------------------------------------
    def evaluate_score(self, matrix, pid):
        """
        IA PARANOÏAQUE : PRIORITÉ DÉFENSE ABSOLUE
        """
        score = 0
        opp_id = 1 if pid == 2 else 2
        
        my_stones = []
        opp_stones = []
        pfarrer_r, pfarrer_c = self.pfarrer_pos # On a besoin de savoir où il est
        
        # 1. ANALYSE DU PLATEAU
        for r in range(ROWS):
            for c in range(COLS):
                s = matrix[r][c]
                if s:
                    if s.spieler == pid:
                        my_stones.append((r, c))
                        # BONUS : Eglise en sécurité
                        if s.typ in ['Turm', 'Schiff']:
                            if 0 < r < ROWS-1 and 0 < c < COLS-1:
                                score += 60 
                            else:
                                score -= 150 # URGENCE : RENTRER L'EGLISE
                    else:
                        opp_stones.append((r, c))
                        # MALUS : L'adversaire a son église au centre !
                        if s.typ in ['Turm', 'Schiff']:
                            if 0 < r < ROWS-1 and 0 < c < COLS-1:
                                score -= 200 # DANGER MORTEL

        # 2. LIBERTÉ (MOBILITÉ)
        # On veut étouffer l'adversaire
        my_liberty = 0
        opp_liberty = 0
        
        for stones, is_me in [(my_stones, True), (opp_stones, False)]:
            liberties = 0
            for r, c in stones:
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and matrix[nr][nc] is None: 
                        liberties += 1
            if is_me: my_liberty = liberties
            else: opp_liberty = liberties
            
        score += (my_liberty * 2) - (opp_liberty * 5) # Pénaliser la liberté adverse plus fort

        # 3. CONNEXITÉ (Le nerf de la guerre)
        # On compte les connexions
        my_connections = 0
        for r, c in my_stones:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    n_stone = matrix[nr][nc]
                    if n_stone and n_stone.spieler == pid:
                        my_connections += 1
        
        opp_connections = 0
        for r, c in opp_stones:
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    n_stone = matrix[nr][nc]
                    if n_stone and n_stone.spieler == opp_id:
                        opp_connections += 1

        # ALGORITHME PARANOÏAQUE :
        # Une connexion à moi vaut +10.
        # Une connexion à lui vaut -25 (Je dois absolument le bloquer).
        score += (my_connections * 10)
        score -= (opp_connections * 25)

        # 4. PRESSION DU PFARRER
        # Si le Pfarrer est collé à une pierre adverse, c'est bien (blocage potentiel)
        pr, pc = self.pfarrer_pos
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = pr+dr, pc+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                n_stone = matrix[nr][nc]
                if n_stone and n_stone.spieler == opp_id:
                    score += 15 # Harcèlement du prêtre

        return score