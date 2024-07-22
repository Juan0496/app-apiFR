"""

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security) ):    
    try:
        # Verifica y decodifica el token de Firebase
        decoded_token = auth.verify_id_token(credentials.credentials)        
        return decoded_token
    except:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

def get_current_user(decoded_token: dict = Depends(verify_token )):
    return User(uid=decoded_token['uid'], estado="estado")



class User(BaseModel):
    uid: str
    estado: str = None

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


@app.post('/proces')
async def protected_route(current_user: User = Depends(get_current_user)):
    print(current_user.uid)
    doc_ref = db.collection("usuarios").document(current_user.uid).get()
    doc = doc_ref.to_dict()
    url = doc.get('url')
    
    return {"exito"}
    """