"""Available formats for Stereo USB Camera
1 camera:
{'index': 0, 'media_type_str': 'MJPG', 'width': 1280, 'height': 720, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 2, 'media_type_str': 'MJPG', 'width': 640, 'height': 480, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 4, 'media_type_str': 'MJPG', 'width': 640, 'height': 360, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 6, 'media_type_str': 'MJPG', 'width': 1280, 'height': 712, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 8, 'media_type_str': 'MJPG', 'width': 640, 'height': 472, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 10, 'media_type_str': 'MJPG', 'width': 640, 'height': 352, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
2 cameras:
{'index': 12, 'media_type_str': 'MJPG', 'width': 2560, 'height': 720, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 14, 'media_type_str': 'MJPG', 'width': 1280, 'height': 480, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 16, 'media_type_str': 'MJPG', 'width': 1280, 'height': 360, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
1 camera:
{'index': 18, 'media_type_str': 'YUY2', 'width': 1280, 'height': 720, 'min_framerate': 10.0, 'max_framerate': 5.0}
{'index': 20, 'media_type_str': 'YUY2', 'width': 640, 'height': 480, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 22, 'media_type_str': 'YUY2', 'width': 640, 'height': 360, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 24, 'media_type_str': 'YUY2', 'width': 1280, 'height': 712, 'min_framerate': 10.0, 'max_framerate': 5.0}
{'index': 26, 'media_type_str': 'YUY2', 'width': 640, 'height': 472, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
{'index': 28, 'media_type_str': 'YUY2', 'width': 640, 'height': 352, 'min_framerate': 30.00003000003, 'max_framerate': 5.0}
2 cameras, slow:
{'index': 30, 'media_type_str': 'YUY2', 'width': 2560, 'height': 720, 'min_framerate': 5.0, 'max_framerate': 5.0}
2 cameras:
{'index': 32, 'media_type_str': 'YUY2', 'width': 1280, 'height': 480, 'min_framerate': 15.000015000015, 'max_framerate': 5.0}
{'index': 34, 'media_type_str': 'YUY2', 'width': 1280, 'height': 360, 'min_framerate': 25.0, 'max_framerate': 5.0}

"""
import pygame
import cv2
#import os
#import sys
#from numpy import dot
#from numpy.linalg import norm
#import cv2.aruco as aruco
print(cv2.__version__)
import numpy as np
import time

angles=[[None],[None],[None],[None],[None]] #time, angle01, angle23, angle0123, marker
positions = [[0],[0],[0],[0],[0],[0],[0]] #time x,y,z of first marker pair x,y,z of second marker pair

virtual_distance1 = -0.08+0.25
virtual_distance2 = -0.08

drawNaruco = True

calibration_matrix_pathL = "calibration\calibration_matrixL.npy"
distortion_coefficients_pathL = "calibration\distortion_coefficientsL.npy"
calibration_matrix_pathR = "calibration\calibration_matrixR.npy"
distortion_coefficients_pathR = "calibration\distortion_coefficientsR.npy"
save_path = "calibration/measurement/"

refine = True

k = [np.load(calibration_matrix_pathL),np.load(calibration_matrix_pathR)]
d = [np.load(distortion_coefficients_pathL),np.load(distortion_coefficients_pathR)]

#internal Camera=0, stereo camera=1
cameraID = 1
framewidth = 1280
frameheight= 720
stereo = True
baseline=0.085
marker_size=0.0393
plotAngles = True
plotPosition = False

#init camera
def init_camera():
    global cap
    global framewidth, frameheight

    #init camera 
    cap = cv2.VideoCapture(cameraID+cv2.CAP_DSHOW)
    #change the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, framewidth*(1+stereo))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frameheight)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    #cap.set(cv2.CAP_PROP_FPS, 30)




    
    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")
        return None
    #get the resolution
    #framewidth  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
    #frameheight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float
    print("Camera resolution: ",framewidth*(1+stereo),frameheight)
   

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

