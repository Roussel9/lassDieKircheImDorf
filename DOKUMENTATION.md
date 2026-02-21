# Ausführliche Projekt-Dokumentation

***Roussel Dongmo***

***Pharel Harold Nanseu Kombou***

***Pierre Tsoungui Junior***
## Lass die Kirche im Dorf - AlphaZero Implementation

---


# Projekt 2 – Eine KI für Brettspiele (AlphaZero)

# Inhaltsverzeichnis

1. [Ausführliche Projekt-Dokumentation](#ausführliche-projekt-dokumentation)
   - Autoren
     - Roussel Dongmo
     - Pharel Harold Nanseu Kombou
     - Pierre Tsoungui Junior

2. [Lass die Kirche im Dorf - AlphaZero Implementation](#lass-die-kirche-im-dorf---alphazero-implementation)

3. [Projekt 2 – Eine KI für Brettspiele (AlphaZero)](#projekt-2--eine-ki-für-brettspiele-alphazero)
   1. [Aufgabe 1: Verständnis des AlphaZero-Frameworks](#aufgabe-1-verständnis-des-alphazero-frameworks)
      - Ziel
      - Grundidee von AlphaZero
      - Zentrale Komponenten
      - Ergebnisse von AlphaZero
      - Fazit Aufgabe 1
   2. [Aufgabe 2: Tic-Tac-Toe mit AlphaZero](#aufgabe-2-tic-tac-toe-mit-alphazero)
      - Ziel
      - Vorgehen
      - Analyse des Frameworks
      - Ergebnis
      - Fazit Aufgabe 2
   3. [Aufgabe 3: Eigenes AlphaZero-Modell für Tic-Tac-Toe](#aufgabe-3-eigenes-alphazero-modell-für-tic-tac-toe)
      - Ziel
      - Vorgehen
      - Hardware
      - Beobachtungen
      - Ergebnisse
      - Fazit Aufgabe 3
   4. [Gesamtfazit zu Aufgabe 1–3](#gesamtfazit-zu-aufgabe-1–3)

4. [Aufgabe 4 bis 6 – Einleitung](#aufgabe-4-bis-6--einleitung)
   1. [Projektziel](#projektziel)
   2. [Projektkontext](#projektkontext)

5. [Spielregeln und Implementierung](#spielregeln-und-implementierung)
   1. [Implementierung der Spielregeln](#implementierung-der-spielregeln)
      - Analyse der Spielregeln
      - Datenrepräsentation
      - Umsetzung der Zugregeln
      - Implementierung der Siegbedingungen

6. [Testen der KI](#testen-der-ki)
   1. [Funktionale Tests](#funktionale-tests)
   2. [KI-Tests durch Probeläufe](#ki-tests-durch-probeläufe)
   3. [Vergleich der Schwierigkeitsgrade](#vergleich-der-schwierigkeitsgrade)

7. [Performance-Beschreibung und Bewertung](#performance-beschreibung-und-bewertung)
   1. [Bewertung der Performance](#bewertung-der-performance)
   2. [Gesamteinschätzung](#gesamteinschätzung)
   3. [Herausforderungen bei der Implementierung](#herausforderungen-bei-der-implementierung)

8. [KI-Implementierung](#ki-implementierung)
   1. [Algorithmus: MCTS (Monte Carlo Tree Search)](#algorithmus-mcts-monte-carlo-tree-search)
      - MCTS-Komponenten
         - Selection
         - Expansion
         - Simulation
         - Backpropagation
      - Implementierung
   2. [Schwierigkeitsgrade](#schwierigkeitsgrade)
      - Einfach
      - Mittel
      - Stark (AlphaZero-Style)
   3. [Bewertungsfunktion (`evaluate_score()`)](#bewertungsfunktion-evaluate_score)

9. [GUI-Implementierung](#gui-implementierung)
   1. [Technologie](#technologie)
   2. [Komponenten](#komponenten)
      - Spielfeld-Darstellung
      - Interaktion
      - Menü
   3. [Status-Anzeige](#status-anzeige)

10. [Testing](#testing)
    1. [Unit-Tests](#unit-tests)
    2. [Integrationstests](#integrationstests)
    3. [Edge Cases](#edge-cases)
    4. [Manuelle Tests](#manuelle-tests)

11. [Performance-Bewertung](#performance-bewertung)
    1. [Laufzeit-Analyse](#laufzeit-analyse)
       - KI-Zugzeiten
       - Speicherverbrauch
    2. [Skalierbarkeit](#skalierbarkeit)
    3. [Optimierungen](#optimierungen)

12. [Ergebnisse und Erkenntnisse](#ergebnisse-und-erkenntnisse)
    1. [Erfolgreiche Implementierung](#erfolgreiche-implementierung)
    2. [Herausforderungen](#herausforderungen)
    3. [Erkenntnisse](#erkenntnisse)
    4. [Verbesserungspotential / Limits](#verbesserungspotential-oder-limits)

13. [Screenshots und Beispiele](#screenshots-und-beispiele)
    1. [Spielstart](#spielstart)
    2. [Platzierungsphase](#platzierungsphase)
    3. [Bewegungsphase](#bewegungsphase)
    4. [Spiel-Ende](#spiel-ende)

14. [Fazit](#fazit)
    1. [Projektziele erreicht](#projektziele-erreicht)
    2. [Lernerfolg](#lernerfolg)
    3. [Ausblick](#ausblick)

15. [Anhang](#anhang)
    1. [Code-Struktur](#code-struktur)
    2. [Wichtige Funktionen](#wichtige-funktionen)


## Aufgabe 1: Verständnis des AlphaZero-Frameworks

### Ziel
Ziel dieser Aufgabe war es, das grundlegende Konzept von **AlphaZero** zu verstehen.  
Hierzu wurden die offiziellen Informationen von DeepMind studiert:

- AlphaZero: *Shedding new light on chess, shogi, and Go*  
  (DeepMind Blog)

### Grundidee von AlphaZero
AlphaZero ist ein allgemeines Lernverfahren für **deterministische, vollständig beobachtbare Nullsummenspiele**.  
Im Gegensatz zu klassischen Spiel-KIs verwendet AlphaZero:

- **kein menschliches Expertenwissen**
- **keine Eröffnungsbücher**
- **keine fest codierten Heuristiken**

Stattdessen lernt die KI ausschließlich durch **Selbstspiel**.

### Zentrale Komponenten
AlphaZero besteht aus drei Hauptbestandteilen:

1. **Neuronales Netzwerk**
   - Gibt eine *Policy* (Zugwahrscheinlichkeiten) aus
   - Gibt einen *Value* (Positionsbewertung) aus

2. **Monte-Carlo-Tree-Search (MCTS)**
   - Durchsucht den Spielbaum
   - Wird durch die Policy des neuronalen Netzes gelenkt

3. **Reinforcement Learning**
   - Die KI verbessert sich durch wiederholtes Selbstspiel

### Ergebnisse von AlphaZero
AlphaZero konnte bekannte Programme wie:
- Stockfish (Schach)
- Elmo (Shogi)
- andere Go-Engines

in kurzer Zeit übertreffen – ausschließlich durch Selbstlernen.

### Fazit Aufgabe 1
AlphaZero kombiniert **Suche (MCTS)** mit **Lernen (Neuronales Netz)** und stellt damit einen grundlegenden Paradigmenwechsel in der Spiele-KI dar.

---

## Aufgabe 2: Tic-Tac-Toe mit AlphaZero

### Ziel
In dieser Aufgabe sollte eine **existierende, vereinfachte AlphaZero-Implementierung** genutzt werden, um ein erstes Verständnis für Struktur und Ablauf des Frameworks zu entwickeln.

### Vorgehen
- Das Repository  
  https://github.com/suragnair/alpha-zero-general  
  wurde lokal geklont
- Die Installation erfolgte gemäß der Anleitung in der `README.md`
- Das enthaltene Tic-Tac-Toe-Beispiel wurde ausgeführt

### Analyse des Frameworks
Das Repository ist modular aufgebaut und trennt klar zwischen:

- **Spielregeln** (Game-Klasse)
- **Neuronales Netzwerk**
- **MCTS-Logik**
- **Training durch Selbstspiel**

Besonders wichtig war das Verständnis:
- wie Spielzustände kodiert werden
- wie MCTS mit dem neuronalen Netzwerk interagiert
- wie Trainingsdaten durch Selbstspiel entstehen

### Ergebnis
Das Tic-Tac-Toe-Beispiel konnte erfolgreich gestartet werden.  
Die KI lernte bereits nach kurzer Trainingszeit, optimal zu spielen.

### Fazit Aufgabe 2
Die Aufgabe diente als **Einstieg in das AlphaZero-Framework** und bildete die Grundlage für eigene Erweiterungen in späteren Aufgaben.

---

## Aufgabe 3: Eigenes AlphaZero-Modell für Tic-Tac-Toe

### Ziel
Ziel war es, ein **eigenes neuronales Netzwerk** für Tic-Tac-Toe mit AlphaZero zu trainieren.

### Vorgehen
- Nutzung der im Repository enthaltenen Trainingsskripte
- Durchführung von Selbstspielen mit MCTS
- Training des neuronalen Netzes mit:
  - Policy-Loss (KL-Divergenz)
  - Value-Loss (Mean Squared Error)

### Hardware
- Training wurde auf:
  - der **CPU**
  durchgeführt

### Beobachtungen
- Bereits nach wenigen Iterationen:
  - verbesserte sich die Zugauswahl deutlich
  - reduzierte sich die Anzahl schlechter Züge
- Die KI lernte:
  - Gewinnstrategien
  - das Erzwingen von Unentschieden

### Ergebnisse
Das trainierte Modell konnte:
- gegen zufällige Spieler zuverlässig gewinnen
- gegen sich selbst stabil spielen

### Fazit Aufgabe 3
Die Aufgabe zeigte, dass AlphaZero auch für einfache Spiele effektiv funktioniert und vollständig ohne menschliches Vorwissen lernt.

---

## Gesamtfazit zu Aufgabe 1–3
Die ersten drei Aufgaben vermittelten ein solides Verständnis von:

- der Funktionsweise von AlphaZero
- dem Zusammenspiel von MCTS und neuronalen Netzen
- dem Trainingsprozess durch Selbstspiel

Dieses Wissen bildete die Grundlage für die Implementierung einer eigenen AlphaZero-KI für das Spiel  
**„Lass die Kirche im Dorf“**.

## (Aufgabe 4 bis 6 ) 1. Einleitung

### 1.1 Projektziel

Dieses Projekt implementiert eine KI für das Strategiespiel "Lass die Kirche im Dorf" basierend auf AlphaZero-Algorithmen. Das Ziel war es, ein autodidaktisches Computerprogramm zu entwickeln, das das Spiel einzig anhand der Spielregeln und durch intensives Spielen gegen sich selbst erlernt.



### 1.2 Projektkontext

Das Projekt wurde im Rahmen eines Data Science Kurses durchgeführt und umfasst:
- Verständnis des AlphaZero-Frameworks
- Implementierung der Spielregeln für "Lass die Kirche im Dorf"
- Entwicklung einer KI mit verschiedenen Schwierigkeitsgraden
- Erstellung einer benutzerfreundlichen GUI
- Testing und Performance-Bewertung

---

## 2. Spielregeln und Implementierung


## Implementierung der Spielregeln

Die Implementierung der Spielregeln von *„Lass die Kirche im Dorf“* stellte den zentralen technischen Bestandteil des Projekts dar.  
Da die KI das Spiel nicht „kennt“, mussten sämtliche Regeln vollständig und eindeutig im Code abgebildet werden.

### Analyse der Spielregeln

Zu Beginn wurden die offiziellen Spielregeln analysiert und in klar definierte Teilaspekte zerlegt:

- Aufbau des Spielfelds (7x7 Raster)
- Unterschiedliche Spielsteine (Turm, Kirchenschiff, Haus)
- Drehende Steine nach jeder Bewegung
- Gleitbewegungen abhängig von der Ausrichtung
- Sonderregel des Pfarrertauschs
- Mehrteilige Siegbedingungen

Diese Zerlegung war notwendig, um die Regeln in einzelne logische Prüfungen zu übersetzen.

### Datenrepräsentation

Das Spielfeld wurde als zweidimensionale 7x7-Datenstruktur implementiert.  
Jeder Spielstein wird durch eine Klasse beschrieben, die folgende Eigenschaften speichert:

- Zugehöriger Spieler
- Typ des Steins (Turm, Schiff, Haus)
- Aktuelle Ausrichtung (horizontal oder vertikal)

Zusätzlich werden der aktuelle Spielerzug, die Position des Pfarrers sowie noch nicht platzierte Steine im Spielzustand verwaltet.

### Umsetzung der Zugregeln

Der wichtigste Schritt war die Implementierung der Methode `get_valid_moves()`.  
Diese Funktion berechnet für jeden Spielzustand alle legalen Züge und stellt sie der KI in strukturierter Form zur Verfügung.

Dabei mussten mehrere Sonderregeln berücksichtigt werden:

- Platzierung von Turm und Kirchenschiff nur auf Ecken
- Diagonale Sperrregel bei Kirchenteilen
- Hausplatzierung ohne orthogonale Nachbarschaft zu eigenen Steinen
- Gleitbewegung nur entlang der aktuellen Ausrichtung
- Blockade-Erkennung durch andere Steine oder den Pfarrer
- Automatische Drehung eines Steins nach jedem Zug
- Pfarrertausch ausschließlich bei blockierten Steinen

Durch diese Methode wird sichergestellt, dass weder Mensch noch KI ungültige Züge ausführen können.

### Implementierung der Siegbedingungen

Die Siegprüfung erfolgt in mehreren Schritten:

1. Überprüfung der Mindestanzahl von neun eigenen Steinen
2. Sicherstellung, dass sowohl Turm als auch Kirchenschiff vorhanden sind
3. Kontrolle, dass sich die Kirche nicht am Rand des Spielfelds befindet
4. Prüfung der vollständigen Zusammenhängendheit aller eigenen Steine  
   (mittels Breitensuche / BFS)

Erst wenn alle Bedingungen erfüllt sind, wird ein Spielsieg erkannt.

---

## Testen der KI

Das Testen der KI erfolgte in mehreren Stufen, um sowohl die Korrektheit der Spielregeln als auch die Spielstärke der KI zu überprüfen.

### Funktionale Tests

Zunächst wurden die Spielregeln isoliert getestet:

- Platzierung von Steinen nur auf erlaubten Feldern
- Korrekte Drehung der Steine nach Bewegungen
- Blockade-Erkennung und Pfarrertausch
- Verhinderung ungültiger Züge
- Korrekte Erkennung von Spielsiegen

Diese Tests wurden sowohl automatisiert (durch Testskripte) als auch manuell durchgeführt.

### KI-Tests durch Probeläufe

Die KI wurde anschließend durch zahlreiche Testspiele evaluiert:

- Mensch gegen KI
- KI gegen KI
- Vergleich verschiedener Schwierigkeitsgrade

Dabei wurde überprüft, ob:
- die KI ausschließlich gültige Züge ausführt
- die KI auf unterschiedliche Spielsituationen sinnvoll reagiert
- höhere Schwierigkeitsgrade zu stärkerem Spielverhalten führen

### Vergleich der Schwierigkeitsgrade

Die Schwierigkeitsstufen unterscheiden sich hauptsächlich durch:
- Anzahl der MCTS-Simulationen
- Maximale Suchtiefe
- Grad an Zufälligkeit bei der Zugauswahl

Dies ermöglichte eine klare Abstufung der Spielstärke bei gleichbleibender Spiellogik.

---

## Performance-Beschreibung und Bewertung



### Bewertung der Performance

**Positive Aspekte:**
- Sehr schnelle Reaktionszeiten auf niedrigen Schwierigkeitsgraden
- Stabiler Spielablauf ohne Abstürze
- KI trifft mit steigender Rechenzeit deutlich bessere Entscheidungen

**Einschränkungen:**
- Hohe Schwierigkeitsgrade führen zu spürbaren Wartezeiten
- MCTS läuft ausschließlich auf der CPU
- Keine Parallelisierung der Simulationen

### Gesamteinschätzung

Die Performance der Anwendung ist für ein universitäres Projekt sehr gut und ausreichend für interaktive Spiele.  
Insbesondere der Zusammenhang zwischen Rechenzeit und Spielstärke ist klar erkennbar und nachvollziehbar.

Für zukünftige Verbesserungen wäre eine vollständige AlphaZero-Implementierung mit neuronalen Netzen und GPU-Unterstützung sinnvoll, um sowohl Spielstärke als auch Effizienz weiter zu steigern.


###  Herausforderungen bei der Implementierung

1. **Drehende Häuser**: Die Ausrichtung muss bei jedem Zug gespeichert und aktualisiert werden
2. **Gleitbewegung**: Steine können mehrere Felder gleiten, müssen aber bei Blockaden stoppen
3. **Pfarrertausch**: Komplexe Logik zur Erkennung blockierter Steine
4. **Diagonale Regel**: Türme/Schiffe dürfen nicht diagonal gegenüber dem Gegner stehen

---

## 3. KI-Implementierung

### 3.1 Algorithmus: MCTS (Monte Carlo Tree Search)

Da eine vollständige AlphaZero-Implementierung mit neuronalen Netzen sehr rechenintensiv ist, wurde zunächst eine **MCTS-basierte KI** implementiert, die ähnliche Prinzipien verwendet.

#### 3.1.1 MCTS-Komponenten

**1. Selection (Auswahl)**
- Starte von der Wurzel
- Wähle Kindknoten basierend auf UCT-Formel:
```
UCT = wins/visits + C * sqrt(ln(parent_visits) / visits)
```
- C = 1.41 (Exploration-Konstante)

**2. Expansion (Erweiterung)**
- Wenn unerforschte Züge vorhanden, erweitere den Baum
- Erstelle neuen Knoten für einen zufälligen unerforschten Zug

**3. Simulation (Rollout)**
- Simuliere zufällige Züge bis zu einer bestimmten Tiefe
- Verwende heuristische Bewertung am Ende

**4. Backpropagation (Rückpropagierung)**
- Aktualisiere Statistiken (wins, visits) entlang des Pfads zur Wurzel

#### 3.1.2 Implementierung

```python
class MCTSNode:
    def __init__(self, state_matrix, parent=None, move=None):
        self.state = state_matrix
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = None

    def uct_select_child(self):
        # UCT-Formel für beste Kindauswahl
        return max(self.children, key=lambda c: 
            c.wins/c.visits + 1.41 * sqrt(log(self.visits)/c.visits))
```

### 3.2 Schwierigkeitsgrade

#### 3.2.1 Einfach

- **Iterationen**: 50
- **Tiefe**: 5
- **Strategie**: Einfache heuristische Bewertung
- **Zugzeit**: < 0.1 Sekunden

**Bewertungsheuristik:**
- Zentrum bevorzugen
- Blockierte Steine befreien
- Gegner blockieren

#### 3.2.2 Mittel

- **Iterationen**: 300
- **Tiefe**: 10
- **Strategie**: Verbesserte strategische Bewertung
- **Zugzeit**: 0.5-1 Sekunde

**Erweiterte Heuristiken:**
- Cluster-Bildung (diagonale Nachbarn)
- Strategische Hausplatzierung
- Bewegungsfreiheit bewerten
- Top-3-Züge mit Wahrscheinlichkeitsverteilung (60%/30%/10%)

#### 3.2.3 Stark (AlphaZero-Style)

- **Iterationen**: 1000
- **Tiefe**: 25
- **Strategie**: Tiefe MCTS-Simulationen
- **Zugzeit**: 2-5 Sekunden

**Features:**
- Immer bester Zug (keine Zufälligkeit)
- Erweiterte Bewertungsfunktion
- Tiefe Vorausschau

### 3.3 Bewertungsfunktion (`evaluate_score()`)

Die Bewertungsfunktion bewertet einen Spielzustand aus Sicht eines Spielers:

```python
def evaluate_score(self, matrix, player_id):
    score = 0
    
    # 1. Kirche-Sicherheit
    # Bonus: Kirche im Zentrum
    # Malus: Kirche am Rand
    
    # 2. Mobilität (Liberty)
    # Mehr freie Nachbarfelder = besser
    
    # 3. Konnexität
    # Mehr Verbindungen zwischen eigenen Steinen = besser
    
    # 4. Pfarrer-Position
    # Pfarrer nahe gegnerischen Steinen = Blockade-Potential
    
    return score
```

**Gewichtungen:**
- Kirche-Sicherheit: ±60 bis ±200 Punkte
- Mobilität: ±2 bis ±5 Punkte pro Freiheit
- Konnexität: +10 pro eigene Verbindung, -25 pro gegnerische Verbindung
- Pfarrer-Position: +15 für Blockade-Potential

---

## 4. GUI-Implementierung

### 4.1 Technologie

- **Framework**: Tkinter (Python Standard-Bibliothek)
- **Canvas**: Für Spielfeld-Darstellung
- **Event-Handling**: Mausklicks für Züge

### 4.2 Komponenten

#### 4.2.1 Spielfeld-Darstellung

- **7x7 Gitter**: Graue Linien auf beigem Hintergrund
- **Steine**: 
  - Häuser: Pentagone (orientiert)
  - Türme: Dreiecke (orientiert)
  - Schiffe: Kreise mit Doppelpfeil
- **Pfarrer**: Schwarzer Pion in der Mitte
- **Farben**: 
  - Spieler 1: Helles Holz (#E3C699)
  - Spieler 2: Dunkles Holz (#5D4037)

#### 4.2.2 Interaktion

**Platzierung:**
1. Klick auf freies Feld
2. Popup für Ausrichtung wählen
3. Stein wird platziert

**Bewegung:**
1. Klick auf eigenen Stein (Auswahl)
2. Klick auf Zielposition
3. Stein gleitet und dreht sich

**Pfarrertausch:**
1. Klick auf Pfarrer
2. Klick auf blockierten Stein
3. Tausch wird ausgeführt

#### 4.2.3 Menü

- **Spiel**: Neues Spiel, Beenden
- **Hilfe**: Spielregeln, Über

### 4.3 Status-Anzeige

- Titelzeile zeigt: Aktueller Spieler, Phase, KI-Schwierigkeit
- Statusleiste (Debug-Modus): Aktuelle Aktionen

---

## 5. Testing

### 5.1 Unit-Tests

**Getestete Komponenten:**

1. **Spielregeln:**
   -  Platzierung von Türmen/Schiffen auf Ecken
   -  Diagonale Regel für Kirchenteile
   -  Haus-Platzierung ohne eigene Nachbarn
   -  Gleitbewegung in Ausrichtung
   -  Blockade-Erkennung
   -  Pfarrertausch

2. **Siegbedingungen:**
   
   -  Zusammenhängend (BFS)
   -  Kirche nicht am Rand
   

3. **KI:**
   -  MCTS-Baum-Erstellung
   -  UCT-Auswahl
   -  Bewertungsfunktion
   -  Verschiedene Schwierigkeitsgrade

### 5.2 Integrationstests

**Getestete Szenarien:**

1. **Vollständiges Spiel Mensch vs Mensch:**
   -  Platzierungsphase funktioniert
   -  Bewegungsphase funktioniert
   -  Siegbedingung wird erkannt
   -  Spielende wird korrekt angezeigt

2. **Spiel gegen KI:**
   -  KI macht gültige Züge
   -  Verschiedene Schwierigkeitsgrade funktionieren
   -  KI reagiert auf Spielzustand

### 5.3 Edge Cases

**Getestete Grenzfälle:**

1. **Blockierte Steine:**
   - Erkennung funktioniert korrekt
   - Pfarrertausch nur für blockierte Steine

2. **Spielende:**
   -  Sieg wird sofort erkannt
   -  Keine Züge mehr möglich

3. **Grenzen des Spielfelds:**
   -  Steine können nicht über Rand gleiten
   -  Platzierung nur auf gültigen Feldern

### 5.4 Manuelle Tests

**Durchgeführte Tests:**

1. **Spielablauf:**
   - Mehrere vollständige Spiele gespielt
   - Verschiedene Strategien getestet
   - KI-Verhalten beobachtet

2. **GUI:**
   - Alle Buttons getestet
   - Menü-Funktionen getestet
   - Fehlerbehandlung getestet

---

## 6. Performance-Bewertung

### 6.1 Laufzeit-Analyse

#### 6.1.1 KI-Zugzeiten

| Schwierigkeit | Iterationen | Durchschnittliche Zugzeit | Max. Zugzeit |
|---------------|-------------|---------------------------|--------------|
| Einfach       | 50          | < 0.1s                    | 0.2s         |
| Mittel        | 300         | 0.5-1s                    | 1.5s         |
| Stark         | 1000        | 2-5s                      | 8s           |

**Faktoren:**
- Anzahl möglicher Züge
- Rechenleistung (CPU)
- Tiefe der Simulation

#### 6.1.2 Speicherverbrauch

- **Spielzustand**: ~1 KB pro Zustand
- **MCTS-Baum**: ~10-100 KB (abhängig von Iterationen)
- **GUI**: ~5-10 MB (Tkinter)

### 6.2 Skalierbarkeit

**Probleme:**
- MCTS skaliert nicht gut mit vielen möglichen Zügen
- Tiefe Simulationen werden langsam

**Lösungen:**
- Begrenzte Tiefe
- Frühe Terminierung bei Gewinn
- Optimierte Datenstrukturen

### 6.3 Optimierungen

**Implementierte Optimierungen:**

1. **Shallow Copy**: Schnelle Kopien des Spielfelds
2. **Frühe Terminierung**: Stoppe bei Gewinn
3. **Caching**: Bewertungen zwischenspeichern (könnte erweitert werden)



---

## 7. Ergebnisse und Erkenntnisse

### 7.1 Erfolgreiche Implementierung

 **Vollständige Spielregeln**: Alle Regeln korrekt implementiert
 **Funktionierende KI**: Drei Schwierigkeitsgrade spielbar
 **Benutzerfreundliche GUI**: Intuitive Bedienung
 **Robuste Validierung**: Keine ungültigen Züge möglich

### 7.2 Herausforderungen

1. **Komplexe Spielregeln**: 
   - Pfarrertausch-Logik war komplex
   - Gleitbewegung mit Blockaden

2. **KI-Performance**:
   - Balance zwischen Stärke und Geschwindigkeit
   - MCTS ohne NN ist limitiert

3. **GUI-Design**:
   - Orientierung der Steine visuell darstellen
   - Benutzerfreundliche Pfarrertausch-Interaktion

### 7.3 Erkenntnisse

1. **MCTS funktioniert**: Auch ohne neuronale Netze liefert MCTS gute Ergebnisse
2. **Heuristiken wichtig**: Gute Bewertungsfunktion ist entscheidend
3. **GUI essentiell**: Visuelle Darstellung macht Testing viel einfacher

### 7.4 Verbesserungspotential(oder Limits)

1. **AlphaZero vollständig**: Neuronale Netze für Bewertung und Policy
2. **
3. **Erweiterte Strategien**: Opening-Book, Endgame-Datenbank
4. **Mehr Varianten**: Größeres Spielfeld, zwei Pfarrer

---

## 8. Screenshots und Beispiele

### 8.1 Spielstart

![](Niveau_AusWahl.PNG)

### 8.2 Platzierungsphase

![](Anfang1.PNG)

### 8.3 Bewegungsphase

![](SpielVerlauf.PNG)



### 8.4 Spiel-Ende



![](end.PNG)


---

## 9. Fazit

### 9.1 Projektziele erreicht

 Spielregeln vollständig implementiert
 KI mit verschiedenen Schwierigkeitsgraden
 Funktionierende GUI
 Dokumentation erstellt

### 9.2 Lernerfolg

- Verständnis von AlphaZero/MCTS-Algorithmen
- Implementierung komplexer Spielregeln
- GUI-Entwicklung mit Tkinter
- Performance-Optimierung

### 9.3 Ausblick

Für zukünftige Verbesserungen:
- Vollständige AlphaZero-Implementierung mit neuronalen Netzen
- GPU-Training für bessere KI
- Erweiterte Spielvarianten
- Online-Multiplayer

---

## 10. Anhang

### 10.1 Code-Struktur

```
game_logic.py:
  - Spielstein (Klasse)
  - GameState (Klasse)
    - get_valid_moves()
    - apply_move()
    - check_win()
    - evaluate_score()

ai_engine.py:
  - MCTSNode (Klasse)
  - AIEngine (Klasse)
    - get_move()
    - run_mcts()

gui.py:
  - GameGUI (Klasse)
    - draw_board()
    - on_click()
    - execute_move()
```

### 10.2 Wichtige Funktionen

**Spielregeln:**
- `get_valid_moves()`: Berechnet alle erlaubten Züge
- `apply_move()`: Führt einen Zug aus
- `check_win()`: Prüft Siegbedingungen

**KI:**
- `run_mcts()`: Führt MCTS-Algorithmus aus
- `evaluate_score()`: Bewertet Spielzustand
- `uct_select_child()`: Wählt besten Kindknoten

**GUI:**
- `draw_board()`: Zeichnet Spielfeld
- `on_click()`: Behandelt Mausklicks
- `execute_move()`: Führt Zug aus und aktualisiert GUI


