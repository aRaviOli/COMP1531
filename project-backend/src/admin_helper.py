from src.data_store import data_store
from src.error import AccessError
from src.jwt_helpers import decode_jwt

def get_user(token):
    store = data_store.get()
    token_data = decode_jwt(token)

    for user in store["users"]:
        if user["auth_user_id"] == token_data["auth_user_id"]:
            if token_data["session_id"] in user["sessions"]:
                return user
        
    raise AccessError(description="The token is invalid")

def search_for_user_in_dm(u_id, dm):
    if len(dm["owner"][0]) != 0 and dm["owner"][0]["u_id"] == u_id:
        return True

    for user in dm["all_members"]:
        if user["u_id"] == u_id:
            return True

    return False

def get_channel_member(u_id, channel):
    channel_member = {}
    for member in channel["all_members"]:
        if member["u_id"] == u_id:
            channel_member = member
    
    return channel_member

def get_dm_member(u_id, dm):
    dm_member = {}
    for member in dm["all_members"]:
        if member["u_id"] == u_id:
            dm_member = member
            
    return dm_member