#update positions
def update_camera(matrix_coefficients, distortion_coefficients):
    global img
    global framewidth, frameheight
    #2 images
    img = [None, None]
    corners = [None, None]
    ids = [None, None]
    rvecs = [None, None]
    tvecs = [None, None]
    #get the image from the camera
    full_img = get_image_from_camera()
    if stereo:
        #split the image in 2 parts because od the stereo camera
        img = [full_img[:, :int(framewidth)], full_img[:, int(framewidth):]]
    else:
        img = [full_img]
    

    #process the images
    for lr in range(len(img)):    
    
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
        parameters = cv2.aruco.DetectorParameters_create()
        # Convert the image to grayscale
        gray = cv2.cvtColor(img[lr], cv2.COLOR_BGR2GRAY)
        # Detect Aruco markers
        corners[lr], ids[lr], rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

        if len(corners[lr]) > 0:
            # Refine the corners
            if refine==True:
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.00001)
                for corner in corners[lr]:
                    cv2.cornerSubPix(gray, corner, winSize = (3,3), zeroZone = (-1,-1), criteria = criteria)
                    #Please note that cv2.cornerSubPix() modifies the corners in-place, so the corners in your corners list will be updated with their refined locations.
                # Estimate the pose of the markers
            rvecs[lr], tvecs[lr], _ = cv2.aruco.estimatePoseSingleMarkers(corners[lr], marker_size, matrix_coefficients[lr], distortion_coefficients[lr])
        
    #we have 4 markers with ids 0,1,2,3 in markers list
    #the list is composed of [index] [RLCombi] [tvec]
    markers = [[None,None,None],[None,None,None],[None,None,None],[None,None,None]]
    for lr in range(2):
        if ids[lr] is not None:
            for i in range(len(ids[lr])):
                if ids[lr][i] == 0:
                    markers[0][lr] = (tvecs[lr][i][0])
                if ids[lr][i] == 1:
                    markers[1][lr] = (tvecs[lr][i][0])
                if ids[lr][i] == 2:
                    markers[2][lr] = (tvecs[lr][i][0])
                if ids[lr][i] == 3:
                    markers[3][lr] = (tvecs[lr][i][0])


    for id in range(4):
        #get the translation vectors of the markers
        tvecL = markers[id][0]
        tvecR = markers[id][1]

        #calculate the distance of the markers based on the stereo angles
        if tvecL is not None and tvecR is not None:
            #calculate the marker angle on each camera image  in x direction
            tan_anglexL = (tvecL[0]/tvecL[2])
            tan_anglexR = (tvecR[0]/tvecR[2])
            #calculate the marker angle on each camera image  in y direction
            tan_angleyL = (tvecL[1]/tvecL[2])
            tan_angleyR = (tvecR[1]/tvecR[2])

            #calculate the distance to the stereo camera based on 2 angles and the distance between the cameras
            z = baseline/(tan_anglexL-tan_anglexR)
            x = (z*tan_anglexL+z*tan_anglexR)/2
            y= (z*tan_angleyL+z*tan_angleyR)/2

            #put the stereo distance in the marker list
            markers[id][2]=np.array([x,y,z])

            #draw the distance on the image
            #cv2.putText(img[0], "Distance: "+str(z), (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            #cv2.putText(img[0], "X: "+str(x), (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            #cv2.putText(img[0], "Y: "+str(y), (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        else:
            if tvecL is not None:
                markers[id][2]=tvecL
            if tvecR is not None:
                markers[id][2]=tvecR
        

    angle01 = None
    angle23 = None
    angle0123 = None
    #get system time
    time = cv2.getTickCount()
    xaxis = np.array([1,0,0])
    normal = np.array([0,0,1])

    # Define a function to calculate the signed angle between two vectors
    def signed_angle(vector1, vector2, normal):
        angle = np.arccos(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))
        cross_product = np.cross(vector1, vector2)
        if np.dot(cross_product, normal) < 0:  # Or > 0 depending on the direction of your coordinate system
            angle = -angle
        return angle/np.pi*180

    #calculate the vector between marker 0 and 1
    #markers[id][2] is the translation vector of the marker
    if markers[0][2] is not None and markers[1][2] is not None:
        vector01 = markers[1][2]-markers[0][2]
        vector01 = vector01.flatten()
        #calculate the 3d angle beween xaxis and the vecto01
        angle01 = signed_angle(xaxis, vector01, normal)
    #calculate the vector between marker 2 and 3
    if markers[2][2] is not None and markers[3][2] is not None:
        vector23 = markers[3][2]-markers[2][2]
        vector23 = vector23.flatten()
        angle23 = signed_angle(xaxis, vector23, normal)
    #calculate the angle between the 2 vectors
    if angle01 is not None and angle23 is not None:
        angle0123 = signed_angle(vector01, vector23, normal)

    filter = 0.5
    #low pass filter hte time series
    if angles[1][-1] is not None and angle01 is not None:
        angle01 = angles[1][-1]*(1-filter)+angle01*filter

    if angles[2][-1] is not None and angle23 is not None:
        angle23 = angles[2][-1]*(1-filter)+angle23*filter

    if angles[3][-1] is not None and angle0123 is not None:
        angle0123 = angles[3][-1]*(1-filter)+angle0123*filter

    angles[0].append(time)
    angles[1].append(angle01)
    angles[2].append(angle23)
    angles[3].append(angle0123)
    angles[4].append(None)

    #calculate the position of the markers. the position is relatice to the positions of the marker pairs
    #add time
    
    timetemp=None

    if markers[0][2] is not None and markers[1][2] is not None:
        vector = (markers[0][2]-markers[1][2])
 
        position = markers[0][2] + vector / np.linalg.norm(vector) *virtual_distance1
        positions[1].append(position[0])
        positions[2].append(position[1])
        positions[3].append(position[2])
        timetemp = time
        

    if markers[2][2] is not None and markers[3][2] is not None:
        vector=(markers[2][2]-markers[3][2])
        position = markers[2][2] + vector / np.linalg.norm(vector)*virtual_distance2
        positions[4].append(position[0])
        positions[5].append(position[1])
        positions[6].append(position[2])
        timetemp = time

    if timetemp is not None:
        positions[0].append(timetemp)

    

    if drawNaruco:  
        #draw the resulting translation (markers[id][2]) of the 4 relevant markers on the image
        vector_str="None"
        for id in range(4):
            if markers[id][2] is not None:
                vector_str = ", ".join("{:.2f}".format(x) for x in markers[id][2])
            cv2.putText(img[0], "T: " + vector_str, (10, 60+30*id), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        if angles[3][-1] is not None:
            cv2.putText(img[0], "Angle: {:.2f}".format(angles[3][-1]), (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        if positions[1][-1] is not None:
            cv2.putText(img[0], "Position1: {:.4f}, ".format(positions[1][-1])+"{:.4f}, ".format(positions[2][-1])+"{:.4f}, ".format(positions[3][-1]), (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        if positions[4][-1] is not None:
            cv2.putText(img[0], "Position2: {:.4f}, ".format(positions[4][-1])+"{:.4f}, ".format(positions[5][-1])+"{:.4f}, ".format(positions[6][-1]), (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        for lr in range(2):  
            #plot the markers on the first image
            img[0] = cv2.aruco.drawDetectedMarkers(img[0], corners[lr], ids[lr])

#save the image
def save_image(image):
    cv2.imwrite(save_path+str(time.time())+"L.png", image[0])
    if stereo:
        cv2.imwrite(save_path+str(time.time())+"R.png", image[1])

#save the angle data to a file in save_path
def save_data(angle_data, position_data):
    np.save(save_path+"angles", angle_data)
    np.save(save_path+"positions", position_data)


#show a demo if main
if __name__ == "__main__":

    import matplotlib.pyplot as plt

    if plotAngles:
        # Create a new figure for the plot
        fig, ax = plt.subplots()
        # Initialize the plot lines
        line01, = ax.plot([], [], '-', color='blue', alpha=0.5)
        line23, = ax.plot([], [], '-', color='red', alpha=0.5)
        line0123, = ax.plot([], [], color='red')
        linemarker, = ax.plot([], [], 'o', color='black')

    if plotPosition:
        #create a second plot for the position
        #it is a 3d plot
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111, projection='3d')
        # Initialize the plot lines
        position01, = ax2.plot([], [], [], '-', color='blue', alpha=0.5)



    # Create a clock object
    clock = pygame.time.Clock()
    pygame.init()
    pygame.mixer.init()
    #start the pygame window
    screen = pygame.display.set_mode((1280, 900))
    pygame.display.set_caption("Video")


    init_camera()
    #start the main loop
    running = True
    #frame=0

    while running:
 
        #frame+=1
        # Get the current FPS
        fps = clock.get_fps()
  

        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # Check if 'm' key is pressed
        #save pictures and mark the event in angles data
        if keys[pygame.K_m]:
            # Save the image
            save_image(img)
            if angles[3][-1] is not None:
                angles[4][-1] =  angles[3][-1]
            elif angles[1][-1] is not None:
                angles[4][-1] =  angles[1][-1]
            elif angles[2][-1] is not None:
                angles[4][-1] =  angles[2][-1]

        # Save the data on "s"
        if keys[pygame.K_s]:
            save_data(angles, positions)

        #toggle refind on r
        if keys[pygame.K_r]:
            refine = not refine
            print("Refine: ", refine)

        #clear the plot on c
        if keys[pygame.K_c]:
            angles=[[None],[None],[None],[None],[None]]
            positions = [[0],[0],[0],[0],[0],[0],[0]]

        #update the plot

        if plotAngles:
            # Plot the angles
            #print(angles)
            line01.set_data(angles[0], angles[1])
            line23.set_data(angles[0], angles[2])
            line0123.set_data(angles[0], angles[3])
            linemarker.set_data(angles[0], angles[4])
        if plotPosition:
            #plot the position
            position01.set_data(positions[1], positions[2])
            position01.set_3d_properties(positions[3])
        
        # Adjust the plot limits
        if plotAngles:
            ax.relim()
            ax.autoscale_view()
        if plotPosition:
            ax2.relim()
            ax2.autoscale_view()

        # Redraw the plot
        plt.draw()
        plt.pause(0.01)
    


        #update position...
        update_camera(k,d)
        #draw framerate
        if drawNaruco:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img[0], "FPS: {:.2f}".format(fps), (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        #draw a vertical line on the image
        cv2.line(img[0], (640, 0), (640, 720), (255, 255, 255), 2)
        #plot the image
        if img is not None:
            screen.blit(pygame.image.frombuffer(img[0].tobytes(), img[0].shape[1::-1], "BGR"), (0, 0))
            if stereo:
                screen.blit(pygame.image.frombuffer(img[1].tobytes(), img[1].shape[1::-1], "BGR"), (0, 720))


        #update the display
        pygame.display.update()
        #limit the framerate to display fps correctly
        clock.tick(60)
    

        
    # When everything done, release the video capture object
    cap.release()