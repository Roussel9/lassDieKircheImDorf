# alphazero_engine.py - Korrigierte Version
import math
import random
import torch
import torch.nn.functional as F
import numpy as np
from game_logic import GameState
from config import ROWS, COLS
from neural_network import AlphaZeroNet, encode_board_state, get_move_probabilities, create_move_index_map
import os

class AlphaZeroMCTSNode:
    """MCTS-Knoten für AlphaZero mit neuronaler Netzwerk-Bewertung."""
    
    def __init__(self, game_state, parent=None, move=None, prior=0.0):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.children = []
        
        # MCTS-Statistiken
        self.visit_count = 0
        self.value_sum = 0.0
        self.prior = prior  # Prior-Wahrscheinlichkeit vom neuronalen Netzwerk
        
        # Gültige Züge (lazy loading)
        self.untried_moves = None
    
    def is_expanded(self):
        """Prüft, ob der Knoten bereits erweitert wurde."""
        return self.untried_moves is not None
    
    def expand(self, valid_moves, move_priors):
        """Erweitert den Knoten mit allen gültigen Zügen."""
        self.untried_moves = valid_moves.copy()
        
        if not valid_moves:
            return
        
        for move in valid_moves:
            # Für Place-Moves: Erstelle Kinder für beide Orientierungen
            if move['type'] == 'place' and 'orientation' not in move:
                # Erstelle beide Orientierungen
                for orientation in ['vertikal', 'horizontal']:
                    move_with_orientation = move.copy()
                    move_with_orientation['orientation'] = orientation
                    
                    # Erstelle Move-String
                    move_str = f"place_{move['pos'][0]}_{move['pos'][1]}_{move['stone_type']}_{orientation}"
                    
                    # Hole Prior vom neuronalen Netzwerk
                    prior = move_priors.get(move_str, 0.001)
                    
                    # Erstelle neuen Spielzustand
                    try:
                        new_state = self.game_state.apply_move(move_with_orientation)
                        
                        # Erstelle Kindknoten
                        child = AlphaZeroMCTSNode(new_state, parent=self, move=move_with_orientation, prior=prior)
                        self.children.append(child)
                    except Exception as e:
                        # Debug: Zeige Fehler
                        #print(f"⚠️  Fehler bei expand() für {move_str}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
            else:
                # Für Move- und Pfarrer-Moves: Normal verarbeiten
                if move['type'] == 'place':
                    orientation = move.get('orientation', 'vertikal')
                    move_str = f"place_{move['pos'][0]}_{move['pos'][1]}_{move['stone_type']}_{orientation}"
                elif move['type'] == 'move':
                    move_str = f"move_{move['from'][0]}_{move['from'][1]}_{move['to'][0]}_{move['to'][1]}"
                elif move['type'] == 'pfarrer':
                    move_str = f"pfarrer_{move['from'][0]}_{move['from'][1]}"
                else:
                    move_str = None
                
                if move_str is None:
                    prior = 0.001  # Fallback
                else:
                    prior = move_priors.get(move_str, 0.001)
                
                # Erstelle neuen Spielzustand
                try:
                    new_state = self.game_state.apply_move(move)
                    
                    # Erstelle Kindknoten
                    child = AlphaZeroMCTSNode(new_state, parent=self, move=move, prior=prior)
                    self.children.append(child)
                except Exception as e:
                    # Debug: Zeige Fehler
                   # print(f"⚠️  Fehler bei expand() für {move_str}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
    
    def ucb_score(self, c_puct=5.0):
        """
        Berechnet UCB-Score für AlphaZero (PUCT-Algorithmus).
        
        Args:
            c_puct: Exploration-Konstante (höher = mehr Exploration)
        """
        if self.visit_count == 0:
            return float('inf')
        
        # Exploitation: Durchschnittswert
        exploitation = self.value_sum / self.visit_count
        
        # Exploration: Prior * sqrt(parent_visits) / (1 + visits)
        if self.parent:
            exploration = c_puct * self.prior * math.sqrt(self.parent.visit_count) / (1 + self.visit_count)
        else:
            exploration = c_puct * self.prior / (1 + self.visit_count)
        
        return exploitation + exploration
    
    def select_child(self, c_puct=5.0):
        """Wählt Kindknoten mit höchstem UCB-Score."""
        return max(self.children, key=lambda c: c.ucb_score(c_puct))
    
    def update(self, value):
        """Aktualisiert Statistiken nach Simulation."""
        self.visit_count += 1
        self.value_sum += value
    
    def get_value(self):
        """Gibt den durchschnittlichen Wert zurück."""
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


