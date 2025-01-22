
#This should be a program that controls a simple humanoid robot.
#First be build a robot head with a face displayed on a screen.
#The user can talk to the robot in natural language and get answers. 

#load the libraries
#import pygame
#from openai import OpenAI
#import keyboard

#import own modules
import language
import speech
import hearing
import gui_face
import threading
import time


VISION = False

if VISION:
    import vision

#initialize variables
last_question= hearing.question
answer_text="The answer will be displayed here!"
emotion = "neutral"
hearing.question = "System: Du wurdest gerade angeschaltet."






####functions####



#gui.init() is done in its own threat
if VISION:
    vision.init_camera()

try:
    # Main program loop
    running = True
    i=0


    gui_thread = threading.Thread(target=gui_face.run_gui, daemon=True)
    gui_thread.start()

    while running:
        running = gui_face.handle_events()


        #get text input 
        question = hearing.question

        if question != last_question:
            last_question=question
            gui_face.last_question=last_question
            # Generate text from the model
            emotion, answer_text = language.generate_response(question)
            gui_face.answer_text=answer_text
            gui_face.emotion=emotion
            #say the answer
            talktime=speech.say(answer_text)
            #set talking time
            gui_face.start_talking(talktime)

        #get the vision
        if VISION:
            vision.update_faces()

        #print("game loop",i)
        i+=1	
        #pause for other threats
        time.sleep(0.01)

finally: #clean up
    print("Beende das Programm...")
    gui_face.running = False  # Beende die GUI-Schleife sicher
    gui_thread.join()  # Warte, bis der GUI-Thread beendet ist
    print("Programm beendet.")

