<<<<<<< HEAD
import keyboard
import sounddevice as sd
import wavio
from openai import OpenAI
import numpy as np
import sys
from dotenv import load_dotenv
import os
#load the api key from the .env file
load_dotenv()

#recordkey = "ctrl" #key to start recording
recordkey="enter"
audio_filename = "audio.wav" #filename to save audio
fs = 44100  # Sample rate for autio recording

# Get the API key
api_key = os.getenv('API_KEY')
# Initialize the OpenAI client with the loaded API key
client = OpenAI(api_key=api_key)
#client = OpenAI(api_key='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')

buffer = []  #Create a buffer to store the audio data



# Define a callback function to process the audio chunks
def callback(indata, frames, time, status):
    buffer.append(indata.copy())


def record_audio_while_key_pressed(filename):
    print("Press and hold the 'Space' key to start recording...")
    #initialize the stream
    stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)

    # Create an input stream with the callback function
    #stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)
    
    # Start recording
    with stream:
        while True:
  
            if keyboard.is_pressed(recordkey):  # if key  is pressed  
                print('Recording...')
                sd.sleep(1000)  # Record for 1 second
            else:
                print('Stopped recording.')
                break

    # Concatenate all recorded frames
    recording = np.concatenate(buffer, axis=0)

    # Save the recorded audio
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", filename)
    #delete the buffer
    buffer.clear()
    
    
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
        #update buffer
        pass#update_prerecord()
    
"""#---------------------------Start automatische Aufnahme------------------------------
import queue
audio_queue = queue.Queue()
import soundfile as sf

def read_microphone_data(duration=0.1):
    #Liest eine kurze Audiosequenz vom Mikrofon.
    return sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)

def calculate_volume(data):
    #Berechnet die Lautstärke der gelesenen Audiosequenz.
    rms = np.sqrt(np.mean(data**2))
    return 20 * np.log10(rms)

def callback(indata, frames, time, status):
    stop_threshold = 0.0001  # Stoppschwellenwert für die Aufnahme
    #Diese Funktion wird von sounddevice für jede neue Audio-Datenportion aufgerufen.
    global recording
    if status:
        print(status)
    if recording:
        volume = rms(indata[:, 0])  # Berechnet RMS des ersten Kanals
        print("Volume:", volume, "Threshold:", stop_threshold)
        if volume < stop_threshold:
            print("Stopping recording due to low volume.")
            recording = False  # Setzt is_recording auf False, um die Aufnahme zu stoppen


def start_recording():
    #Startet die Audioaufnahme.
    global recording
    recording = True
    with sf.SoundFile(audio_filename, mode='w', samplerate=fs, channels=1) as file:
        with sd.InputStream(callback=callback):
            while recording:
                file.write(audio_queue.get())
    

def stop_recording():
    #Stoppt die Audioaufnahme.
    global recording
    recording = False

def rms(frame):
    #Berechnet den RMS-Wert der Audio-Daten.
    count = len(frame)
    sum_squares = np.sum(np.square(frame))
    rms_val = np.sqrt(sum_squares / count)
    return rms_val

# Beispiel, wie die Funktionen verwendet werden könnten
def monitor_and_record():
    start_threshold = -30  # Startschwellenwert für die Aufnahme
    while True:
        data = read_microphone_data()  # Mikrofoneingang lesen
        volume = calculate_volume(data)  # Lautstärke des Eingangs berechnen
        
        #print the volume
        print("Volume:", volume, "Threshold:", start_threshold)
        if volume > start_threshold:  # Überprüfen, ob die Lautstärke den Startschwellenwert überschreitet
            print("Start recording")
            start_recording()
            

#---------------------------Ende automatische Aufnahme------------------------------"""
    
#start main loop if main

is_recording = True
i=0
if __name__ == "__main__":
    #print("Audio Devides:", sd.query_devices())
    print_default_input_device_info()

    running = True
    while running:
    #get text input 
        question = check_key_and_record()
        #question = monitor_and_record()

        if question:
            last_question=question
            # Generate text from the model
            #say the answer
            print(last_question)

        #print("game loop",i)
