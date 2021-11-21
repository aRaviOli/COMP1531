from src.data_store import data_store
from src.error import AccessError, InputError
from src.jwt_helpers import decode_jwt
import jwt

#   Search if the channel exists in the database
def search_for_channel(store, channel_id):
    if len(store["channels"]) == 0:
        raise InputError("There are no channels")
    
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            return channel
    #if code gets to here, channel id doesn't exist
    raise InputError(description="channel_id does not exist")

#   Search for the user in the channel
def search_for_user_in_channel(auth_user_id, channel):
    for user in channel["all_members"]:
        if user["u_id"] == auth_user_id:
            return True
    return False 

#   Search for the owner in the channel
#
#   Args:
#       - auth_user_id <id>: The u_id being searched
#       - channel <dict>: The dict containing specific channel
#
#   Returns:
#       - True <bool>: If user is an owner in the channel
#       - False <bool>: If user is not an owner in the channel
def search_for_owner_in_channel(u_id, channel):
    for user in channel["owner_members"]:
        if user["u_id"] == u_id:
            return True
    return False 

#   Search for the user in the database
def search_for_user_in_store(auth_user_id, store):
    for user in store["users"]:
        if user["auth_user_id"] == auth_user_id:
            return {
                "u_id": user["auth_user_id"],
                "email": user["email"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "permission_id": user["permission_id"],
                "profile_img_url": user["profile_img_url"]
            }
    #if code made it here, user doesn't exist in user list
    #raise AccessError("User doesn't exist") 

#   Adds an user to the channel
#   Appends user to channel member type
def add_user_to_channel(user, channel, member_type):
        channel[member_type].append(user)

def remove_user_from_channel(user, channel, member_type):
        channel[member_type].remove(user)
        
#   Checks if the token is valid by checking email and
#   sesion_id after decoding
def valid_token(store, token):
    try:
        token_data = decode_jwt(token)
    except jwt.exceptions.DecodeError as error:
        raise AccessError(description="Token cannot be decoded") from error
    token_id = token_data["auth_user_id"]
    session_id = token_data["session_id"]
    token_user = None
    
    for users in store["users"]:
        if users["auth_user_id"] == token_id:
            for ids in users["sessions"]:
                if ids == session_id:
                    token_user = users
    
    if token_user != None:    
        return {
            "u_id": token_user["auth_user_id"],
            "email": token_user["email"],
            "name_first": token_user["name_first"],
            "name_last": token_user["name_last"],
            "handle_str": token_user["handle_str"],
            "profile_img_url": token_user["profile_img_url"]
        }

def if_invalid_access(item):
    if item == None:
        raise AccessError(description="The current token used is invalid")