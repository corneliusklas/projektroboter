import subprocess
import os

def say(text, lang="de", speed=175, pitch=50): #_with_espeak_non_blocking
    """Spricht Text mit eSpeak nicht blockierend aus."""
    espeak_path = os.path.join(
        os.getcwd(), "eSpeak", "command_line", "espeak.exe"
    )  # Passe den Pfad an, falls nötig
    
    if not os.path.exists(espeak_path):
        print("eSpeak.exe wurde nicht gefunden!")
        return

    # Baue den Befehl
    command = [
        espeak_path,
        f"-v{lang}",
        f"-s{speed}",
        f"-p{pitch}",
        text
    ]

    # Starte den Prozess nicht blockierend
    try:
        process = subprocess.Popen(command)
        print("Text wird gesprochen...")
    except Exception as e:
        print(f"Fehler beim Ausführen von eSpeak: {e}")

    #berechne die Dauer der Sprachausgabe
    words = len(text.split())
    corrector = 1.2
    duration = words / speed * 60 *corrector # Zeit in Sekunden
    return duration

#speak example if this is main
if __name__ == "__main__":
    # Beispielaufruf
    print(say("Hallo, ich bin ein Roboter!"))




"""
Windows Stimmen
import pyttsx3

# Initialisierung des Speech-Engines
engine = pyttsx3.init()

# Konfigurationen
speed = 175  # Wörter pro Minute
language = "de"  # Sprache (z. B. Deutsch)

# Setze die Geschwindigkeit und Sprache
engine.setProperty('rate', speed)
engine.setProperty('voice', 'german')  # 'deutsch' oder 'german', je nach Konfiguration

def say(text):
    %Führt die Sprachausgabe aus.
    %Args:
    %    text (str): Der Text, der gesprochen werden soll.
    %Returns:
    %    float: Die geschätzte Zeit der Sprachausgabe in Sekunden.
    
    print("Talking...")

    # Spreche den Text
    engine.say(text)
    engine.runAndWait()

    # Berechne die Dauer der Sprachausgabe
    words = len(text.split())
    duration = words / speed * 60  # Zeit in Sekunden
    print("Talking stopped.")
    return duration

#list voices
def list_voices():
    %Listet die verfügbaren Stimmen auf
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    for idx, voice in enumerate(voices):
        print(f"Index: {idx}, ID: {voice.id}, Name: {voice.name}")

# Teste die Funktion, wenn dieses Skript direkt ausgeführt wird
if __name__ == "__main__":
    duration = say("Hallo, ich bin ein Roboter!")
    print(f"Geschätzte Dauer: {duration:.2f} Sekunden")
    list_voices()
"""

"""alt, von der console: import os
#convert the answertext to speech with espeak external program
#https://espeak.sourceforge.net/commands.html, file: -w speech.wav
speed = 175 #words per minute
#talking=False
lan="de"

def say(text):
    print("Talking.")
    talking=True
    command = 'cmd /c "eSpeak\command_line\espeak -p 30 -v '+lan+'-m2 -s ' + str(speed)+' "'+text+'""'
    print("command: ", command)
    os.system(command )

    #os.system('cmd /c "C:\Programme\eSpeak\command_line\espeak -p 30 -v de-m2 -s ' + str(speed)+' "'+answer_text+'"' ) 
    print("Talking stopped.")
    #talking=False
    #estiomate the time to speak
    words = len(text.split())
    time = words / speed * 60
    return time
    
#speak example if this is main
if __name__ == "__main__":
        say("Hallo, Ich bin ein Roboter")222"""