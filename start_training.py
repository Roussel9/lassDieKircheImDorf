# start_training.py
# Einfaches Skript zum Starten des Trainings mit verschiedenen Optionen

import sys
import os

def print_menu():
    """Zeigt das Hauptmenü."""
    print("\n" + "=" * 60)
    print("ALPHAZERO TRAINING - LASS DIE KIRCHE IM DORF")
    print("=" * 60)
    print("\nWählen Sie eine Option:")
    print()
    print("1. 🧪 SCHNELLER TEST (5 Spiele, 1 Iteration)")
    print("   ⏱️  Dauer: 10-12 Minuten")
    print("   💡 Empfohlen zum ersten Test")
    print()
    print("2. 📚 MITTLERES TRAINING (20 Spiele, 2 Iterationen)")
    print("   ⏱️  Dauer: 15-25 Minuten")
    print("   💡 Gute Balance zwischen Zeit und Qualität")
    print()
    print("3. 🚀 VOLLSTÄNDIGES TRAINING (50 Spiele, 5 Iterationen)")
    print("   ⏱️  Dauer: 40-90 Minuten (CPU) ")
    print("   💡 Beste Ergebnisse")
    print()
    print("4. ⚙️  EIGENE EINSTELLUNGEN")
    print("   💡 Passen Sie Parameter manuell an")
    print()
    print("5. ❌ Abbrechen")
    print()
    print("=" * 60)

def get_choice():
    """Fragt nach Benutzerauswahl."""
    while True:
        try:
            choice = input("Ihre Wahl (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("⚠️  Bitte wählen Sie 1, 2, 3, 4 oder 5")
        except KeyboardInterrupt:
            print("\n\nAbgebrochen.")
            sys.exit(0)

def run_training(num_games, num_iterations, num_simulations):
    """Startet das Training mit gegebenen Parametern."""
    print("\n" + "=" * 60)
    print("TRAINING GESTARTET")
    print("=" * 60)
    print(f"\nKonfiguration:")
    print(f"  - Spiele pro Iteration: {num_games}")
    print(f"  - Iterationen: {num_iterations}")
    print(f"  - Simulationen pro Zug: {num_simulations}")
    
    # Prüfe ob train_alphazero.py existiert
    if not os.path.exists('train_alphazero.py'):
        print("\n❌ FEHLER: train_alphazero.py nicht gefunden!")
        print("   Stellen Sie sicher, dass Sie im richtigen Ordner sind.")
        return False
    
    # Modifiziere train_alphazero.py temporär
    print("\n📝 Konfiguriere Training-Parameter...")
    
    try:
        # Lese train_alphazero.py
        with open('train_alphazero.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ersetze Parameter
        import re
        
        # Finde und ersetze num_games
        content = re.sub(
            r'num_games\s*=\s*\d+',
            f'num_games = {num_games}',
            content
        )
        
        # Finde und ersetze num_iterations
        content = re.sub(
            r'num_iterations\s*=\s*\d+',
            f'num_iterations = {num_iterations}',
            content
        )
        
        # Finde und ersetze num_simulations
        content = re.sub(
            r'num_simulations\s*=\s*\d+',
            f'num_simulations = {num_simulations}',
            content
        )
        
        # Schreibe zurück
        with open('train_alphazero.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Parameter konfiguriert")
        
    except Exception as e:
        print(f"⚠️  Konnte Parameter nicht automatisch ändern: {e}")
        print("   Bitte ändern Sie manuell in train_alphazero.py:")
        print(f"   - num_games = {num_games}")
        print(f"   - num_iterations = {num_iterations}")
        print(f"   - num_simulations = {num_simulations}")
        input("\nDrücken Sie Enter, wenn Sie fertig sind...")
    
    # Starte Training
    print("\n🚀 Starte Training...")
    print("   (Dies kann eine Weile dauern. Sie können die Ausgabe verfolgen.)")
    print()
    
    import subprocess
    try:
        result = subprocess.run([sys.executable, 'train_alphazero.py'], check=True)
        print("\n✅ Training erfolgreich abgeschlossen!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training fehlgeschlagen: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n⚠️  Training abgebrochen.")
        return False

def custom_settings():
    """Fragt nach benutzerdefinierten Einstellungen."""
    print("\n" + "=" * 60)
    print("EIGENE EINSTELLUNGEN")
    print("=" * 60)
    print()
    
    try:
        num_games = int(input("Anzahl Spiele pro Iteration (Empfehlung: 20-50): "))
        num_iterations = int(input("Anzahl Iterationen (Empfehlung: 2-5): "))
        num_simulations = int(input("Simulationen pro Zug (Empfehlung: 50-200): "))
        
        if num_games < 1 or num_iterations < 1 or num_simulations < 1:
            print("❌ Alle Werte müssen größer als 0 sein!")
            return False
        
        print(f"\n📊 Ihre Konfiguration:")
        print(f"   Spiele: {num_games}")
        print(f"   Iterationen: {num_iterations}")
        print(f"   Simulationen: {num_simulations}")
        
        confirm = input("\nTraining starten? (j/n): ").strip().lower()
        if confirm in ['j', 'ja', 'y', 'yes']:
            return run_training(num_games, num_iterations, num_simulations)
        else:
            print("Abgebrochen.")
            return False
            
    except ValueError:
        print("❌ Bitte geben Sie gültige Zahlen ein!")
        return False
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        return False

def main():
    """Hauptfunktion."""
    # Prüfe ob train_alphazero.py existiert
    if not os.path.exists('train_alphazero.py'):
        print("\n❌ FEHLER: train_alphazero.py nicht gefunden!")
        print("   Stellen Sie sicher, dass Sie im richtigen Ordner sind.")
        input("\nDrücken Sie Enter zum Beenden...")
        return
    
    # Prüfe Models-Ordner
    if not os.path.exists('models'):
        print("\n📁 Erstelle models/ Ordner...")
        os.makedirs('models', exist_ok=True)
        print("✅ models/ Ordner erstellt")
    
    while True:
        print_menu()
        choice = get_choice()
        
        if choice == '1':
            # Schneller Test
            success = run_training(5, 1, 50)
            break
        elif choice == '2':
            # Mittleres Training
            success = run_training(20, 2, 100)
            break
        elif choice == '3':
            # Vollständiges Training
            print("\n⚠️  WICHTIG: Dies kann 30-90 Minuten dauern (CPU) oder 15-30 Min (GPU)!")
            confirm = input("Wirklich starten? (j/n): ").strip().lower()
            if confirm in ['j', 'ja', 'y', 'yes']:
                success = run_training(50, 5, 100)
                break
            else:
                print("Abgebrochen.")
                continue
        elif choice == '4':
            # Eigene Einstellungen
            custom_settings()
            break
        elif choice == '5':
            print("\nAbgebrochen.")
            return
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TRAINING ABGESCHLOSSEN!")
        print("\nSie können jetzt:")
        print("   python main.py")
        print("   ausführen, um gegen die trainierte KI zu spielen.")
    else:
        print("❌ Training konnte nicht abgeschlossen werden.")
        print("   Prüfen Sie die Fehlermeldungen oben.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(0)
