<<<<<<< HEAD

from openai import OpenAI
import os
client = OpenAI(api_key='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')
import keyboard
import numpy as np


import sounddevice as sd
import wavio
key = "ctrl" #key to start recording
audio_filename = "audio.wav" #filename to save audio

# Set the sample rate for recording
fs = 44100  # Sample rate

# Create a buffer to store the audio data
buffer = []#np.zeros((fs * 10,))  # 10 seconds buffer

# Define a callback function to process the audio chunks
def callback(indata, frames, time, status):
    buffer.append(indata.copy())

def record_audio_while_key_pressed(filename):
    print("Press and hold the 'r' key to start recording...")

    # Create an input stream with the callback function
    stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)

    # Start recording
    with stream:
        while True:
            if keyboard.is_pressed(key):  # if key  is pressed 
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
    
    
# Transcribe audio using Whisper ASR API
def transcribe_audio(filename):
    print("Transcribing audio...")
    audio_file= open(filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcript.text





#main loop
running = True
while running:
    #check for r key pressed
    if keyboard.is_pressed(key):
        #record_audio(audio_filename + str(i)+".wav",duration,fs)
        record_audio_while_key_pressed(audio_filename)
        #record_audio(audio_filename, duration, fs)
        running=False



sentence=transcribe_audio(audio_filename)




#command "C:\Programme\eSpeak\command_line>espeak -p 60 -v de "Hallo, Ich bin ein Roboter"")
#execute espeak system command
answer_text= sentence#'Hallo, Ich bin ein Roboter'#

speed = 110#175 #words per minute
command='cmd /c "C:\Programme\eSpeak\command_line\espeak -p 120 -v de-m2 -s ' + str(speed)+ ' "'+answer_text+'"'

print("command: ", command)
os.system(command )
#os.system(command='cmd /c "C:\Programme\eSpeak\command_line\espeak -p 120 -v de -s 110 "Wo soll ich den Einkaufskorb hinschicken? Haha"' )
#print "bla" every few seconds during duration
#import time
#for i in range(0, int(duration)*10):
#    print("bla")
#    time.sleep(.1) 


=======

from openai import OpenAI
import os
client = OpenAI(api_key='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')
import keyboard
import numpy as np


import sounddevice as sd
import wavio
key = "ctrl" #key to start recording
audio_filename = "audio.wav" #filename to save audio

# Set the sample rate for recording
fs = 44100  # Sample rate

# Create a buffer to store the audio data
buffer = []#np.zeros((fs * 10,))  # 10 seconds buffer

# Define a callback function to process the audio chunks
def callback(indata, frames, time, status):
    buffer.append(indata.copy())

def record_audio_while_key_pressed(filename):
    print("Press and hold the 'r' key to start recording...")

    # Create an input stream with the callback function
    stream = sd.InputStream(callback=callback, channels=1, samplerate=fs)

    # Start recording
    with stream:
        while True:
            if keyboard.is_pressed(key):  # if key  is pressed 
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
    
    
# Transcribe audio using Whisper ASR API
def transcribe_audio(filename):
    print("Transcribing audio...")
    audio_file= open(filename, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcript.text





#main loop
running = True
while running:
    #check for r key pressed
    if keyboard.is_pressed(key):
        #record_audio(audio_filename + str(i)+".wav",duration,fs)
        record_audio_while_key_pressed(audio_filename)
        #record_audio(audio_filename, duration, fs)
        running=False



sentence=transcribe_audio(audio_filename)




#command "C:\Programme\eSpeak\command_line>espeak -p 60 -v de "Hallo, Ich bin ein Roboter"")
#execute espeak system command
answer_text= sentence#'Hallo, Ich bin ein Roboter'#

speed = 110#175 #words per minute
command='cmd /c "C:\Programme\eSpeak\command_line\espeak -p 120 -v de-m2 -s ' + str(speed)+ ' "'+answer_text+'"'

print("command: ", command)
os.system(command )
#os.system(command='cmd /c "C:\Programme\eSpeak\command_line\espeak -p 120 -v de -s 110 "Wo soll ich den Einkaufskorb hinschicken? Haha"' )
#print "bla" every few seconds during duration
#import time
#for i in range(0, int(duration)*10):
#    print("bla")
#    time.sleep(.1) 


>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
