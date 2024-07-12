<<<<<<< HEAD
import os
#convert the answertext to speech with espeak external program
#https://espeak.sourceforge.net/commands.html, file: -w speech.wav
speed = 175 #words per minute
talking=False

def say(text):
    print("Talking.")
    talking=True
    command = 'cmd /c "eSpeak\command_line\espeak -p 30 -v de-m2 -s ' + str(speed)+' "'+text+'""'
    print("command: ", command)
    os.system(command )

    #os.system('cmd /c "C:\Programme\eSpeak\command_line\espeak -p 30 -v de-m2 -s ' + str(speed)+' "'+answer_text+'"' ) 
    print("Talking stopped.")
    talking=False
#
    
#speak example if this is main
if __name__ == "__main__":
=======
import os
#convert the answertext to speech with espeak external program
#https://espeak.sourceforge.net/commands.html, file: -w speech.wav
speed = 175 #words per minute
talking=False

def say(text):
    print("Talking.")
    talking=True
    command = 'cmd /c "eSpeak\command_line\espeak -p 30 -v de-m2 -s ' + str(speed)+' "'+text+'""'
    print("command: ", command)
    os.system(command )

    #os.system('cmd /c "C:\Programme\eSpeak\command_line\espeak -p 30 -v de-m2 -s ' + str(speed)+' "'+answer_text+'"' ) 
    print("Talking stopped.")
    talking=False
#
    
#speak example if this is main
if __name__ == "__main__":
>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
        say("Hallo, Ich bin ein Roboter")