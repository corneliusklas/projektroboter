import keyboard
import sounddevice as sd
import wavio
import numpy as np
import threading
import queue
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

global RECORDING
RECORDING = False
lan="de"

# Get the API key
import loadapikey
loadapikey.api_key

api_key = os.getenv('API_KEY')
# Initialize the OpenAI client with the loaded API key
client = OpenAI(api_key=api_key)


recordkey = "enter"
audio_filename = "audio.wav"
fs = 44100  # Sample rate for audio recording
channels = 1  # Number of audio channels	
blocksize=1024
#prerecord lenth in ms
prerecord=500
#prerecord block lenth
prerecord_block=int((fs / 1000 * prerecord) / blocksize)
print("prerecord block",prerecord_block)

audio_buffer = queue.Queue() #maxsize= int(fs * buffer_duration))  # Buffer to hold n seconds of audio buffer_duration = .5  # Duration of the buffer in seconds

global question
last_question = "Press " + recordkey + " to ask a question!"
question = last_question

def audio_callback(indata, frames, time, status):
    """Callback function for the audio stream."""
    if not audio_buffer.full():
        audio_buffer.put(indata.copy())

def continuous_recording():
    global RECORDING
    """Continuously record audio into the buffer."""
    with sd.InputStream(callback=audio_callback, channels=channels, samplerate=fs, blocksize=blocksize):

        while True:
            if keyboard.is_pressed(recordkey):
                RECORDING = True
                print('Recording...')
                sd.sleep(1000)  # Record for 1 second after key press
            else:
                if RECORDING:
                    print('Stopped recording.')
                    RECORDING = False
                    save_audio(audio_filename)
                    global question
                    question = transcribe_audio(audio_filename)
                else:
                    # Remove the oldest data from the buffer
                    while not audio_buffer.qsize() < prerecord_block:
                        audio_buffer.get()  # Remove the oldest data from the buffer
                    sd.sleep(int(500)) #record also a bit of sound before the key is pressed. Otherwise the first word is cut off, because it takes a bit of time to start the recording


print("Press and hold the " + recordkey +" key to start recording...")

def save_audio(audio_filename):
    # Extract audio from the buffer
    buffer_content = []
    while not audio_buffer.empty():
        buffer_content.append(audio_buffer.get())
    recording = np.concatenate(buffer_content, axis=0)

    # Save the recorded audio
    wavio.write(audio_filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", audio_filename)



def analyze_audio(file_path):
    from pydub import AudioSegment
    from pydub.silence import detect_nonsilent
    # Lade die Audiodatei
    audio = AudioSegment.from_wav(file_path)

    # Erkenne die Zeitstempel der nicht stillen Abschnitte (Stille ist < -40 dBFS)
    non_silent_ranges = detect_nonsilent(audio, min_silence_len=1000, silence_thresh=-40)

    # Überprüfung der Ergebnisse
    #if len(non_silent_ranges) == 0:
    #    print("Die Audiodatei enthält nur Stille.")
    #else:
    #    print(f"Die Audiodatei enthält {len(non_silent_ranges)} nicht stille Abschnitte.")
    return len(non_silent_ranges)



# Transcribe audio using Whisper ASR API
def transcribe_audio(filename):
    global lan
    print("Transcribing audio...")

    # Beispielaufruf der Funktion
    non_silent=analyze_audio(filename)

    if non_silent == 0:
        return "~" #"No audio detected"
    
    # Öffnen der Audiodatei
    audio_file= open(filename, "rb")
    #check for errors 
    #try:
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
       
        language=lan
    )
    return transcript.text # " non_silent: " + str(non_silent)
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



# Start continuous recording in a separate thread
recording_thread = threading.Thread(target=continuous_recording, daemon=True)
recording_thread.start()


if __name__ == "__main__":
    print_default_input_device_info()
    running = True
    while running:
        if last_question != question:
            last_question = question
            print(last_question)
        if keyboard.is_pressed('esc'):
            running = False
        #pause the loop for a short time
        time.sleep(0.01)







        