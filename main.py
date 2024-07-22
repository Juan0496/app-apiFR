from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Depends, HTTPException, Security
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import base64
from io import BytesIO
import pyrebase
from firebaseConfig  import autho
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import cv2
import face_recognition
import asyncio
import numpy as np
import os
import math
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials,HTTPBearer, HTTPAuthorizationCredentials
app = FastAPI()

class Usuario(BaseModel):
    email: str
    password: str

security = HTTPBearer()

cred = credentials.Certificate("./assets/homesecurity.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


@app.post('/sigin')
async def Sigin(us:Usuario):
    try:
        user = autho.sign_in_with_email_and_password(us.email, us.password)
        token = user["idToken"]  
        uid = user["localId"]     
    
    except:
      print("fallo en registro")      
      return {"error"}       
    return {"status": {token} , "uid":{uid}}



async def get_current_user_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Authorization header missing")
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token.get("uid")
        
    
    except Exception as e:
        await websocket.close(code=1008, reason="Invalid or expired token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return dict(uid=user_id)

@app.websocket('/procesamiento')
async def protected_route(websocket: WebSocket,current_user: dict = Depends(get_current_user_ws)):
    await websocket.accept()
    
    path_img_andrea="./andrea.jpg"  
    if not os.path.exists(path_img_andrea):
            await websocket.send_text("Error: File not found")
            return
    Andrea_image = cv2.imread(path_img_andrea)
    if Andrea_image is None:
            await websocket.send_text("Error: Could not load image")
            return     
    image_rgb_andrea = cv2.cvtColor(Andrea_image , cv2.COLOR_BGR2RGB)  
    Andrea_face_encoding = face_recognition.face_encodings(image_rgb_andrea)[0]   
    path_img_juan="./Juan.jpg"
    Juan_image = cv2.imread(path_img_juan)
    image_rgb_juan = cv2.cvtColor(Juan_image, cv2.COLOR_BGR2RGB)
    Juan_face_encoding = face_recognition.face_encodings(image_rgb_juan)[0]
    known_face_encodings = [
        Andrea_face_encoding,
        Juan_face_encoding
    ]
    known_face_names = [
        "Andrea Moreno",
        "Juan Moreno"
    ]
    des = 1
    det = 1
    nodet = 1
    rostro=" "
    try:                
        user = current_user['uid']
        doc_ref = db.collection("usuarios").document(user).get()
        doc = doc_ref.to_dict()
        url = doc.get('url')
        if not doc_ref:
            return("No se encontro la direccion de la camara")
        camera_ip_url = "rtsp://admin:forbidenmemoris4@192.168.18.65:554/Streaming/Channels/1"
        cap = cv2.VideoCapture(camera_ip_url)
        if not cap.isOpened():
            print("Error al abrir el stream de la cámara IP")
            exit()        
        while True:
            ret, frame = cap.read()
            if ret == False:
                continue
            frame = cv2.flip(frame, 1)           
            face_locations= face_recognition.face_locations(frame )
            face_encodings = face_recognition.face_encodings(frame , face_locations)       
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
                rostro=" "        
                nodet+=1
                des=1
                det=1
                
            if det == 2 or  (det % 200) == 0:
                await websocket.send_text(f"La camara detectó a {rostro}")
                print(f"La camara detectó a {rostro}")
            elif (des==2) or (des % 200)  == 0:
                await websocket.send_text(f"La camara detectó un rostro {rostro}")
                print(f"La camara detectó un rostro {rostro}")
            elif (nodet ==2) or (nodet % 200) == 0:
                await websocket.send_text(f"No se detectó ningún rostro aun")      
                print(f"No se detectó ningún rostro aun")   
           
         
    
        
    except WebSocketDisconnect:
        print("Client disconnected")
        cap.release()  

    return{"prueba exitosa"}
EXPO_PUSH_ENDPOINT = "https://exp.host/--/api/v2/push/send"

class Mensaje(BaseModel):
    expo_push_token: str
    title: str
    body: str
@app.post("/send_notification/")
async def send_notification(mensaje:Mensaje):
    print(mensaje.body)
    message = {
        "to": mensaje.expo_push_token,
        "sound": "default",
        "title": mensaje.title,
        "body": mensaje.body,
        "data": {"someData": "goes here"},
    }
    headers = {
        "Accept": "application/json",
        "Accept-encoding": "gzip, deflate",
        "Content-Type": "application/json",
    }
    response = requests.post(EXPO_PUSH_ENDPOINT, json=message, headers=headers)
    return {"message": "Notification sent", "response": response.json()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
