<<<<<<< HEAD
#! pip install deepface
from deepface import DeepFace
import cv2
import os
import sys
from numpy import dot
from numpy.linalg import norm


#database path
database_path = 'dataset/'
#get all image names from the database
databaseNames = os.listdir(database_path)
#only use jpg files
databaseNames = [name for name in databaseNames if name.endswith(".jpg")]
#remove the file extension by removing the last 4 characters
databaseNames = [name[:-4] for name in databaseNames]

#calculate the face vetors for the database
#database_face_vectors = [DeepFace.represent("dataset/"+name+".jpg") for name in databaseNames]
#print("face_vectors: ",face_vectors)



cap = None

xs, ys, ws, hs, faces,confidences,extractedfaces = [], [], [], [], [], [], []
img = None
framewidth = 0
frameheight = 0

#get face position
def get_face_position():
    global xs, ys, ws, hs, faces,confidences,img,extractedfaces
    #make the image suilable for deepface
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #get face position
    faces = DeepFace.extract_faces(img, enforce_detection=False)
    #print(faces[0])
    xs, ys, ws, hs, extractedfaces, confidences = [], [], [], [],[],[]
    #nurmber_of_faces = len(faces)
    #print(f"Found {nurmber_of_faces} faces")
    for face in faces:
        extractedface=face["face"] #= extracted image?
        x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
        #print(f"Face found at X: {x}, Y: {y}, Width: {w}, Height: {h}")
        confidence = face["confidence"]
        xs.append(x)
        ys.append(y)
        ws.append(w)
        hs.append(h)
        extractedfaces.append(extractedface)
        confidences.append(confidence)

    #sort by face width
    xs, ys, ws, hs, faces,confidences = zip(*sorted(zip(xs, ys, ws, hs, faces,confidences), key=lambda x: x[2]))
        
    return xs, ys, ws, hs, extractedfaces, confidences

#init camera
def init_camera():
    global cap
    global framewidth, frameheight
    #init camera
    cap = cv2.VideoCapture(0)
    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")
        return None
    #get the resolution
    framewidth  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
    frameheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float

    #return cap



#get the image from the camera
def get_image_from_camera():
    global cap

    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        return None

    return frame

#update faces
def update_faces():
    global xs, ys, ws, hs, faces,confidences,img
    #get the image from the camera
    img = get_image_from_camera()
    #get face position
    xs, ys, ws, hs, faces,confidences = get_face_position()

#verify the person name from the image
def identify_person(face,name):
 
    result = DeepFace.verify("dataset/"+name+".jpg", face, enforce_detection=False)
    verified=result["verified"]


    if verified:
        return name
    else:
        return ""

#check wich person is in the image compared to the database
def identify_persons(face,names):
    #global  faces
    namenumber=len(names)
    #create and allnames Array wiht the length len(faces)
    allnames=""#[""]*len(faces)
    for i in range(namenumber):
        name=names[i]
        #compare the faces
        oneperson = identify_person(face,name)
        #combine the strings in both lists
        #for j in range(len(onepersonlist)):
        #    allnames[j]=allnames[j]+"/"+onepersonlist[j]
        if allnames=="":
            allnames=oneperson
        else:
            allnames=allnames+" or "+oneperson
    return allnames
    

#show a demo if main
if __name__ == "__main__":
    import pygame
    pygame.init()
    pygame.mixer.init()
    #start the pygame window
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Video")
    #init camera
    init_camera()
    #start the main loop
    running = True
    frame=0
    names=[""]
    while running:
        frame+=1
        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        #update face position, vector ans so on
        update_faces()
        
        #plot the image
        screen.blit(pygame.image.frombuffer(img.tostring(), img.shape[1::-1], "BGR"), (0, 0))

        #compare the faces
        #names=verify_person("Cornelius.Klas.JPG")


 
        #plot the face position with pygame
        face_number=len(faces)
        #only the first face
        #face_number=1
        for i in range(face_number):
            x, y, w, h,face, confidence, extractedface = xs[i], ys[i], ws[i], hs[i],faces[i], confidences[i], extractedfaces[i]
            if confidence > 0.5:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, w, h), 2)
                
                #check every n frames
                n=1
                if False: #frame%n==0:
                    names=identify_persons(extractedface,["Cornelius.Klas","Casimir.Hee"])#databaseNames)
                    font = pygame.font.SysFont('Arial', 15)
                    text = font.render(names, True, (255, 0, 0))
                    screen.blit(text, (x, y))
    
        #update the display
        pygame.display.update()
    

        
    # When everything done, release the video capture object
=======
#! pip install deepface
from deepface import DeepFace
import cv2
import os
import sys
from numpy import dot
from numpy.linalg import norm


