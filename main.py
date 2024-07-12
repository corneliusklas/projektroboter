<<<<<<< HEAD

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


#initialize variables
last_question="Press " + str(hearing.recordkey) +" to ask a question!"
answer_text="The answer will be displayed here!"
emotion = "neutral"
talking = False






####functions####



gui.init()
vision.init_camera()

# Main program loop
running = True
i=0
while running:
    running = gui.handle_events()
    #select emotion by keyboard
    emotion = gui.select_emotion(emotion)
    #select talking by keyboard
    talking = gui.select_talking()

    #get text input 
    question = hearing.check_key_and_record()

    if question:
        last_question=question
        # Generate text from the model
        emotion, answer_text = language.generate_response(question)
        #say the answer
        speech.say(answer_text)

    #get the vision
    vision.update_faces()

    # Update the robot head display
    gui.update_display(emotion, talking,last_question,answer_text)



    print("game loop",i)
    i+=1	

# Clean up
gui.pygame.quit()
=======

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


#initialize variables
last_question="Press " + str(hearing.recordkey) +" to ask a question!"
answer_text="The answer will be displayed here!"
emotion = "neutral"
talking = False






####functions####



gui.init()
vision.init_camera()

# Main program loop
running = True
i=0
while running:
    running = gui.handle_events()
    #select emotion by keyboard
    emotion = gui.select_emotion(emotion)
    #select talking by keyboard
    talking = gui.select_talking()

    #get text input 
    question = hearing.check_key_and_record()

    if question:
        last_question=question
        # Generate text from the model
        emotion, answer_text = language.generate_response(question)
        #say the answer
        speech.say(answer_text)

    #get the vision
    vision.update_faces()

    # Update the robot head display
    gui.update_display(emotion, talking,last_question,answer_text)



    print("game loop",i)
    i+=1	

# Clean up
gui.pygame.quit()
>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
