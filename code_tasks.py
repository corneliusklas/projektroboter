import subprocess

def force_update_repo():
    try:
        # Lokale Änderungen verwerfen
        subprocess.run(["git", "reset", "--hard"], check=True)

        # Die neuesten Änderungen aus dem Remote-Repository holen
        subprocess.run(["git", "pull", "origin", "main"], check=True)

        print("Git-Update erfolgreich abgeschlossen (alle Aenderungen verworfen).")
    
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Git-Update: {e}")

if __name__ == "__main__":
    force_update_repo()