=======
import keyboard
import sounddevice as sd
import wavio
from openai import OpenAI
import numpy as np
import sys
from dotenv import load_dotenv
import os
#load the api key from the .env file
load_dotenv()

#recordkey = "ctrl" #key to start recording
recordkey="enter"
audio_filename = "audio.wav" #filename to save audio
fs = 44100  # Sample rate for autio recording

# Get the API key
api_key = os.getenv('API_KEY')
# Initialize the OpenAI client with the loaded API key
client = OpenAI(api_key=api_key)
#client = OpenAI(api_key='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')

buffer = []  #Create a buffer to store the audio data



# Define a callback function to process the audio chunks
def callback(indata, frames, time, status):
    buffer.append(indata.copy())


def record_audio_while_key_pressed(filename):
    print("Press and hold the 'Space' key to start recording...")
    #initialize the stream
    stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)

    # Create an input stream with the callback function
    #stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)
    
    # Start recording
    with stream:
        while True:
  
            if keyboard.is_pressed(recordkey):  # if key  is pressed  
                print('Recording...')
                sd.sleep(1000)  # Record for 1 second
            else:
                print('Stopped recording.')
                break

    # Concatenate all recorded frames
    recording = np.concatenate(buffer, axis=0)

    # Save the recorded audio
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", filename)
    #delete the buffer
    buffer.clear()
    
    
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
        #update buffer
        pass#update_prerecord()
    
"""#---------------------------Start automatische Aufnahme------------------------------
import queue
audio_queue = queue.Queue()
import soundfile as sf

def read_microphone_data(duration=0.1):
    #Liest eine kurze Audiosequenz vom Mikrofon.
    return sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)

def calculate_volume(data):
    #Berechnet die Lautstärke der gelesenen Audiosequenz.
    rms = np.sqrt(np.mean(data**2))
    return 20 * np.log10(rms)

def callback(indata, frames, time, status):
    stop_threshold = 0.0001  # Stoppschwellenwert für die Aufnahme
    #Diese Funktion wird von sounddevice für jede neue Audio-Datenportion aufgerufen.
    global recording
    if status:
        print(status)
    if recording:
        volume = rms(indata[:, 0])  # Berechnet RMS des ersten Kanals
        print("Volume:", volume, "Threshold:", stop_threshold)
        if volume < stop_threshold:
            print("Stopping recording due to low volume.")
            recording = False  # Setzt is_recording auf False, um die Aufnahme zu stoppen


def start_recording():
    #Startet die Audioaufnahme.
    global recording
    recording = True
    with sf.SoundFile(audio_filename, mode='w', samplerate=fs, channels=1) as file:
        with sd.InputStream(callback=callback):
            while recording:
                file.write(audio_queue.get())
    

def stop_recording():
    #Stoppt die Audioaufnahme.
    global recording
    recording = False

def rms(frame):
    #Berechnet den RMS-Wert der Audio-Daten.
    count = len(frame)
    sum_squares = np.sum(np.square(frame))
    rms_val = np.sqrt(sum_squares / count)
    return rms_val

# Beispiel, wie die Funktionen verwendet werden könnten
def monitor_and_record():
    start_threshold = -30  # Startschwellenwert für die Aufnahme
    while True:
        data = read_microphone_data()  # Mikrofoneingang lesen
        volume = calculate_volume(data)  # Lautstärke des Eingangs berechnen
        
        #print the volume
        print("Volume:", volume, "Threshold:", start_threshold)
        if volume > start_threshold:  # Überprüfen, ob die Lautstärke den Startschwellenwert überschreitet
            print("Start recording")
            start_recording()
            

#---------------------------Ende automatische Aufnahme------------------------------"""
    
#start main loop if main

is_recording = True
i=0
if __name__ == "__main__":
    #print("Audio Devides:", sd.query_devices())
    print_default_input_device_info()

    running = True
    while running:
    #get text input 
        question = check_key_and_record()
        #question = monitor_and_record()

        if question:
            last_question=question
            # Generate text from the model
            #say the answer
            print(last_question)

        #print("game loop",i)
>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
        #i+=1	