import cv2
import numpy as np
import face_recognition
from time import sleep
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

camera_ip_url = "rtsp://admin:forbidenmemoris4@192.168.18.65:554/Streaming/Channels/1"
cap = cv2.VideoCapture(camera_ip_url)

#cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
Andrea_image = cv2.imread("andrea.JPG")
Andrea_face_encoding = face_recognition.face_encodings(Andrea_image)[0]
Juan_image = cv2.imread("Juan.JPG")
Juan_face_encoding = face_recognition.face_encodings(Juan_image)[0]
known_face_encodings = [
    Andrea_face_encoding,
    Juan_face_encoding
]
known_face_names = [
    "Andrea Moreno",
    "Juan Moreno"
]


if not cap.isOpened():
    print("Error al abrir el stream de la cámara IP")
    exit()
des = 1
det = 1
nodet = 1
rostro = ""
i=0
while i<10000:       

    ret, frame = cap.read()
    if ret == False:
        break
    frame = cv2.flip(frame, 1)
    resized_frame = cv2.resize(frame, (640, 480))

    face_locations= face_recognition.face_locations(resized_frame)
    face_encodings = face_recognition.face_encodings(resized_frame, face_locations)       
    if face_locations != []:         
        for pos, face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)            
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                rostro = name                   
                det+=1  
                des = 1
                nodet = 1
            else:
                rostro = "desconocido"                    
                des+=1
                det=1
                nodet=1
    else:
        rostro = "vacio"            
        nodet+=1
        des=1
        det=1
                    
    if det == 2 or  (det %100 == 0):
        print(f"La camara detectó a {rostro}")

       
    elif des==2 or (des %100 == 0):
        print(f"La camara detectó un rostro {rostro}")

     
    elif nodet ==2 or (nodet %100 == 0):
        print(f"No se detectó ningún rostro aun")
      
       
   
    i+=1
  
                
  
cap.release()
cv2.destroyAllWindows()




   #face_frame_encodings = face_recognition.face_encodings(frame, known_face_locations=[face_location])[0]
                # result = face_recognition.compare_faces([face_image_encodings], face_frame_encodings)