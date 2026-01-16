# ai_engine.py
import math
import random
import time
from game_logic import GameState
from config import ROWS, COLS

class MCTSNode:
    def __init__(self, state_matrix, parent=None, move=None):
        self.state = state_matrix
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = None # On le remplit à la volée

    def uct_select_child(self):
        # Exploration constant C = 1.41
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
    def get_move(self, game_state, difficulty, player_id):
        # 1. Configurer la puissance selon la difficulté
        iterations = 50   # Einfach (Stupide/Rapide)
        depth_max = 5     # Profondeur de simulation
        
        if difficulty == "mittel":
            iterations = 300
            depth_max = 10
        elif difficulty == "stark":
            iterations = 1000 # AlphaZero style (prend 2-3 secondes)
            depth_max = 25

        print(f"KI ({difficulty}) startet MCTS mit {iterations} Iterationen...")

        # 2. Lancer MCTS
        return self.run_mcts(game_state, iterations, depth_max, player_id)

    def run_mcts(self, root_game, iterations, depth_max, pid):
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
                # On applique le coup pour mettre à jour la matrice virtuelle
                # (Attention: simplifcation, on ne change pas le tour ici pour la descente)
                # Dans une implémentation stricte, il faut alterner les joueurs.

            # --- 2. EXPANSION ---
            if node.untried_moves:
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