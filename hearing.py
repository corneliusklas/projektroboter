from pynput import keyboard
import sounddevice as sd
import wavio
import numpy as np
import threading
import queue
from openai import OpenAI
import time

global RECORDING
RECORDING = False
lan = "de"

# Get the API key
import loadapikey
api_key = loadapikey.api_key

# Initialize the OpenAI client with the loaded API key
client = OpenAI(api_key=api_key)

recordkey = keyboard.Key.enter  # Tastenkürzel für Aufnahme
audio_filename = "audio.wav"
fs = 44100  # Sample rate für die Audioaufnahme
channels = 1  # Anzahl der Audiokanäle
blocksize = 1024
prerecord = 500  # Pre-Record-Länge in ms
prerecord_block = int((fs / 1000 * prerecord) / blocksize)

print("Prerecord block", prerecord_block)

audio_buffer = queue.Queue()  # Buffer für Audioclips
global question
last_question = f"Press {recordkey} to ask a question!"
question = last_question

def audio_callback(indata, frames, time, status):
    """Callback-Funktion für den Audiostream."""
    if not audio_buffer.full():
        audio_buffer.put(indata.copy())

def continuous_recording():
    global RECORDING
    """Kontinuierliche Aufnahme in den Buffer."""
    with sd.InputStream(callback=audio_callback, channels=channels, samplerate=fs, blocksize=blocksize):
        while True:
            if RECORDING:
                print('Recording...')
                sd.sleep(1000)  # Aufnahme läuft für 1 Sekunde nach Tastendruck
            else:
                while not audio_buffer.qsize() < prerecord_block:
                    audio_buffer.get()
                sd.sleep(500)  # Kurze Verzögerung für Prerecording

# Dynamische Ausgabe mit dem richtigen Tastenwert
print(f"Press and hold the {recordkey.name.upper()} key to start recording...")

def save_audio(audio_filename):
    """Speichert den aufgenommenen Audio-Buffer in eine Datei."""
    buffer_content = []
    while not audio_buffer.empty():
        buffer_content.append(audio_buffer.get())
    recording = np.concatenate(buffer_content, axis=0)
    wavio.write(audio_filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", audio_filename)

def analyze_audio(file_path):
    """Überprüft, ob die Audiodatei Sprachinhalt enthält."""
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
    audio = AudioSegment.from_wav(file_path)
    non_silent_ranges = detect_nonsilent(audio, min_silence_len=1000, silence_thresh=-40)
    return len(non_silent_ranges)

def transcribe_audio(filename):
    """Transkribiert das aufgenommene Audio mit OpenAI Whisper."""
    global lan
    print("Transcribing audio...")

    non_silent = analyze_audio(filename)
    if non_silent == 0:
        return "~"

    audio_file = open(filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language=lan
    )
    return transcript.text

def get_mic_index_by_name(mic_name):
    """Sucht nach einem Mikrofon mit dem angegebenen Namen und gibt den Index zurück."""
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        if mic_name in device['name']:
            return index
    return None

def print_default_input_device_info():
    """Gibt das Standard-Eingabegerät aus."""
    default_device_info = sd.query_devices(kind='input')
    print("Standard-Eingabegerät:", default_device_info['name'])

def on_key_press(key):
    """Wird aufgerufen, wenn eine Taste gedrückt wird."""
    global RECORDING
    if key == recordkey:
        RECORDING = True

def on_key_release(key):
    """Wird aufgerufen, wenn eine Taste losgelassen wird."""
    global RECORDING
    global question
    if key == recordkey:
        if RECORDING:
            print('Stopped recording.')
            RECORDING = False
            save_audio(audio_filename)
            question = transcribe_audio(audio_filename)

    if key == keyboard.Key.esc:
        print("Programm wird beendet...")
        return False

# Starte den Keyboard-Listener
listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
listener.start()

# Starte die kontinuierliche Aufnahme in einem separaten Thread
recording_thread = threading.Thread(target=continuous_recording, daemon=True)
recording_thread.start()

if __name__ == "__main__":
    print_default_input_device_info()
    running = True
    while running:
        if last_question != question:
            last_question = question
            print(last_question)
        time.sleep(0.01)  # Kurze Pause, um CPU-Last zu reduzieren