#database path
database_path = 'dataset/'
#get all image names from the database
databaseNames = os.listdir(database_path)
#only use jpg files
databaseNames = [name for name in databaseNames if name.endswith(".jpg")]
#remove the file extension by removing the last 4 characters
databaseNames = [name[:-4] for name in databaseNames]

#calculate the face vetors for the database
#database_face_vectors = [DeepFace.represent("dataset/"+name+".jpg") for name in databaseNames]
#print("face_vectors: ",face_vectors)



cap = None

xs, ys, ws, hs, faces,confidences,extractedfaces = [], [], [], [], [], [], []
img = None
framewidth = 0
frameheight = 0

#get face position
def get_face_position():
    global xs, ys, ws, hs, faces,confidences,img,extractedfaces
    #make the image suilable for deepface
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #get face position
    faces = DeepFace.extract_faces(img, enforce_detection=False)
    #print(faces[0])
    xs, ys, ws, hs, extractedfaces, confidences = [], [], [], [],[],[]
    #nurmber_of_faces = len(faces)
    #print(f"Found {nurmber_of_faces} faces")
    for face in faces:
        extractedface=face["face"] #= extracted image?
        x, y, w, h = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
        #print(f"Face found at X: {x}, Y: {y}, Width: {w}, Height: {h}")
        confidence = face["confidence"]
        xs.append(x)
        ys.append(y)
        ws.append(w)
        hs.append(h)
        extractedfaces.append(extractedface)
        confidences.append(confidence)

    #sort by face width
    xs, ys, ws, hs, faces,confidences = zip(*sorted(zip(xs, ys, ws, hs, faces,confidences), key=lambda x: x[2]))
        
    return xs, ys, ws, hs, extractedfaces, confidences

#init camera
def init_camera():
    global cap
    global framewidth, frameheight
    #init camera
    cap = cv2.VideoCapture(0)
    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")
        return None
    #get the resolution
    framewidth  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
    frameheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float

    #return cap



#get the image from the camera
def get_image_from_camera():
    global cap

    # Capture frame-by-frame
    ret, frame = cap.read()

    # If frame is read correctly, ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        return None

    return frame

#update faces
def update_faces():
    global xs, ys, ws, hs, faces,confidences,img
    #get the image from the camera
    img = get_image_from_camera()
    #get face position
    xs, ys, ws, hs, faces,confidences = get_face_position()

#verify the person name from the image
def identify_person(face,name):
 
    result = DeepFace.verify("dataset/"+name+".jpg", face, enforce_detection=False)
    verified=result["verified"]


    if verified:
        return name
    else:
        return ""

#check wich person is in the image compared to the database
def identify_persons(face,names):
    #global  faces
    namenumber=len(names)
    #create and allnames Array wiht the length len(faces)
    allnames=""#[""]*len(faces)
    for i in range(namenumber):
        name=names[i]
        #compare the faces
        oneperson = identify_person(face,name)
        #combine the strings in both lists
        #for j in range(len(onepersonlist)):
        #    allnames[j]=allnames[j]+"/"+onepersonlist[j]
        if allnames=="":
            allnames=oneperson
        else:
            allnames=allnames+" or "+oneperson
    return allnames
    

#show a demo if main
if __name__ == "__main__":
    import pygame
    pygame.init()
    pygame.mixer.init()
    #start the pygame window
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Video")
    #init camera
    init_camera()
    #start the main loop
    running = True
    frame=0
    names=[""]
    while running:
        frame+=1
        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        #update face position, vector ans so on
        update_faces()
        
        #plot the image
        screen.blit(pygame.image.frombuffer(img.tostring(), img.shape[1::-1], "BGR"), (0, 0))

        #compare the faces
        #names=verify_person("Cornelius.Klas.JPG")


 
        #plot the face position with pygame
        face_number=len(faces)
        #only the first face
        #face_number=1
        for i in range(face_number):
            x, y, w, h,face, confidence, extractedface = xs[i], ys[i], ws[i], hs[i],faces[i], confidences[i], extractedfaces[i]
            if confidence > 0.5:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, w, h), 2)
                
                #check every n frames
                n=1
                if False: #frame%n==0:
                    names=identify_persons(extractedface,["Cornelius.Klas","Casimir.Hee"])#databaseNames)
                    font = pygame.font.SysFont('Arial', 15)
                    text = font.render(names, True, (255, 0, 0))
                    screen.blit(text, (x, y))
    
        #update the display
        pygame.display.update()
    

        
    # When everything done, release the video capture object
>>>>>>> 5a8394f52afdf53d4be1d96fbdf1e105decc4505
    cap.release()