class AlphaZeroEngine:
    """AlphaZero KI-Engine mit neuronalem Netzwerk."""
    
    def __init__(self, model_path=None, device='cpu'):
        """
        Initialisiert die AlphaZero-Engine.
        
        Args:
            model_path: Pfad zum trainierten Modell (optional)
            device: 'cpu' oder 'cuda'
        """
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # Lade oder erstelle Modell
        self.model = AlphaZeroNet().to(self.device)
        
        if model_path and os.path.exists(model_path):
            try:
                print(f"Versuche Modell zu laden: {model_path}")
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                self.model.eval()
                print(f"✅ Modell geladen von {model_path}")
            except Exception as e:
                print(f"⚠️  Konnte Modell nicht laden: {e}")
                print("Verwende zufällig initialisiertes Modell.")
                self.model.train()  # Im Trainingsmodus für Training
        else:
            if model_path:
                print(f"⚠️  Modell-Pfad existiert nicht: {model_path}")
            print("Verwende zufällig initialisiertes Modell.")
            self.model.train()  # Im Trainingsmodus für Training
        
        # Move-Index-Mapping
        self.move_index_map = create_move_index_map()
    
    def get_move(self, game_state, difficulty, player_id):
        """
        Berechnet den besten Zug für die gegebene Schwierigkeit.
        
        Args:
            game_state: Aktueller Spielzustand
            difficulty: 'einfach', 'mittel', oder 'stark'
            player_id: Spieler-ID (1 oder 2)
        
        Returns:
            move: Besten Zug als Dictionary
        """
        # Konfiguriere Parameter basierend auf Schwierigkeit
        if difficulty == "einfach":
            num_simulations = 25
            c_puct = 1.0
            temperature = 1.0  # Mehr Zufälligkeit
        elif difficulty == "mittel":
            num_simulations = 100
            c_puct = 2.0
            temperature = 0.5  # Weniger Zufälligkeit
        elif difficulty == "stark":
            num_simulations = 400
            c_puct = 5.0
            temperature = 0.1  # Sehr wenig Zufälligkeit (fast deterministisch)
        else:
            num_simulations = 100
            c_puct = 2.0
            temperature = 0.5
        
        print(f"AlphaZero ({difficulty}): {num_simulations} Simulationen, c_puct={c_puct}, temp={temperature}")
        
        # Führe AlphaZero-MCTS aus
        root = AlphaZeroMCTSNode(game_state)
        root.untried_moves = game_state.get_valid_moves(player_id)
        
        if not root.untried_moves:
            return None
        
        # Erweitere Root-Knoten mit neuronaler Netzwerk-Bewertung
        self._expand_node(root, player_id)
        
        # MCTS-Simulationen
        for _ in range(num_simulations):
            self._simulate(root, player_id, c_puct)
        
        # Wähle besten Zug basierend auf Besuchszahlen
        if not root.children:
            # Fallback: Zufälliger Zug
            move = random.choice(root.untried_moves)
            if move['type'] == 'place' and 'orientation' not in move:
                move['orientation'] = random.choice(['vertikal', 'horizontal'])
            return move
        
        # Wähle Zug basierend auf Besuchszahlen und Temperatur
        visit_counts = [c.visit_count for c in root.children]
        
        if temperature == 0.0 or difficulty == "stark":
            # Deterministisch: Wähle meistbesuchten Zug
            best_idx = np.argmax(visit_counts)
            best_move = root.children[best_idx].move
        else:
            # Stochastisch: Sample basierend auf Besuchszahlen
            visit_probs = np.array(visit_counts) ** (1.0 / temperature)
            visit_probs = visit_probs / visit_probs.sum()
            best_idx = np.random.choice(len(root.children), p=visit_probs)
            best_move = root.children[best_idx].move
        
        # Stelle sicher, dass Orientierung vorhanden ist
        if best_move['type'] == 'place' and 'orientation' not in best_move:
            best_move['orientation'] = random.choice(['vertikal', 'horizontal'])
        
        return best_move
    
    def _expand_node(self, node, player_id):
        """Erweitert einen Knoten mit neuronaler Netzwerk-Bewertung."""
        if node.is_expanded():
            return
        
        try:
            # Kodiere Spielzustand
            state_tensor = encode_board_state(node.game_state, player_id).to(self.device)
            
            # Forward pass durch neuronales Netzwerk
            with torch.no_grad():
                policy_logits, value = self.model(state_tensor.unsqueeze(0))  # Batch-Dimension hinzufügen
            
            # Konvertiere Policy zu Wahrscheinlichkeiten für gültige Züge
            valid_moves = node.game_state.get_valid_moves(player_id)
            move_priors = get_move_probabilities(policy_logits, valid_moves, self.move_index_map)
            
            # Debug: Zeige was expand() erhält
            #print(f"🔍 DEBUG _expand_node: valid_moves={len(valid_moves)}, move_priors={len(move_priors)}")
            if len(valid_moves) > 0 and len(move_priors) == 0:
                print(f"⚠️  WARNUNG: move_priors ist leer! valid_moves={len(valid_moves)}")
                # Zeige ersten valid_move
                if valid_moves:
                    print(f"🔍 Erster valid_move: {valid_moves[0]}")
            
            # Erweitere Knoten
            node.expand(valid_moves, move_priors)
            
            # Debug: Prüfe ob Kinder erstellt wurden
            #print(f"🔍 DEBUG _expand_node: Nach expand() - node.children={len(node.children)}")
            if len(node.children) == 0 and len(valid_moves) > 0:
                print(f"⚠️  WARNUNG: Keine Kinder nach expand()! valid_moves={len(valid_moves)}, move_priors={len(move_priors)}")
                if move_priors:
                    print(f"🔍 Erste 3 move_priors keys: {list(move_priors.keys())[:3]}")
        except Exception as e:
            print(f"⚠️  Fehler in _expand_node: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _simulate(self, root, player_id, c_puct):
        """
        Führt eine MCTS-Simulation durch.
        
        Args:
            root: Wurzelknoten
            player_id: Spieler-ID (Perspektive des Wurzelknotens)
            c_puct: Exploration-Konstante
        """
        node = root
        depth = 0
        
        # 1. SELECTION: Wähle Pfad bis zu Blattknoten
        while node.children and not node.untried_moves:
            node = node.select_child(c_puct)
            depth += 1
        
        # Bestimme aktuellen Spieler basierend auf Tiefe
        # In jedem Zug wechselt der Spieler
        current_player = player_id if depth % 2 == 0 else (1 if player_id == 2 else 2)
        
        # 2. EXPANSION: Erweitere Blattknoten falls nötig
        if node.untried_moves:
            self._expand_node(node, current_player)
        
        # 3. EVALUATION: Bewerte Position mit neuronalem Netzwerk
        # Verwende immer die Perspektive des aktuellen Spielers
        if node.children:
            # Verwende Value vom neuronalen Netzwerk
            state_tensor = encode_board_state(node.game_state, current_player).to(self.device)
            with torch.no_grad():
                _, value = self.model(state_tensor.unsqueeze(0))
            value = value.item()
        else:
            # Fallback: Heuristische Bewertung
            value = node.game_state.evaluate_score(node.game_state.board, current_player)
            # Normalisiere auf [-1, 1]
            value = np.tanh(value / 100.0)
        
        # Prüfe Siegbedingung
        if node.game_state.check_win(current_player):
            value = 1.0  # Gewinn für aktuellen Spieler
        elif node.game_state.check_win(1 if current_player == 2 else 2):
            value = -1.0  # Verlust für aktuellen Spieler
        
        # 4. BACKPROPAGATION: Aktualisiere Statistiken
        # Value ist aus Sicht des aktuellen Spielers (current_player am Blatt)
        # Bei Backpropagation: Value wird für jeden Spielerwechsel negiert
        while node is not None:
            # Bestimme Perspektive für diesen Knoten (anhand der game_state.turn)
            # Die game_state.turn zeigt an, wer am Zug ist
            node_player = node.game_state.turn if hasattr(node.game_state, 'turn') else player_id
            
            # Transformiere Value: Wenn Knoten-Spieler != Blatt-Spieler, negiere
            if node_player == current_player:
                node_value = value
            else:
                node_value = -value
            
            node.update(node_value)
            # Für nächsten Knoten (Eltern): Perspektive wechselt
            value = -value
            node = node.parent
    
    def save_model(self, path):
        """Speichert das Modell."""
        # Stelle sicher, dass der Ordner existiert
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"✅ Modell gespeichert: {path}")
    
    def load_model(self, path):
        """Lädt ein trainiertes Modell."""
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            self.model.eval()
            print(f"✅ Modell geladen: {path}")
        else:
            print(f"⚠️  Modell nicht gefunden: {path}")