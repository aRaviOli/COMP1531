import hashlib
import jwt

SESSION_TRACKER = -1
SECRET = 'french_table'

#   generates a new sequential session ID
def new_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER
    
#   resets session ID
def reset_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER = -1

#   Creates a JWT using SECRET and algorithm HS256
def create_jwt(auth_user_id, session_id):
    return jwt.encode({"auth_user_id": auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')

#   Decodes a JWT string into an object of the data
def decode_jwt(encoded_jwt):
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])

#   Hashes the entered password with sha256
def hashing(password):
    return hashlib.sha256(password.encode()).hexdigest()