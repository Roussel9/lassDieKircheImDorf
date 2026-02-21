# neural_network.py - Korrigierte Version

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from game_logic import GameState
from config import ROWS, COLS

class AlphaZeroNet(nn.Module):
    """Neuronales Netzwerk für AlphaZero."""
    
    def __init__(self, input_channels=17, num_actions=None):
        super(AlphaZeroNet, self).__init__()
        
        # Berechne num_actions automatisch falls nicht angegeben
        if num_actions is None:
            # Berechne: Platzierungszüge (7*7*3*2) + Bewegungszüge (7*7*7*7-49) + Pfarrer (7*7)
            # = 294 + 2352 + 49 = 2695
            move_map = create_move_index_map()
            num_actions = len(move_map)
            print(f"📊 Neural Network: num_actions automatisch auf {num_actions} gesetzt")
        
        # Convolutional Layers für Board-Verarbeitung
        self.conv1 = nn.Conv2d(input_channels, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(256)
        
        self.conv4 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(512)
        
        # Policy Head
        self.policy_conv = nn.Conv2d(512, 32, kernel_size=1)
        self.policy_bn = nn.BatchNorm2d(32)
        self.policy_fc = nn.Linear(32 * ROWS * COLS, num_actions)
        
        # Value Head
        self.value_conv = nn.Conv2d(512, 32, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(32)
        self.value_fc1 = nn.Linear(32 * ROWS * COLS, 256)
        self.value_fc2 = nn.Linear(256, 1)
        
    def forward(self, x):
        # Board hat Shape: [batch_size, channels, height, width]
        # Erwartet: [batch, 17, 7, 7]
        
        # Prüfe Shape und passe an wenn nötig
        if len(x.shape) == 3:
            # Wenn [channels, height, width] -> [1, channels, height, width]
            x = x.unsqueeze(0)
        elif len(x.shape) == 2:
            # Wenn [height, width] -> [1, 1, height, width] und dann auf 17 Kanäle erweitern
            x = x.unsqueeze(0).unsqueeze(0)
            x = x.repeat(1, 17, 1, 1)
        
        # Prüfe ob korrekte Anzahl Kanäle
        if x.shape[1] != 17:
            # Falls falsche Anzahl Kanäle, auf 17 Kanäle anpassen
            if x.shape[1] < 17:
                # Pad mit Nullen
                padding = torch.zeros(x.shape[0], 17 - x.shape[1], x.shape[2], x.shape[3], device=x.device)
                x = torch.cat([x, padding], dim=1)
            else:
                # Schneide ab
                x = x[:, :17, :, :]
        
        # Shared Convolutional Layers
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        x = F.relu(self.bn4(self.conv4(x)))
        
        # Policy Head
        p = F.relu(self.policy_bn(self.policy_conv(x)))
        p = p.view(p.size(0), -1)
        policy = self.policy_fc(p)
        
        # Value Head
        v = F.relu(self.value_bn(self.value_conv(x)))
        v = v.view(v.size(0), -1)
        v = F.relu(self.value_fc1(v))
        value = torch.tanh(self.value_fc2(v))
        
        return policy, value.squeeze()

def encode_board_state(game_state, current_player):
    """
    Kodiert den Spielzustand in einen Tensor.
    
    Args:
        game_state: GameState Objekt
        current_player: Aktueller Spieler (1 oder 2)
    
    Returns:
        Tensor der Form [channels, rows, cols]
    """
    board = game_state.board
    channels = 17
    
    # Erstelle leeren Tensor
    tensor = torch.zeros(channels, ROWS, COLS, dtype=torch.float32)
    
    for r in range(ROWS):
        for c in range(COLS):
            stone = board[r][c]
            
            if stone:
                # Spieler 1 Features
                if stone.spieler == 1:
                    # Typ-spezifische Kanäle
                    if stone.typ == 'Haus':
                        tensor[0, r, c] = 1.0
                    elif stone.typ == 'Turm':
                        tensor[1, r, c] = 1.0
                    elif stone.typ == 'Schiff':
                        tensor[2, r, c] = 1.0
                    
                    # Ausrichtung
                    if stone.ausrichtung == 'vertikal':
                        tensor[3, r, c] = 1.0
                    else:
                        tensor[4, r, c] = 1.0
                
                # Spieler 2 Features
                elif stone.spieler == 2:
                    if stone.typ == 'Haus':
                        tensor[5, r, c] = 1.0
                    elif stone.typ == 'Turm':
                        tensor[6, r, c] = 1.0
                    elif stone.typ == 'Schiff':
                        tensor[7, r, c] = 1.0
                    
                    if stone.ausrichtung == 'vertikal':
                        tensor[8, r, c] = 1.0
                    else:
                        tensor[9, r, c] = 1.0
    
    # Pfarrer Position (Kanal 10)
    pr, pc = game_state.pfarrer_pos
    tensor[10, pr-1, pc-1] = 1.0
    
    # Kanäle, die für das gesamte Board gleich sind
    
    # Aktueller Spieler Kanal (11)
    if current_player == 1:
        tensor[11, :, :] = 1.0
    else:
        tensor[12, :, :] = 1.0
    
    # Ungelegte Steine Information (13, 14)
    unplaced_p1 = len(game_state.unplaced_pieces[1])
    unplaced_p2 = len(game_state.unplaced_pieces[2])
    
    tensor[13, :, :] = unplaced_p1 / 9.0  # Normalisiert
    tensor[14, :, :] = unplaced_p2 / 9.0
    
    # Spielphase (Place vs Move) (15)
    phase = 1.0 if unplaced_p1 > 0 or unplaced_p2 > 0 else 0.0
    tensor[15, :, :] = phase
    
    # Turn-Zähler (vereinfacht) (16)
    tensor[16, :, :] = game_state.turn / 2.0
    
    return tensor

def create_move_index_map():
    """
    Erstellt eine Mapping von Moves zu Indizes.
    
    Returns:
        Dictionary mit Move-String -> Index Mapping
    """
    move_index_map = {}
    index = 0
    
    # Platzierungszüge
    for r in range(1, ROWS + 1):
        for c in range(1, COLS + 1):
            for stone_type in ['Haus', 'Turm', 'Schiff']:
                for orientation in ['vertikal', 'horizontal']:
                    move_str = f"place_{r}_{c}_{stone_type}_{orientation}"
                    move_index_map[move_str] = index
                    index += 1
    
    # Bewegungszüge
    for r1 in range(1, ROWS + 1):
        for c1 in range(1, COLS + 1):
            for r2 in range(1, ROWS + 1):
                for c2 in range(1, COLS + 1):
                    if (r1, c1) != (r2, c2):
                        move_str = f"move_{r1}_{c1}_{r2}_{c2}"
                        move_index_map[move_str] = index
                        index += 1
    
    # Pfarrer-Austauschzüge
    for r in range(1, ROWS + 1):
        for c in range(1, COLS + 1):
            move_str = f"pfarrer_{r}_{c}"
            move_index_map[move_str] = index
            index += 1
    
    # Berechne und zeige Gesamtzahl
    total_moves = len(move_index_map)
    print(f"📊 Move-Index-Map: {total_moves} mögliche Züge erstellt")
    
    return move_index_map

def get_move_probabilities(policy_logits, valid_moves, move_index_map):
    """
    Extrahiert Wahrscheinlichkeiten für gültige Züge.
    
    Args:
        policy_logits: Logits vom neuronalen Netzwerk [batch, num_actions]
        valid_moves: Liste gültiger Züge
        move_index_map: Mapping von Moves zu Indizes
    
    Returns:
        Dictionary mit Move-String -> Wahrscheinlichkeit
    """
    # Softmax über alle Logits
    policy_probs = F.softmax(policy_logits, dim=-1)
    
    # Extrahiere Wahrscheinlichkeiten für gültige Züge
    move_probs = {}
    
    for move in valid_moves:
        # Erstelle einen String-Key für den Move
        if move['type'] == 'place':
            orientation = move.get('orientation', 'vertikal')
            move_str = f"place_{move['pos'][0]}_{move['pos'][1]}_{move['stone_type']}_{orientation}"
        elif move['type'] == 'move':
            move_str = f"move_{move['from'][0]}_{move['from'][1]}_{move['to'][0]}_{move['to'][1]}"
        elif move['type'] == 'pfarrer':
            move_str = f"pfarrer_{move['from'][0]}_{move['from'][1]}"
        else:
            continue
        
        if move_str in move_index_map:
            idx = move_index_map[move_str]
            # Prüfe ob Index im gültigen Bereich ist
            if idx < policy_probs.size(1):
                move_probs[move_str] = policy_probs[0, idx].item()
            else:
                # Index außerhalb des Bereichs - Fallback
                print(f"⚠️  WARNUNG: Move-Index {idx} außerhalb des Netzwerk-Bereichs (max: {policy_probs.size(1)-1})")
                move_probs[move_str] = 0.001
        else:
            # Fallback für unbekannte Züge
            move_probs[move_str] = 0.001
    
    # Normalisiere, damit Summe = 1
    total = sum(move_probs.values())
    if total > 0:
        for key in move_probs:
            move_probs[key] /= total
    else:
        # Gleichverteilung falls alle 0
        for key in move_probs:
            move_probs[key] = 1.0 / len(move_probs)
    
    return move_probs