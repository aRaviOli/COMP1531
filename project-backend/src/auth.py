from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for
from random import choice
from src.auth_helper import email_check, handle, length_check
from src.data_store import data_store
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt, decode_jwt, hashing, new_session_id
from src.other import clear_v1
from src.user_helper import involvement_rate, utilization_rate
import smtplib
import string

# <auth_login_v2 takes an email and password and looks through currently
# registered accounts. If matching credentials are found then return the 
# corresponding user_id. Else return an InputError>
#
# Arguments:
#   <email> (<str>) - this is the email used to register an account
#   <password> (<str>) - data required to match corresponding to email
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - email entered does not belong to a registered user
#                   - password is not correct
#
# Return Value:
#   Returns <{token, auth_user_id}> as dict on <InputError not raised>
def auth_login_v2(email, password):
    store = data_store.get()
    
    for users in store["users"]:
        if users["email"] == email:
            # if both email and password match then return corresponding id
            if users["password"] == hashing(password):
                session_id = new_session_id()

                if session_id == 0:
                    users["permission_id"] = 1
                users["sessions"].append(session_id)

                # Analytics
                involvement_rate(store, users["auth_user_id"])
                utilization_rate(store)
                data_store.set(store)

                return {
                    "token": create_jwt(users["auth_user_id"], session_id),
                    "auth_user_id": users["auth_user_id"]
                }
    # if looped to end of users and no matching email was found
    # then inputerror -> invalid email
    raise InputError(description="Email or password is incorrect")

# <auth_logout_v1 takes a token as input and invalidates the token and its
# associated session>
# 
# Arguments:
#  - token <str>: the token for user logging out

def auth_logout_v1(token):
    store = data_store.get()

    logout_user = decode_jwt(token)

    for user in store["users"]:
        if user["auth_user_id"] == logout_user["auth_user_id"]:
            if logout_user["session_id"] in user["sessions"]:
                user["sessions"].remove(logout_user["session_id"])
            else:
                raise AccessError(description="User already logged out")

    data_store.set(store)

    return {}

# <auth_register_v2 registers an account based on the credentials it receive
# then calls auth_login_v2>
#
# Arguments:
# <email> (<str>) - this is the email used to register an account
# <password> (<str>) - this is the block of data required to successfully login
# <name_first> (<str>) - this is the user's first name
# <name_last> (<str>) - this is the user's last or family name
# 
# Exceptions:   
# InputError - Occurs when any of the 4 arguments entered does not match
#              the requirements:
#
# Return Value:
# Returns <{token, auth_user_id}> as dict on <when InputError is not raised>
def auth_register_v2(email, password, name_first, name_last):
    store = data_store.get()
    # Holds the id of the user
    new_id = len(store["users"])
    
    # If the email is invalid then raise InputError otherwise check if
    # its registered 
    if not email_check(email):
        raise InputError(description="Email is of invalid format.")
    else:
        for users in store["users"]:
            if users["email"] == email:
                raise InputError(description=f"{email} already taken")
        # Check if the length is valid
        length_check(password, name_first, name_last)
    
    # The dictionary that holds the data of the new user
    new_user = {
        "auth_user_id": new_id,
        "email": email,
        "name_first": name_first,
        "name_last": name_last,
        "handle_str": handle(store, name_first, name_last),
        "password": hashing(password),
        "sessions": [],
        "permission_id": 2,
        "reset_code": [],
        "profile_img_url": url_for("static", filename="default.jpg", _external=True),
        "notifications": []
    }

    # Analytics
    time_stamp = int(datetime.now().timestamp())
    if new_user["auth_user_id"] == 0:
        store["workspace_stats"]["channels_exist"].append({"num_channels_exist": 0, "time_stamp": time_stamp})
        store["workspace_stats"]["dms_exist"].append({"num_dms_exist": 0, "time_stamp": time_stamp})
        store["workspace_stats"]["messages_exist"].append({"num_messages_exist": 0, "time_stamp": time_stamp})
        store["workspace_stats"]["utilization_rate"] = 0
    
    store["user_stats"].append({
        "channels_joined": [{"num_channels_joined": 0,"time_stamp": time_stamp}],
        "dms_joined": [{"num_dms_joined": 0, "time_stamp": time_stamp}],
        "messages_sent": [{"num_messages_sent": 0, "time_stamp": time_stamp}],
        "involvement_rate": 0
    })

    # Append the data to the list
    store["users"].append(new_user)
    data_store.set(store)
    
    return auth_login_v2(email, password)

# <auth_passwordreset_request_v1 sends an email containing the secret code
# for resetting password
#
# Arguments:
# <email> (<str>) - this is the email that requested the password reset
def auth_passwordreset_request_v1(email):
    store = data_store.get()
    secret_code = "".join([choice(string.ascii_uppercase + string.digits) for x in range(6)])
    found = False

    for users in store["users"]:
        if users["email"] == email:
            found = True
            users["reset_code"].append(hashing(secret_code))
            users["sessions"] = []
    
    if not found:
        return {}
    
    sender = {
        "email": "t13balpaca@gmail.com",
        "password": "frenchtable"
    }
    
    message = MIMEMultipart()
    message["Subject"] = "Forgot you Streams password?"
    message["From"] = sender["email"]
    message["To"] = email
    
    content = f'''Hi, seems like you forgot your password for Streams and requested a password reset for this email address.
    Secret code: {secret_code}
    If this was not you, please ignore this email.
    '''
    message.attach(MIMEText(content, 'plain'))
    
    # Security
    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender["email"], sender["password"])
    text = message.as_string()
    session.sendmail(sender["email"], email, text)
    session.quit()
    
    data_store.set(store)
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()

    if len(new_password) <= 6:
        raise InputError("New password is too short")

    for user in store["users"]:
        if hashing(reset_code) in user["reset_code"]:
            user["password"] = hashing(new_password)
            user["reset_code"] = []
            data_store.set(store)
            return {}

    raise InputError("Invalid reset code")