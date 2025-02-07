import subprocess
import os
import pyttsx3
import time
engine_type="espeak" # "espeak", "windows" oder "openai"
if engine_type == "openai":
    import openai
    # Get the API key
    import loadapikey
    api_key=loadapikey.api_key
    # Initialize the OpenAI client with the loaded API key
    openai.api_key = api_key


def say(text,lang="de", speed=175, pitch=50):
    """
    Spricht Text aus, basierend auf der gewählten Engine (espeak, windows, openai).
    
    Args:
        text (str): Der zu sprechende Text.
        engine_type (str): Die Sprachsynthese-Engine ('espeak', 'windows', 'openai').
        lang (str): Sprachcode (z.B. 'de').
        speed (int): Sprechgeschwindigkeit.
        pitch (int): Tonhöhe (nur für eSpeak).
    
    Returns:
        float: Geschätzte Dauer der Sprachausgabe in Sekunden.
    """
    if engine_type == "espeak":
        return say_with_espeak(text, lang, speed, pitch)
    elif engine_type == "windows":
        return say_with_windows(text, speed,voice_index=0)
    elif engine_type == "openai":
        return say_with_openai(text)
    else:
        print("Ungültige Engine. Wähle 'espeak', 'windows' oder 'openai'.")
        return None

def say_with_espeak(text, lang="de", speed=175, pitch=50):
    """Spricht Text mit eSpeak nicht blockierend aus."""
    espeak_path = os.path.join(os.getcwd(), "eSpeak", "command_line", "espeak.exe")
    
    if not os.path.exists(espeak_path):
        print("eSpeak.exe wurde nicht gefunden!")
        return

    command = [
        espeak_path,
        f"-v{lang}",
        f"-s{speed}",
        f"-p{pitch}",
        text
    ]
    
    try:
        subprocess.Popen(command)
        print("Text wird gesprochen mit eSpeak...")
    except Exception as e:
        print(f"Fehler beim Ausführen von eSpeak: {e}")

    words = len(text.split())
    corrector = 1.2
    duration = words / speed * 60 * corrector
    return duration

def say_with_windows(text, speed=175, voice_index=0):
    """Spricht den Text mit einer bestimmten Windows-Stimme aus."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if 0 <= voice_index < len(voices):  # Sicherstellen, dass der Index existiert
        engine.setProperty('voice', voices[voice_index].id)
    else:
        print("Ungültiger Index, Standardstimme wird verwendet.")

    engine.setProperty('rate', speed)
    engine.say(text)
    engine.runAndWait()

def get_audio_duration(file_path):
    """Berechnet die Dauer einer MP3-Datei in Sekunden."""
    try:
        audio = MP3(file_path)
        return audio.info.length  # Länge in Sekunden
    except Exception as e:
        print(f"Fehler beim Abrufen der Audiodauer: {e}")
        return None

def say_with_openai(text, voice="alloy", model="tts-1"):
    """
    Nutzt OpenAI TTS, um den Text in Sprache umzuwandeln und die Dauer zurückzugeben.
    
    Args:
        text (str): Der zu sprechende Text.
        voice (str): Die gewünschte Stimme ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer').
        model (str): Das TTS-Modell ('tts-1' oder 'tts-1-hd').

    Returns:
        float: Die tatsächliche Länge der generierten Audiodatei in Sekunden oder None, falls ein Fehler auftritt.
    """
    try:
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        # Speichere die Datei als 'output.mp3'
        audio_file_path = "output.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(response.content)

        print(f"Audio gespeichert unter: {audio_file_path}")

        # Warte kurz, um sicherzustellen, dass die Datei vollständig gespeichert wurde
        time.sleep(1)

        # Berechne die tatsächliche Audiodauer
        duration = get_audio_duration(audio_file_path)

        # Falls die Dauer erfolgreich berechnet wurde, gebe sie zurück
        if duration is not None:
            print(f"Geschätzte Dauer: {duration:.2f} Sekunden")
        else:
            print("Konnte die Dauer der Audiodatei nicht berechnen.")

        # Spiele die Datei ab (unter Windows)
        os.system(f"start {audio_file_path}")  # Windows
        # os.system(f"afplay {audio_file_path}")  # macOS
        # os.system(f"mpg123 {audio_file_path}")  # Linux

        return duration
    except Exception as e:
        print(f"Fehler bei der OpenAI-TTS-Anfrage: {e}")
        return None

if __name__ == "__main__":

    duration = say("Hallo, ich bin ein Roboter! 42")
    print(f"Geschätzte Dauer: {duration:.2f} Sekunden")
    