
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
import gui
import vision
import time



#initialize variables
last_question= hearing.question
answer_text="The answer will be displayed here!"
emotion = "neutral"
talking = False
hearing.question = "System: Du wurdest gerade angeschaltet."






####functions####



#gui.init() is done in its own threat
vision.init_camera()

# Main program loop
running = True
i=0
while running:
    running = gui.handle_events()
    #select emotion by keyboard
    #gui.emotion = gui.select_emotion(emotion) ->  emotion via keyboard
    #select talking by keyboard
    gui.talking = gui.select_talking()

    #get text input 
    question = hearing.question

    if question != last_question:
        last_question=question
        gui.last_question=last_question
        # Generate text from the model
        emotion, answer_text = language.generate_response(question)
        gui.answer_text=answer_text
        gui.emotion=emotion
        #say the answer
        speech.say(answer_text)

    #get the vision
    vision.update_faces()

    # Update the robot head display
    #gui.update_display(emotion, talking,last_question,answer_text) -> in the tread gui



    #print("game loop",i)
    i+=1	
    #pause for other threats
    time.sleep(0.01)

# Clean up
#gui.pygame.quit() -> in run gui
