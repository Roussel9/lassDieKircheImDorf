# train_alphazero.py
# Training-Skript für AlphaZero durch Selbstspiel
import torch
import torch.optim as optim
import torch.nn.functional as F
import random
import copy
import os
import shutil
from collections import deque
from game_logic import GameState
from neural_network import AlphaZeroNet, encode_board_state, create_move_index_map
from alphazero_engine import AlphaZeroEngine, AlphaZeroMCTSNode

class SelfPlayBuffer:
    """Speichert Trainingsdaten aus Selbstspiel."""
    
    def __init__(self, max_size=10000):
        self.buffer = deque(maxlen=max_size)
    
    def add(self, state, policy, value):
        """Fügt einen Trainingsdatensatz hinzu."""
        self.buffer.append((state, policy, value))
    
    def sample(self, batch_size):
        """Sampelt einen Batch von Trainingsdaten."""
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        states = torch.cat([s[0] for s in batch], dim=0)  # Concatenate along batch dimension
        policies = torch.stack([s[1] for s in batch])
        values = torch.stack([s[2] for s in batch])
        return states, policies, values
    
    def size(self):
        return len(self.buffer)


# In train_alphazero.py, self_play_game Funktion:

def self_play_game(engine, num_simulations = 100, c_puct=5.0, max_game_length=200):
    """
    Führt ein Selbstspiel durch und sammelt Trainingsdaten.
    
    Args:
        engine: AlphaZeroEngine
        num_simulations: Anzahl MCTS-Simulationen pro Zug
        c_puct: Exploration-Konstante
        max_game_length: Maximale Spielzüge (verhindert endlose Spiele)
    
    Returns:
        training_data: Liste von (state, policy, value) Tupeln
    """
    game = GameState()
    training_data = []
    move_index_map = create_move_index_map()
    
    # Speichere alle besuchten Positionen während des Spiels
    game_history = []
    
    move_count = 0
    
    while not game.game_over and move_count < max_game_length:
        current_player = game.turn
        move_count += 1
        
        # Erstelle MCTS-Baum für aktuellen Zustand
        root = AlphaZeroMCTSNode(game)
        # WICHTIG: Setze untried_moves NICHT hier, sonst ist is_expanded() = True!
        # root.untried_moves wird in _expand_node gesetzt
        
        valid_moves_before = game.get_valid_moves(current_player)
        if not valid_moves_before:
            # Debug: Keine gültigen Züge mehr
            break
        
        # Erweitere Root-Knoten
        try:
            # Debug: Zeige valid_moves vor Expansion
          #  print(f"🔍 DEBUG: {len(valid_moves_before)} valid_moves vor Expansion")
            
            engine._expand_node(root, current_player)
            
            # Debug: Zeige was nach Expansion passiert ist
          #  print(f"🔍 DEBUG: root.children nach Expansion: {len(root.children)}")
            if len(root.children) == 0:
                print(f"🔍 DEBUG: valid_moves waren: {valid_moves_before}")
        except Exception as e:
            print(f"⚠️  Fehler beim Expandieren: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Überprüfe ob Expansion erfolgreich war
        if not root.children:
            print(f"⚠️  WARNUNG: root.children ist leer nach Expansion! (valid_moves={len(root.untried_moves) if root.untried_moves else 0})")
            break
        
        # Führe MCTS-Simulationen durch
        try:
            for _ in range(num_simulations):
                engine._simulate(root, current_player, c_puct)
        except Exception as e:
            print(f"⚠️  Fehler bei Simulation: {e}")
            import traceback
            traceback.print_exc()
            break
        
        # Erstelle Policy-Vektor aus Besuchszahlen
        if root.children:
            visit_counts = torch.zeros(len(root.children))
            for i, child in enumerate(root.children):
                visit_counts[i] = child.visit_count
            
            # Normalisiere zu Wahrscheinlichkeiten
            if visit_counts.sum() > 0:
                policy = visit_counts / visit_counts.sum()
            else:
                policy = torch.ones(len(root.children)) / len(root.children)
            
            # Speichere Trainingsdaten
            state_tensor = encode_board_state(game, current_player)
            game_history.append((state_tensor, policy, root.children))
            
            # Temperatur-Abstufung: Zu Beginn hohe Temperatur (Exploration),
            # gegen Ende niedrige Temperatur (Exploitation)
            # AlphaZero Standard: Nach 30 Zügen deterministisch spielen
            temperature = 1.0 if move_count <= 30 else 0.0
            
            # Wähle Zug basierend auf Policy und Temperatur
            if temperature == 0.0:
                # Deterministisch: Wähle meistbesuchten Zug
                move_idx = torch.argmax(policy).item()
            else:
                # Stochastisch: Sample basierend auf Temperatur
                # Erhöhe Temperatur für mehr Exploration
                policy_temp = policy ** (1.0 / temperature)
                policy_temp = policy_temp / policy_temp.sum()
                move_idx = torch.multinomial(policy_temp, 1).item()
            
            move = root.children[move_idx].move
        else:
            move = random.choice(root.untried_moves)
        
        # Führe Zug aus
        game = game.apply_move(move)
        
        # Prüfe Siegbedingung
        if game.check_win(current_player):
            winner = current_player
            break
        elif game.check_win(1 if current_player == 2 else 2):
            winner = 1 if current_player == 2 else 2
            break
    
    # Bestimme Sieger
    if game.game_over:
        winner = game.winner
    else:
        # Unentschieden (Spiel zu lang)
        winner = None
    
    # Debug: Zeige wie viele Positionen gesammelt wurden
    if len(game_history) == 0:
        print(f"⚠️  WARNUNG: Keine Positionen in game_history gesammelt! (move_count={move_count}, game_over={game.game_over})")
    
    # Erstelle Trainingsdaten mit korrekten Werten
    for i, (state, policy, children) in enumerate(game_history):
        # Wert basierend auf Sieger
        if winner is None:
            value = 0.0
        elif (i % 2 == 0 and winner == 1) or (i % 2 == 1 and winner == 2):
            value = 1.0  # Gewinn
        else:
            value = -1.0  # Verlust
        
        # Konvertiere Policy zu vollständigem Vektor
        # Verwende die tatsächliche Anzahl der möglichen Züge
        max_moves = len(move_index_map)
        full_policy = torch.zeros(max_moves)
        
        if children:
            for j, child in enumerate(children):
                if child.move:
                    move = child.move
                    # Erstelle konsistenten Move-String
                    if move['type'] == 'place':
                        orientation = move.get('orientation', 'vertikal')
                        move_str = f"place_{move['pos'][0]}_{move['pos'][1]}_{move['stone_type']}_{orientation}"
                    elif move['type'] == 'move':
                        move_str = f"move_{move['from'][0]}_{move['from'][1]}_{move['to'][0]}_{move['to'][1]}"
                    elif move['type'] == 'pfarrer':
                        move_str = f"pfarrer_{move['from'][0]}_{move['from'][1]}"
                    else:
                        continue
                    
                    move_idx = move_index_map.get(move_str, -1)
                    if move_idx >= 0 and j < len(policy):
                        full_policy[move_idx] = policy[j].item()
        
        training_data.append((state.unsqueeze(0), full_policy, torch.tensor(value)))
    
    return training_data


def train_model(model, training_data, epochs=10, batch_size=32, lr=0.001):
    """
    Trainiert das neuronale Netzwerk.
    
    Args:
        model: AlphaZeroNet Modell
        training_data: Liste von (state, policy, value) Tupeln
        epochs: Anzahl Epochen
        batch_size: Batch-Größe
        lr: Lernrate
    """
    if not training_data:
        print("Keine Trainingsdaten vorhanden!")
        return
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    model.train()
    
    # Konvertiere zu Batches
    states = torch.cat([d[0] for d in training_data])
    policies = torch.stack([d[1] for d in training_data])
    values = torch.stack([d[2] for d in training_data])
    
    for epoch in range(epochs):
        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0
        num_batches = 0
        
        # Shuffle Daten
        indices = torch.randperm(len(training_data))
        
        for i in range(0, len(training_data), batch_size):
            batch_indices = indices[i:i+batch_size]
            batch_states = states[batch_indices]
            batch_policies = policies[batch_indices]
            batch_values = values[batch_indices]
            
            # Forward pass
            policy_pred, value_pred = model(batch_states)
            
            # Policy-Loss (KL-Divergenz - AlphaZero Standard)
            # Anpassen der Policy-Größe falls nötig
            min_size = min(policy_pred.size(1), batch_policies.size(1))
            policy_pred_cropped = policy_pred[:, :min_size]
            batch_policies_cropped = batch_policies[:, :min_size]
            
            # Softmax über Policy-Logits für Wahrscheinlichkeitsverteilung
            policy_pred_probs = F.log_softmax(policy_pred_cropped, dim=1)
            
            # KL-Divergenz zwischen Target-Policy (MCTS) und Predicted-Policy
            policy_loss = F.kl_div(policy_pred_probs, batch_policies_cropped, reduction='batchmean')
            
            # Value-Loss (MSE)
            value_loss = F.mse_loss(value_pred.squeeze(), batch_values)
            
            # Gesamt-Loss (AlphaZero: beide Losses gleichgewichtet)
            loss = policy_loss + value_loss
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            total_policy_loss += policy_loss.item()
            total_value_loss += value_loss.item()
            num_batches += 1
        
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0
        avg_policy_loss = total_policy_loss / num_batches if num_batches > 0 else 0.0
        avg_value_loss = total_value_loss / num_batches if num_batches > 0 else 0.0
        print(f"Epoche {epoch+1}/{epochs} | Loss: {avg_loss:.4f} (Policy: {avg_policy_loss:.4f}, Value: {avg_value_loss:.4f})")


# In train_alphazero.py, main() Funktion:
def main():
    """Hauptfunktion für Training."""
    print("AlphaZero Training gestartet...")
    
    # Konfiguration
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Verwende Gerät: {device}")
    
    # Parameter können hier angepasst werden
    num_games = 20  # Anzahl Selbstspiele pro Iteration
    num_iterations = 2  # Anzahl Training-Iterationen
    num_simulations = 100  # MCTS-Simulationen pro Zug
    model_path = "models/alphazero_model.pth"
    
    # Zeige aktuelle Parameter an (WICHTIG: Zur Bestätigung)
    print(f"\n📊 Training-Parameter:")
    print(f"   - Spiele pro Iteration: {num_games}")
    print(f"   - Anzahl Iterationen: {num_iterations}")
    print(f"   - MCTS-Simulationen pro Zug: {num_simulations}")
    print(f"   - Training-Epochs pro Iteration: 10")
    print(f"   - Batch-Größe: 32")
    print(f"   - Lernrate: 0.001\n")
    
    # Erstelle Models-Ordner
    os.makedirs("models", exist_ok=True)
    
    # Initialisiere Engine OHNE Modell-Pfad (für neues Training)
    engine = AlphaZeroEngine(device=device)  # Kein model_path übergeben!
    model = engine.model
    model.train()
    
    # Replay Buffer für Datenspeicherung über mehrere Iterationen
    replay_buffer = SelfPlayBuffer(max_size=50000)
    
    # Training-Loop mit Fehlerbehandlung
    try:
        for iteration in range(num_iterations):
            print(f"\n=== Iteration {iteration+1}/{num_iterations} ===")
            
            # WICHTIG: Modell für MCTS muss im eval()-Modus sein (keine Gradienten)
            # Für Training wird es später auf train() gesetzt
            model.eval()
            engine.model = model
            
            # Sammle Trainingsdaten durch Selbstspiel
            all_training_data = []
            
            try:
                for game_num in range(num_games):
                    if (game_num + 1) % 1 == 0:  # Jedes Spiel ausgeben
                        print(f"Spiele Spiel {game_num+1}/{num_games}...")
                    
                    # Setze Modell auf eval() für MCTS-Simulationen
                    engine.model.eval()
                    training_data = self_play_game(engine, num_simulations=num_simulations)
                    
                    # Füge Daten zum Replay Buffer hinzu
                    for state, policy, value in training_data:
                        replay_buffer.add(state, policy, value)
                    
                    all_training_data.extend(training_data)
            except Exception as e:
                print(f"⚠️  Fehler beim Selbstspiel: {e}")
                raise
            
            print(f"Gesammelte Trainingsdaten: {len(all_training_data)} Positionen (neu)")
            print(f"Replay Buffer: {replay_buffer.size()} Positionen (gesamt)")
            
            # Berechne Statistiken für Effizienz-Kontrolle
            avg_positions_per_game = len(all_training_data) / num_games if num_games > 0 else 0
            print(f"📈 Statistiken: Ø {avg_positions_per_game:.1f} Positionen pro Spiel")
            
            if not all_training_data:
                print("⚠️  Keine Trainingsdaten gesammelt. Überspringe Training.")
                continue
            
            # Trainiere Modell mit neuem und altem Daten
            print("Trainiere Modell...")
            total_training_samples = len(all_training_data) + (min(len(all_training_data), replay_buffer.size()) if replay_buffer.size() > 0 else 0)
            print(f"   Training mit ~{total_training_samples} Positionen...")
            try:
                # Nutze sowohl neue als auch alte Daten für Training
                combined_data = all_training_data.copy()
                if replay_buffer.size() > 0:
                    # Sample alte Daten aus Replay Buffer (50% neue, 50% alte)
                    num_old_samples = min(len(all_training_data), replay_buffer.size())
                    if num_old_samples > 0:
                        old_states, old_policies, old_values = replay_buffer.sample(num_old_samples)
                        # Konvertiere zu Liste von Tupeln (wie all_training_data)
                        for i in range(old_states.size(0)):
                            combined_data.append((old_states[i:i+1], old_policies[i], old_values[i]))
                
                # WICHTIG: Setze Modell auf Trainingsmodus für Backpropagation
                model.train()
                train_model(model, combined_data, epochs=10, batch_size=32, lr=0.001)
            except Exception as e:
                print(f"⚠️  Fehler beim Training: {e}")
                raise
            
            # WICHTIG: Modell bleibt im Trainingsmodus für nächste Iteration
            # AlphaZero: Modell wird kontinuierlich trainiert, nur am Ende gespeichert
            print(f"Iteration {iteration+1} abgeschlossen. Training wird fortgesetzt...")
        
        # Speichere finales Modell (AlphaZero: Nur am Ende nach allen Iterationen)
        try:
            engine.save_model(model_path)
            print(f"\n✅ Training abgeschlossen! Finales Modell gespeichert: {model_path}")
        except Exception as e:
            print(f"\n❌ Fehler beim Speichern des finalen Modells: {e}")
            raise
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Training durch Benutzer unterbrochen!")
        # Speichere aktuellen Zustand
        checkpoint_path = f"models/alphazero_model_interrupted.pth"
        try:
            engine.save_model(checkpoint_path)
            print(f"✅ Checkpoint bei Unterbrechung gespeichert: {checkpoint_path}")
        except:
            print("⚠️  Konnte Checkpoint nicht speichern.")
        raise
    except Exception as e:
        print(f"\n❌ Kritischer Fehler während Training: {e}")
        # Versuche finalen Checkpoint zu speichern
        checkpoint_path = f"models/alphazero_model_error.pth"
        try:
            engine.save_model(checkpoint_path)
            print(f"✅ Notfall-Checkpoint gespeichert: {checkpoint_path}")
        except:
            print("❌ Konnte Notfall-Checkpoint nicht speichern!")
        raise


if __name__ == "__main__":
    main()
