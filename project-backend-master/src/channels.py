from datetime import datetime
from src.channel_helper import valid_token, if_invalid_access
from src.data_store import data_store
from src.error import AccessError, InputError
from src.user_helper import involvement_rate, search_for_user, update_userspace, update_workspace, utilization_rate

# <provides a list of channels that the authorised user is a part of>
#
# Arguments:
#   <auth_user_id> (<int>): the user that we are searching for in channels
#
# Exceptions:
#   InputError - when auth_user_id is not a registered user
#
# Return Value:
#   A list of dictionaries with types {channel_id, name}

def channels_list_v2(token):
    store = data_store.get()
    token_data = valid_token(store, token)
    
    if_invalid_access(token_data)

    user_id = token_data["u_id"]
    
    user_channels = []
    for channel in store["channels"]:
        is_public = channel["is_public"]
        for member in channel["all_members"]:
            if member["u_id"] == user_id and is_public:
                id_and_name_dict = {
                    "channel_id": channel["channel_id"],
                    "name": channel["channel_name"]
                }
                user_channels.append(id_and_name_dict)
    return {
        'channels': user_channels
    }

# <provides a list of all existing channels including all private channels>
#
# Arguments:
#   <auth_user_id> (<int>): the id of the user
#
# Exception:
#   AccessError - when auth_user_id is not a registered user
#
# Return Value:
#   A list of dictionaries with types {channel_id, name}

def channels_listall_v2(token):
    store = data_store.get()
    channels = []
    # check if user id is in list of users. 
    token = valid_token(store, token)
    
    if_invalid_access(token)
    
    for channel in store["channels"]:
        id_and_name_dict = {
            "channel_id": channel["channel_id"],
            "name": channel["channel_name"]
        }
        channels.append(id_and_name_dict)    
    
    return {
        "channels": channels
    }

# <channels_create_v2 creates a channel and assigns the id of the user who
# created the channel as owner and returns a successful channel_id>
#
# Arguments:
# <token> (<str>) - this is the identification used to create the channel
# <name> (<str>) - this is the name of the new channel
# <is_public> (<boolean>) - this is the publicity of the channel (True if
#                           public, False if private)
# 
# Exceptions:
# InputError - Occurs when any of the 3 arguments entered does not match
#              the requirements
# AccessError - Occurs when the token used to create a channel
#               is not registered in the database
#
# Return Value:
# Returns <channel_id> as an int on <when InputError or AccessError 
# is not raised>
def channels_create_v2(token, name, is_public):
    store = data_store.get()
    channel_id = len(store["channels"])

    if not isinstance(is_public, bool):
        raise InputError("is_public must be set to boolean type True of False")
    
    owner = valid_token(store, token)

    if_invalid_access(owner)
    
    if 0 < len(name) < 21:
        # If the length of the channel name is between 1 to 20 characters then 
        # store the data
        new_channel = {
            "channel_id": channel_id,
            "channel_name": name,
            "is_public": is_public,
            "owner_members": [],
            "all_members": [],
            "messages": [],
            "standup": {"is_active": False,
                        "time_finish": None,
                        "stored_standup_strings": []
            },

        }
        new_channel["owner_members"].append(owner)
        new_channel["all_members"].append(owner)
        store["channels"].append(new_channel)

        # Analytics
        channels_joined = search_for_user(store, "channels", "all_members", owner["u_id"])
        update_userspace(store, owner["u_id"], "channels_joined", "num_channels_joined", channels_joined)
        update_workspace(store, "channels_exist", "num_channels_exist", "channels")
        involvement_rate(store, owner["u_id"])
        utilization_rate(store)

        data_store.set(store)

        return {
            "channel_id": new_channel["channel_id"]
        }
    # Name longer than 20 characters, so raise exception
    raise InputError(description="Channel name must be between 1 to 20 characters")
