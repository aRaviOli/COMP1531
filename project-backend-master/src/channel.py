from src.admin_helper import get_user
from src.channel_helper import add_user_to_channel,remove_user_from_channel, search_for_channel, search_for_user_in_channel, search_for_user_in_store, valid_token
from src.channel_helper import search_for_owner_in_channel, if_invalid_access
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import clear_v1
from src.user_helper import involvement_rate, search_for_user, update_userspace, utilization_rate

# <a user already present in a channel invites another existing user
# to the channel provided they are not already in it. the invited user
# is automatically added to the channel>
#
# Arguments:
#   - token <str> : token of the inviting user
#   - channel_id <int> : id of the channel user is being invited to
#   - u_id <int> : id of the invited user
#
# Exceptions:
#   InputError  - When channel_id does not match any existing channel
#               - When u_id is not a valid user
#               - When u_id is a user already in the channel
#   AccessError - When channel_id is valid but auth_user_id is not a
#                 member of the channel
#
# Return Value:
#   No return value.

def channel_invite_v2(token, channel_id, u_id):
    store = data_store.get()

    # if token does not correspond to valid user raise InputError
    auth_user = get_user(token)
        
    # search for an existing channel given channel_id, if existing
    # return said channel, if not raise InputError 
    channel = search_for_channel(store, channel_id)

    # if auth_user_id not in channel raise AccessError
    if not search_for_user_in_channel(auth_user["auth_user_id"], channel):
        raise AccessError(description="Authorised user not in channel")

    # invited_user -> the user being invited to join the channel
    # if u_id not valid raise InputError
    invited_user = search_for_user_in_store(u_id, store)

    if invited_user == None:
        raise InputError(description="User doesn't exist") 

    # if u_id is a user already in channel raise InputError
    if search_for_user_in_channel(u_id, channel):
        raise InputError(description="User being invited is already in channel")

    invited_user.pop("permission_id")

    add_user_to_channel(invited_user, channel, "all_members")

    # Notifications
    auth_user_handle = auth_user["handle_str"]
    channel_name = channel["channel_name"]
    notif_msg = f"{auth_user_handle} added you to {channel_name}"

    notification = {
        "channel_id": channel_id,
        "dm_id": -1,
        "notification_message": notif_msg
    }

    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            if len(user["notifications"]) == 20:
                user["notifications"].pop(19)
            user["notifications"].insert(0, notification)

    # Analytics
    channels_joined = search_for_user(store, "channels", "all_members", u_id)
    update_userspace(store, u_id, "channels_joined", "num_channels_joined", channels_joined)
    involvement_rate(store, u_id)
    utilization_rate(store)
    data_store.set(store)

    return {}


'''
Given a channel with ID channel_id that the authorised user is a member of, 
provide basic details about the channel.

 Arguments:
 <token> (<str>) - this is the token of the user looking for channel details
 <channel_id> (<int>) - This is the channel id
 
 Exceptions:
 InputError - Occurs when channel_id does not refer to a valid channel.
 AccessError - Occurs when channel_id is valid and the authorised user 
               is not a member of the channel

 Return Value:
 Returns a dictionary { name, is_public, owner_members, all_members }, 
 given no AccessErrors or InputErrors are raised.
 '''
def channel_details_v2(token, channel_id):    
    store = data_store.get()

    user = valid_token(store, token)

    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)

    if search_for_user_in_channel(user["u_id"], channel):
        return {
            'name': channel["channel_name"],
            'is_public': channel["is_public"],
            'owner_members': channel["owner_members"],
            'all_members': channel["all_members"]
        }
    else:
        raise AccessError(description="The user is not in the channel")

'''
Given a channel_id of a channel that the authorised user can join,
adds them to that channel.

 Arguments:
 <auth_user_id> (<int>) - this is the user_id used to create the channel
 <channel_id> (<dictionary>) - this is the dictionary containing channel_id
 
 Exceptions:
 InputError - Occurs when channel_id does not refer to a valid channel.
            - Occurs when the authorised user is already a member of the channel.
 AccessError - Occurs when channel_id refers to a channel that is private and the
               authorised user is not already a channel member and is not a global 
               owner

 Return Value:
 No return value, unless InputError or AccessError was raised.
 '''
def channel_join_v2(token, channel_id):
    store = data_store.get()
    user = valid_token(store, token)
    
    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)

    user_deets = search_for_user_in_store(user["u_id"], store)
    
    if not channel["is_public"]:
        if not user_deets["permission_id"] == 1:
            raise AccessError(description="Unable to join private channel")

    if search_for_user_in_channel(user_deets["u_id"], channel):
        raise InputError(description="User already in channel")
    
    user_deets.pop("permission_id")
    
    add_user_to_channel(user_deets, channel, "all_members")
    
    # Analytics
    channels_joined = search_for_user(store, "channels", "all_members", user["u_id"])
    update_userspace(store, user["u_id"], "channels_joined", "num_channels_joined", channels_joined)
    involvement_rate(store, user["u_id"])
    utilization_rate(store)
    data_store.set(store)

    return{}

