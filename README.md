# AlphaZero-basierte KI für ein 7x7 Brettspiel

Dieses Projekt implementiert eine KI auf Basis von **AlphaZero**,  
kombiniert mit **Monte-Carlo Tree Search (MCTS)**, für ein komplexes Brettspiel
auf einem 7x7 Spielfeld.

Das Ziel war es, moderne KI-Techniken auf ein nicht-triviales Spiel mit
vielen Regeln und möglichen Zügen zu übertragen.

---

## Projektübersicht

- **Spieltyp:** Strategisches Brettspiel (7x7)
- **KI-Ansatz:** AlphaZero (Neural Network + MCTS)
- **Framework:** PyTorch
- **Training:** Self-Play
- **Ausführung:** CPU (GPU empfohlen)

---

## Zentrale Komponenten

### AlphaZeroNet (neural_network.py)
- Neuronales Netzwerk mit 17 Eingabekanälen
- 4 Convolutional Layers zur Mustererkennung
- Zwei Ausgaben:
  - **Policy Head:** Wahrscheinlichkeiten für mögliche Züge
  - **Value Head:** Bewertung der Spielposition (-1 bis 1)

### Monte-Carlo Tree Search (MCTS)
- Nutzt die Policy und Value des Netzwerks
- Führt mehrere Simulationen pro Zug durch
- Schwierigkeitsgrade über Anzahl der Iterationen steuerbar

---

## Eingabedarstellung (State Encoding)

Der Spielzustand wird als Tensor mit **17 Kanälen** kodiert, u. a.:
- Positionen und Typen der Steine beider Spieler
- Ausrichtungen der Steine
- Position des Pfarrers
- Aktueller Spieler und Spielphase

---

## Schwierigkeitsgrade

- **Einfach:** ca. 50 MCTS-Iterationen
- **Mittel:** ca. 300 MCTS-Iterationen
- **Stark:** 1000+ MCTS-Iterationen

---

## Bekannte Einschränkungen

- Training ohne GPU ist sehr langsam
- Volles AlphaZero-Niveau („Superhuman“) auf CPU nicht erreichbar
- Große Zustands- und Aktionsräume erschweren die Konvergenz

---

## Zukünftige Verbesserungen

- Training mit GPU (CUDA)
- Nutzung von Cloud-Rechnern für längere Trainingsläufe
- Optimierung des Move-Index-Mappings
- Erweiterte Evaluation gegen ältere Modelle

---

## Voraussetzungen

- Python 3.9+
- PyTorch
- NumPy

---

## Ausführen (Beispiel)

```bash
python main.py
```
# AlphaZero-basierte KI für ein 7x7 Brettspiel

![Spielverlauf](SpielVerlauf.png)

---

## 👥 Authors

Developed by:

- Roussel Dongmo  Jiometio
- Pharel Harold Nanseu Kombou  
- Pierre Tsoungui Junior  

University Project – 2025
