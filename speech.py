import subprocess
import os
import pyttsx3
import pygame

engine = None  # Globale Variable für das pyttsx3-Objekt

engine_type="native" # "espeak_win", "native" oder "openai"
if engine_type == "openai":
    import openai
    # Get the API key
    import loadapikey
    api_key=loadapikey.api_key
    # Initialize the OpenAI client with the loaded API key
    openai.api_key = api_key

def play_audio_pygame(file_path):
    """
    Spielt eine Audio-Datei mit pygame im Hintergrund ab und gibt die Dauer zurück.
    
    Args:
        file_path (str): Pfad zur Audio-Datei (WAV oder MP3).
    
    Returns:
        float: Die Dauer der Datei in Sekunden.
    """
    # Pygame initialisieren
    pygame.mixer.init()
    
    # Datei laden
    pygame.mixer.music.load(file_path)
    
    # Dauer berechnen
    sound = pygame.mixer.Sound(file_path)
    duration = sound.get_length()  # Gibt die Dauer in Sekunden zurück
    
    # Abspielen
    pygame.mixer.music.play()

    return duration

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
    if engine_type == "espeak_win":
        return say_with_espeak_win(text, lang, speed, pitch)
    elif engine_type == "native":
        return say_with_native(text, speed,voice_index=0, lang=lang, pitch=pitch)
    elif engine_type == "openai":
        return say_with_openai(text)
    else:
        print("Ungültige Engine. Wähle 'espeak', 'windows' oder 'openai'.")
        return None

def say_with_espeak_win(text, lang="de", speed=175, pitch=50):
    """Spricht Text mit eSpeak nicht blockierend aus. - Unter Windows"""
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

def say_with_native(text, speed=175, voice_index=0, lang="de", pitch=50):
    """benutzt die native Sprachsynthese des Betriebssystems.
    Unter Linux: Spricht den Text mit espeak aus.
    Unter Windows: Spricht den Text mit einer bestimmten Windows-Stimme aus."""
    global engine
    if engine is None:  # Nur einmal initialisieren
        engine = pyttsx3.init()
    voices = engine.getProperty('voices')



    if 0 <= voice_index < len(voices):  # Sicherstellen, dass der Index existiert
        engine.setProperty('voice', voices[voice_index].id)
    else:
        print("Ungültiger Index, Standardstimme wird verwendet.")

    engine.setProperty('rate', speed)
    engine.setProperty('volume', 1.0)
    engine.setProperty('pitch', pitch)
    engine.setProperty('language', lang)
    engine.say(text)
    engine.runAndWait()

    words = len(text.split())
    corrector = 1.2
    duration = words / speed * 60 * corrector
    return duration

#def get_audio_duration(file_path):
#    """Berechnet die Dauer einer MP3-Datei in Sekunden."""
#    try:
#        audio = MP3(file_path)
#        return audio.info.length  # Länge in Sekunden
#    except Exception as e:
#        print(f"Fehler beim Abrufen der Audiodauer: {e}")
#        return None

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

        # Speichere die Datei als 'output.mp3/wav'
        audio_file_path = "output.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(response.content)

        print(f"Audio gespeichert unter: {audio_file_path}")

        # Warte kurz, um sicherzustellen, dass die Datei vollständig gespeichert wurde
        #time.sleep(1)

        duration=play_audio_pygame(audio_file_path)

        print(f"Dauer:", duration, "Sekunden")



        return duration
    except Exception as e:
        print(f"Fehler bei der OpenAI-TTS-Anfrage: {e}")
        return None

if __name__ == "__main__":

    duration = say("Hallo, ich bin ein Roboter! 42.")
    pygame.time.wait(int(duration*1000))
    #print(f"Geschätzte Dauer: {duration:.2f} Sekunden")
    