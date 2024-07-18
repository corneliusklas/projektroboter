import keyboard
import sounddevice as sd
import wavio
import numpy as np
import threading
import queue
from openai import OpenAI
from dotenv import load_dotenv
import os

# Get the API key
api_key = os.getenv('API_KEY')
# Initialize the OpenAI client with the loaded API key
client = OpenAI(api_key=api_key)
print("API key",api_key)

recordkey = "enter"
audio_filename = "audio.wav"
fs = 44100  # Sample rate for audio recording
buffer_duration = 1  # Duration of the buffer in seconds
audio_buffer = queue.Queue(maxsize=fs * buffer_duration * 2)  # Buffer to hold 1 second of audio

def audio_callback(indata, frames, time, status):
    """Callback function for the audio stream."""
    if not audio_buffer.full():
        audio_buffer.put(indata.copy())

def continuous_recording():
    """Continuously record audio into the buffer."""
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=fs):
        while True:
            sd.sleep(1000)

# Start continuous recording in a separate thread
recording_thread = threading.Thread(target=continuous_recording, daemon=True)
recording_thread.start()

def record_audio_while_key_pressed(filename):
    print("Press and hold the 'Enter' key to start recording...")
    while True:
        if keyboard.is_pressed('enter'):
            print('Recording...')
            sd.sleep(1000)  # Record for 1 second after key press
            break

    # Extract audio from the buffer
    buffer_content = []
    while not audio_buffer.empty():
        buffer_content.append(audio_buffer.get())
    recording = np.concatenate(buffer_content, axis=0)

    # Save the recorded audio
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", filename)

    
# Transcribe audio using Whisper ASR API
def transcribe_audio(filename,lan="de"):
    print("Transcribing audio...")
    audio_file= open(filename, "rb")
    #check for errors 
    #try:
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        language=lan
    )
    return transcript.text
    #except:
    #    #get a text for the spececific error
    #    error = str(sys.exc_info()[1])
    #    #print the error
    #    print("error: ",error)
    #    #output the error as speeech
    #    return error
    

def get_mic_index_by_name(mic_name):
    """
    Sucht nach einem Mikrofon mit dem gegebenen Namen und gibt dessen Index zurück.
    Gibt None zurück, wenn kein Gerät mit diesem Namen gefunden wurde.
    """
    devices = sd.query_devices()
    for index, device in enumerate(devices):
        if mic_name in device['name']:
            return index
    return None

def print_default_input_device_info():
    # Ermitteln der Eigenschaften des Standard-Eingabegeräts
    default_device_info = sd.query_devices(kind='input')
    # Ausgabe des Namens des Standard-Eingabegeräts
    print("Standard-Eingabegerät:", default_device_info['name'])

def check_key_and_record():
    if keyboard.is_pressed(recordkey):
        record_audio_while_key_pressed(audio_filename)
        question = transcribe_audio(audio_filename)
        return question
    else:
        pass  # This could be a place to handle continuous buffer update if needed

if __name__ == "__main__":
    print_default_input_device_info()
    running = True
    while running:
        question = check_key_and_record()
        if question:
            last_question = question
            print(last_question)