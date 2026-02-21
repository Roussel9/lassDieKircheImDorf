# ai_engine.py
# AlphaZero KI-Engine mit Fallback auf einfaches MCTS
import math
import random
import time
import os
import torch
from game_logic import GameState
from config import ROWS, COLS

# Versuche AlphaZero zu importieren, Fallback auf einfaches MCTS
try:
    from alphazero_engine import AlphaZeroEngine
    ALPHAZERO_AVAILABLE = True
except ImportError:
    print("Warnung: AlphaZero-Module nicht verfügbar. Verwende einfaches MCTS.")
    ALPHAZERO_AVAILABLE = False

class MCTSNode:
    """Einfacher MCTS-Knoten als Fallback."""
    def __init__(self, state_matrix, parent=None, move=None):
        self.state = state_matrix
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = None

    def uct_select_child(self):
        # Exploration constant C = 1.41
        if not self.children:
            return None
        s = sorted(self.children, key=lambda c: c.wins/c.visits + 1.41 * math.sqrt(math.log(self.visits)/c.visits))[-1]
        return s

    def add_child(self, move, state):
        node = MCTSNode(state, parent=self, move=move)
        if self.untried_moves and move in self.untried_moves:
            self.untried_moves.remove(move)
        self.children.append(node)
        return node

    def update(self, result):
        self.visits += 1
        self.wins += result

class AIEngine:
    """KI-Engine mit AlphaZero-Unterstützung und Fallback."""
    
    def __init__(self):
        """Initialisiert die KI-Engine."""
        self.alphazero_engine = None
        
        # Versuche AlphaZero-Engine zu laden
        if ALPHAZERO_AVAILABLE:
            try:
                # Prüfe ob trainiertes Modell existiert
                model_paths = [
                    "models/alphazero_model.pth",
                    "models/alphazero_model_iter_5.pth",
                    "models/alphazero_model_iter_4.pth",
                    "models/alphazero_model_iter_3.pth",
                ]
                
                model_path = None
                for path in model_paths:
                    if os.path.exists(path):
                        model_path = path
                        break
                
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.alphazero_engine = AlphaZeroEngine(model_path=model_path, device=device)
                print(f"AlphaZero-Engine geladen (Modell: {model_path or 'keines - verwendet zufällig initialisiertes Modell'})")
            except Exception as e:
                print(f"Fehler beim Laden von AlphaZero: {e}. Verwende Fallback-MCTS.")
                self.alphazero_engine = None
    
    def get_move(self, game_state, difficulty, player_id):
        """
        Berechnet den besten Zug mit AlphaZero oder Fallback-MCTS.
        
        Args:
            game_state: Aktueller Spielzustand
            difficulty: 'einfach', 'mittel', oder 'stark'
            player_id: Spieler-ID (1 oder 2)
        """
        # Verwende AlphaZero wenn verfügbar
        if self.alphazero_engine is not None:
            try:
                move = self.alphazero_engine.get_move(game_state, difficulty, player_id)
                if move:
                    return move
            except Exception as e:
                print(f"Fehler bei AlphaZero-Zugberechnung: {e}. Verwende Fallback.")
        
        # Fallback: Einfaches MCTS
        return self._get_move_fallback(game_state, difficulty, player_id)
    
    def _get_move_fallback(self, game_state, difficulty, player_id):
        """Fallback-Methode mit einfachem MCTS."""
        # 1. Konfiguriere Parameter basierend auf Schwierigkeit
        iterations = 50   # Einfach
        depth_max = 5
        
        if difficulty == "mittel":
            iterations = 300
            depth_max = 10
        elif difficulty == "stark":
            iterations = 1000
            depth_max = 25

        print(f"KI ({difficulty}) startet MCTS mit {iterations} Iterationen...")

        # 2. Führe MCTS aus
        return self.run_mcts(game_state, iterations, depth_max, player_id)

    def run_mcts(self, root_game, iterations, depth_max, pid):
        """Einfaches MCTS als Fallback."""
        # On travaille sur une copie de la matrice pour aller vite
        root_matrix = root_game.board
        root_node = MCTSNode(state_matrix=root_matrix)
        
        # Initialisation des coups possibles
        root_node.untried_moves = root_game.get_valid_moves(pid, root_matrix)
        if not root_node.untried_moves: return None

        # Boucle principale MCTS
        for _ in range(iterations):
            node = root_node
            # Copie nécessaire pour descendre dans l'arbre sans casser la racine
            # (Note: ici on simplifie, idéalement on stocke l'état dans le noeud)
            current_matrix = [row[:] for row in node.state] # Shallow copy rapide des lignes
            
            # --- 1. SELECTION ---
            while node.untried_moves == [] and node.children != []:
                node = node.uct_select_child()
                if node is None:
                    break
                # On applique le coup pour mettre à jour la matrice virtuelle
                # (Attention: simplifcation, on ne change pas le tour ici pour la descente)
                # Dans une implémentation stricte, il faut alterner les joueurs.

            # --- 2. EXPANSION ---
            if node and node.untried_moves:
                m = random.choice(node.untried_moves)
                # Orientation random pour la simulation
                if m['type'] == 'place': m['orientation'] = random.choice(['vertikal', 'horizontal'])
                
                # Appliquer le coup sur une nouvelle matrice
                new_matrix = root_game.apply_move_fast(current_matrix, m, pid)
                node = node.add_child(m, new_matrix)
                current_matrix = new_matrix # On continue avec celle-là

            # --- 3. SIMULATION (ROLLOUT) ---
            temp_matrix = current_matrix
            d = 0
            while d < depth_max:
                # On simule pour le joueur courant (pid)
                # Pour faire simple, on suppose que l'adversaire ne joue pas (ou joue aléatoire)
                moves = root_game.get_valid_moves(pid, temp_matrix)
                if not moves: break
                
                m = random.choice(moves)
                if m['type'] == 'place': m['orientation'] = random.choice(['vertikal', 'horizontal'])
                
                temp_matrix = root_game.apply_move_fast(temp_matrix, m, pid)
                d += 1

            # --- 4. BACKPROPAGATION ---
            # Evaluation de l'état final
            score = root_game.evaluate_score(temp_matrix, pid)
            # Normalisation sigmoid-ish (0 = perte, 1 = gain)
            result = 0.5
            if score > 5: result = 1.0
            elif score < -5: result = 0.0
            
            while node is not None:
                node.update(result)
                node = node.parent

        # Choisir le coup le plus visité
        if not root_node.children:
             # Fallback si pas d'enfants (ex: itérations trop faibles)
             if root_node.untried_moves: 
                 m = random.choice(root_node.untried_moves)
                 if m['type'] == 'place': m['orientation'] = random.choice(['vertikal', 'horizontal'])
                 return m
             return None

        best_node = sorted(root_node.children, key=lambda c: c.visits)[-1]
        best_move = best_node.move
        
        # S'assurer d'avoir une orientation pour le placement
        if best_move['type'] == 'place' and 'orientation' not in best_move:
            best_move['orientation'] = random.choice(['vertikal', 'horizontal'])
            
        return best_move
