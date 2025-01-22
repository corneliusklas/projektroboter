import pygame
import threading
import time
#constants
sizex = 1024#1920 #
sizey = 600#1080 #

###load data###
#load face images
faceImages=[[],[],[],[]]

screen = None
emotion_to_face = None

#eye position relative to the eye size
left_eye_x = 0.290
left_eye_y = 0.29
right_eye_x = 0.710
right_eye_y = 0.29
#pupille
eye_radius_x=0.05 #relative to the screen size
eye_radius_y=0.07 #relative to the screen size
eye_x=0.0
eye_y=-0

global emotion, talking,last_question,answer_text
emotion = "neutral"
talking = False
last_question= "test"
answer_text= "test"

#init function
def init():
    global screen, emotion_to_face, faceImages, sizex, sizey
    # Initialize the robot head display
    pygame.init()
    pygame.mixer.init()
    if False:	
        try:screen = pygame.display.set_mode((sizex, sizey),pygame.NOFRAME,display=1)#RESIZABLE) #pygame.FULLSCREEN
        except:
            print("Display 1 not available")
            screen = pygame.display.set_mode((sizex, sizey))
    else:
        screen = pygame.display.set_mode((sizex, sizey))
        
    #os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (0,0)
    pygame.display.set_caption("Robot Head")
    #angry=[]
    faceImages[0].append(pygame.image.load("face/angry0.png"))
    faceImages[0].append(pygame.image.load("face/angry.png"))
    #happy=[]
    faceImages[1].append(pygame.image.load("face/happy0.png"))
    faceImages[1].append(pygame.image.load("face/happy.png"))
    #sad=[]
    faceImages[2].append(pygame.image.load("face/sad0.png"))
    faceImages[2].append(pygame.image.load("face/sad.png"))
    #neutral=[]
    faceImages[3].append(pygame.image.load("face/neutral0.png"))
    faceImages[3].append(pygame.image.load("face/neutral.png"))

    # Define a dictionary to map emotions to faces
    emotion_to_face = {
    "angry": faceImages[0],
    "happy": faceImages[1],
    "sad": faceImages[2],
    "neutral": faceImages[3]
    }

    



def select_emotion(emotion):
    pressed = pygame.key.get_pressed()
    #print(pressed)
    if pressed[pygame.K_1]:
        return "angry"
    elif pressed[pygame.K_2]:
        return "happy"
    elif pressed[pygame.K_3]:
        return "sad"
    elif pressed[pygame.K_4]:
        return "neutral"
    else:
        return emotion
    
def select_talking():    
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_a]: #talking
        return 1	
    else:
        return 0
    
def handle_events():
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_ESCAPE]:
        return False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def update_display():#emotion, talking,last_question,answer_text):
    global screen, emotion_to_face, faceImages, sizex, sizey, eye_radius, eye_x, eye_y 
    global emotion, talking,last_question,answer_text

    # Get the face for the selected emotion
    face = emotion_to_face.get(emotion, faceImages[3])  # Default to neutral face if emotion is not recognized

    # Select the face based on whether the robot is talking
    faceD = face[1] if talking else face[0]

    faceD = pygame.transform.scale(faceD, (sizex, sizey))

    # Update the robot head display
   
    screen.fill((255, 255, 255))

    # Draw the face
    screen.blit(faceD, (0, 0))
    #set the size of the face
   
    # Draw the left eyeball

    pygame.draw.circle(screen, (0, 0, 0), ((left_eye_x+eye_radius_x*eye_x)*sizex, (left_eye_y+eye_radius_y*eye_y)*sizey), 0.01*sizex) 
    # Draw the right eyeball
    pygame.draw.circle(screen, (0, 0, 0), ((right_eye_x+eye_radius_x*eye_x)*sizex, (right_eye_y+eye_radius_y*eye_y)*sizey), 0.01*sizex)

    #print the answer text on the screen
    font = pygame.font.SysFont('Arial', int(0.012*sizex))
    text1 = font.render(last_question, True, (0, 0, 0))
    text2 = font.render(answer_text, True, (0, 0, 0))
    screen.blit(text1, (0.05*sizex, 0.92*sizey))
    screen.blit(text2, (0.05*sizex, 0.94*sizey))
    
    # Update the display
    pygame.display.flip()


def run_gui():
    running = True
    while running:
        running = handle_events()
        update_display()
        #time.sleep(0.01)
    pygame.quit()


init()
# Create a thread to run the GUI
gui_thread = threading.Thread(target=run_gui,daemon=True)

# Start the GUI thread
gui_thread.start()

#start main loop if main
if __name__ == "__main__":
    #init()
    #main loop
    running = True

    while running:
        running = handle_events()
        #select emotion by keyboard
        emotion = select_emotion(emotion)
        #select talking by keyboard
        talking = select_talking()
        #update the display
        #update_display()#emotion, talking,"test","test")
        #pause for other threats
        time.sleep(0.01)
    # Clean up
    #pygame.quit() in run gui
    