def channel_leave_v1(token, channel_id):
    store = data_store.get()
    user = valid_token(store, token)
    
    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)
      
    if not search_for_user_in_channel(user["u_id"], channel):
        raise AccessError(description="Authorised user is not an member of the channel")

    if search_for_owner_in_channel(user["u_id"], channel):
        remove_user_from_channel(user, channel, "owner_members")

    remove_user_from_channel(user, channel, "all_members")

    # Analytics
    channels_joined = search_for_user(store, "channels", "all_members", user["u_id"])
    update_userspace(store, user["u_id"], "channels_joined", "num_channels_joined", channels_joined)
    involvement_rate(store, user["u_id"])
    utilization_rate(store)
    data_store.set(store)
    
    return{}

def channel_addowner_v1(token, channel_id, u_id):
    store = data_store.get()
    user = valid_token(store, token)

    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)

    added_owner_user = search_for_user_in_store(u_id, store)
    user_deets = search_for_user_in_store(user["u_id"], store)

    if added_owner_user == None:
        raise InputError(description="u_id does not exist in data store")

    if not search_for_user_in_channel(user_deets["u_id"], channel):
        raise InputError(description="The token used is not a member for this channel")

    if not search_for_user_in_channel(added_owner_user["u_id"], channel):
        raise InputError(description="The user to be added as an owner is not a member for this channel")

    if search_for_owner_in_channel(u_id, channel):
        raise InputError(description="User is already an owner for this channel")
    
    if not search_for_owner_in_channel(user_deets["u_id"], channel):
        if not user_deets["permission_id"] == 1:
            raise AccessError(description="Not authorised to add owner to this channel")

    added_owner_user.pop("permission_id")
 
    add_user_to_channel(added_owner_user, channel, "owner_members")
    involvement_rate(store, u_id)
    utilization_rate(store)
    data_store.set(store)

    return {}   

def channel_removeowner_v1(token, channel_id, u_id):
    store = data_store.get()
    user = valid_token(store, token)

    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)

    removed_owner_user = search_for_user_in_store(u_id, store)
    user_deets = search_for_user_in_store(user["u_id"], store)

    if removed_owner_user == None:
        raise InputError(description="u_id does not exist in data store")

    if not search_for_owner_in_channel(u_id, channel):
        raise InputError(description="Owner user to be removed, is not an owner for this channel")
    
    if not search_for_user_in_channel(user_deets["u_id"], channel):
        raise InputError(description="The authorised user is not a member for this channel")

    if not search_for_owner_in_channel(user_deets["u_id"], channel):
        if not user_deets["permission_id"] == 1:
            raise AccessError(description="Not authorised to remove owners from this channel")

    if len(channel['owner_members']) == 1:
        raise InputError(description='Cannot remove last remaining owner of this channel')
    
    removed_owner_user.pop("permission_id")

    remove_user_from_channel(removed_owner_user, channel, "owner_members")
    involvement_rate(store, u_id)
    utilization_rate(store)
    data_store.set(store)

    return {}

"""
This function returns up to 50 messages with given channel id, authorised user
and start index of the message in the channel.

Arguments
        token (String) - an encoded token
        channel_id (Integer) - a channel id
        start (Integer) - the starting index of the message in messages array.

Exception:
        InputError - channel_id does not refer to a valid channel.
                   - start is greater than the total number of messages in the
                     channel.
                     
        AccessError - channel_id is valid and the authorised user is not a
                      member of the channel.

Return Value:
        a dictionary in the form of {[messages], start, end} where messages
        in a list, start and end as Integer.
"""
def channel_messages_v2(token, channel_id, start):
    store = data_store.get()
    user = valid_token(store, token)
    channel = search_for_channel(store, channel_id)
    
    search_for_user_in_store(user["u_id"], store)

    if not search_for_user_in_channel(user["u_id"], channel):
        raise AccessError(description="User ID does not exist in this channel")

    if len(channel["messages"]) < start:
        raise InputError(description="Start index is out of bound")

    end = -1
    messages = []
    if (start + 50) < len(channel["messages"]):
        end = start + 50
        messages = channel["messages"][start:end]
    else:
        messages = channel["messages"][start:]
    
    for message in messages:
        if user["u_id"] in message["reacts"][0]["u_ids"]:
            message["reacts"][0]["is_this_user_reacted"] = True
        else:
            message["reacts"][0]["is_this_user_reacted"] = False
    
    return {
        'messages': messages,
        'start': start,
        'end': end
    }
