import subprocess
import os
import pyttsx3
import pygame
import platform
import json
import scipy.io.wavfile as wav
import numpy as np	
from pydub import AudioSegment

engine = None  # Globale Variable für das pyttsx3-Objekt


#  engine_type="espeak" # "espeak", "native" oder "openai"
# Sprachsynth-Engine from config.json
with open('config.json') as f:
    data = json.load(f)
    engine_type = data['speech_engine']

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
    global engine_type
    if engine_type == "espeak":
        return say_with_espeak(text, lang, speed, pitch)
    elif engine_type == "native":
        return say_with_native(text, speed,voice_index=0, lang=lang, pitch=pitch)
    elif engine_type == "openai":
        return say_with_openai(text)
    else:
        print("Ungültige Engine. Wähle 'espeak', 'windows' oder 'openai'.")
        return None

def say_with_espeak(text, lang="de", speed=175, pitch=50):
    """
    Einheitliche eSpeak-Sprachausgabe für Windows & Linux.

    Args:
        text (str): Der zu sprechende Text.
        lang (str): Sprache (z.B. 'de' für Deutsch, 'en' für Englisch).
        speed (int): Sprechgeschwindigkeit (Standard: 175).
        pitch (int): Tonhöhe (0-99, Standard: 50).

    Returns:
        float: Geschätzte Dauer der Sprachausgabe in Sekunden.
    """
    if platform.system() == "Windows":
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
    else:  # Linux / Raspberry Pi
        command = [
            "espeak",
            f"-v{lang}",
            f"-s{speed}",
            f"-p{pitch}",
            text
        ]

    try:
        subprocess.Popen(command)
        print(f"Text wird gesprochen mit eSpeak ({platform.system()})...")
    except Exception as e:
        print(f"Fehler beim Ausführen von eSpeak: {e}")

    # Berechnung der Sprachausgabe-Dauer
    words = len(text.split())
    corrector = 1.2  # Anpassungsfaktor für realistische Berechnung
    duration = words / speed * 60 * corrector
    return duration

def say_with_native(text, speed=175, voice_index=0):
    """benutzt die native Sprachsynthese des Betriebssystems.
    Unter Linux: Spricht den Text mit espeak aus.
    Unter Windows: Spricht den Text mit einer bestimmten Windows-Stimme aus."""
    global engine
    if engine is None:  # Nur einmal initialisieren
        engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("Verfügbare Stimmen:")
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.id}")

    if 0 <= voice_index < len(voices):  # Sicherstellen, dass der Index existiert
        engine.setProperty('voice', voices[voice_index].id)
    else:
        print("Ungültiger Index, Standardstimme wird verwendet.")

    engine.setProperty('rate', speed)
    engine.setProperty('volume', 1.0)

    engine.say(text)
    engine.runAndWait()

    words = len(text.split())
    corrector = 1.2
    duration = words / speed * 60 * corrector
    return duration


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


import numpy as np
import scipy.io.wavfile as wav

def apply_ring_modulation(input_file, output_file, frequency=80, depth=.5): #400, 0,5
    """
    Wendet einen Ringmodulationseffekt auf eine WAV-Datei an.
    Anwendung von Ringmodulation nach Vorschlag von: https://spectrum.ieee.org/audio-deepfake-fix?utm_source=tldrai
    
    Args:
        input_file (str): Pfad zur Eingangsdatei (WAV).
        output_file (str): Pfad zur Ausgabe (WAV).
        frequency (float): Frequenz des Modulators in Hz (z. B. 400 Hz für Robotereffekt).
        depth (float): Intensität des Effekts (0 = kein Effekt, 1 = 100% Modulation).
    """
    
    # Lade die Audiodatei
    rate, data = wav.read(input_file)
    
    # Falls Stereo, nur einen Kanal nutzen
    if len(data.shape) > 1:
        data = data[:, 0]  
    
    # Erstelle eine Sinuswelle als Modulator
    t = np.arange(len(data)) / rate
    modulator = np.sin(2 * np.pi * frequency * t)
    
    # Skaliere die Modulation mit `depth`
    modulated_data = (1 - depth) * data + depth * (data * modulator)
    
    # Normiere zurück in 16-Bit Integer-Werte
    modulated_data = np.int16(modulated_data / np.max(np.abs(modulated_data)) * 32767)
    
    # Speichere die neue Datei
    wav.write(output_file, rate, modulated_data)
    print(f"Moduliertes Audio gespeichert unter: {output_file}")




def say_with_openai(text, voice="fable", model="tts-1"): #alloy, ash, coral, echo ...
    """
    Nutzt OpenAI TTS, um den Text in Sprache umzuwandeln und die Dauer zurÃ¼ckzugeben.
    
    Args:
        text (str): Der zu sprechende Text.
        voice (str): Die gewuenschte Stimme ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer').
        model (str): Das TTS-Modell ('tts-1' oder 'tts-1-hd').

    Returns:
        float: Die tatsaechliche Laenge der generierten Audiodatei in Sekunden oder None, falls ein Fehler auftritt.
    """
    try:
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        # Speichere die Datei als 'output.mp3/wav'
        mp3_file_path = "output.mp3"
        with open( "output.mp3"     , "wb") as f:
            f.write(response.content)

        # Konvertiere MP3 zu WAV
        wav_file_path = "output.wav"
        audio = AudioSegment.from_file(mp3_file_path, format="mp3")
        audio.export(wav_file_path, format="wav")


        print(f"Audio gespeichert unter: {wav_file_path}")

        # Wende den Ringmodulationseffekt an
        modulated_file = "output_modulated.wav"
        apply_ring_modulation(wav_file_path, modulated_file)
        print(f"Moduliertes Audio gespeichert unter: {modulated_file}")
        
        # Spiele das modulierte Audio ab
        duration = play_audio_pygame(modulated_file)
        print(f"Dauer: {duration} Sekunden")

        return duration
    except Exception as e:
        print(f"Fehler bei der OpenAI-TTS-Anfrage: {e}")
        return None

if __name__ == "__main__":

    duration = say("Hallo, ich bin ein Roboter! 42.")
    
    #print(f"Geschätzte Dauer: {duration:.2f} Sekunden")
    #test apply_ring_modulation
    #apply_ring_modulation("output.wav", "output_modulated.wav", frequency=80, depth=1)
    #test play_audio_pygame
    #duration = play_audio_pygame("output_modulated.wav")
    pygame.time.wait(int(duration*1000))
    