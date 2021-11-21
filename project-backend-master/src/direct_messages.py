from datetime import datetime
from src.channels import channels_create_v2
from src.channel_helper import valid_token, if_invalid_access
from src.data_store import data_store
from src.dm_helper import find_dm, find_member
from src.error import InputError, AccessError
from src.jwt_helpers import decode_jwt
from src.other import clear_v1
from src.user_helper import existing_messages, involvement_rate, search_for_user, update_userspace, update_workspace, utilization_rate

# <Creates a new dm chat with the person who created it set as the owner
# and and adds members to the chat based on the u_ids supplied.>
#
# Arguments:
#   <token> (<string>): token of the person who will be the dm owner.
#   <u_ids> (<int list>): list of user id's.
#
# Exceptions:
#   InputError - one or more of the u_ids are not found in data. 
#   AccessError - Invalid token is supplied. 
#
# Return Value:
#   A dictionary containing the dm_id of the dm {dm_id}
def dm_create_v1(token, u_ids):
    store = data_store.get()
    dm_id = 0
    for dm in store["direct_messages"]:
        if dm_id == dm["dm_id"]:
            dm_id += 1
    
    owner_dictionary = valid_token(store, token)
    
    if_invalid_access(owner_dictionary)

    all_members = []
    # add owner_dictionary to all_members.            
    all_members.append(owner_dictionary)
    
    # add members to all_members
    for user_id in u_ids:
        if user_id == owner_dictionary["u_id"]:
            raise InputError(description="Owner id in u_ids")
        user_found = False
        for user in store["users"]:
           
            if user_id == user["auth_user_id"]:
                user_found = True
                found_member_dict = {
                        "u_id": user["auth_user_id"],
                        "email": user["email"],
                        "name_first": user["name_first"], 
                        "name_last": user["name_last"],
                        "handle_str": user["handle_str"],
                        "profile_img_url": user["profile_img_url"]
                }
                all_members.append(found_member_dict)
                
        if user_found == False:
            raise InputError(description="An input user_id is not in the list of users.") 
    
    # create channel name from user handles. 
    list_of_handles = []
    for member in all_members:
        list_of_handles.append(member["handle_str"])    
    list_of_handles.sort()
    
    name = ''
    for handle_index in range(0, len(list_of_handles)):
        
        if handle_index != len(list_of_handles) -1:
            name = name + list_of_handles[handle_index] + ", "
        else:
            name = name + list_of_handles[handle_index]

    new_dm = {
        "dm_id": dm_id,
        "name": name,
        "owner": [owner_dictionary],
        "all_members": all_members,
        "messages": []
    }
    store["direct_messages"].append(new_dm)

    # Notifications
    user_handle = owner_dictionary["handle_str"]
    dm_name = name
    notif_msg = f"{user_handle} added you to {dm_name}"
    
    notification = {
        "channel_id": -1,
        "dm_id": dm_id,
        "notification_message": notif_msg
    }

    for user in store["users"]:
        if user["auth_user_id"] in u_ids:
            if len(user["notifications"]) == 20:
                user["notifications"].pop(19)
            user["notifications"].insert(0, notification)

    # Analytics
    dms_joined_owner = search_for_user(store, "direct_messages", "all_members", owner_dictionary["u_id"])
    update_userspace(store, owner_dictionary["u_id"], "dms_joined", "num_dms_joined", dms_joined_owner)
    for u_id in u_ids:
        dms_joined_u_id = search_for_user(store, "direct_messages", "all_members", u_id)
        update_userspace(store, u_id, "dms_joined", "num_dms_joined", dms_joined_u_id)
        involvement_rate(store, u_id)
    update_workspace(store, "dms_exist", "num_dms_exist", "direct_messages")
    utilization_rate(store)
    
    data_store.set(store)

    return {"dm_id": new_dm["dm_id"]} 
      
# <Given a user token returns a list of channel names and id's that user is a 
# part of >
#
# Arguments:
#   <token> (<string>): the user that we are searching for in dm's
#
# Return Value:
#   A list of dictionaries with types {dm_id, name}            
    
def dm_list_v1(token):
    store = data_store.get()
    user = valid_token(store, token)
    # iterate through the dms and check if the user is a member. If so add to
    # list of dms. 
    
    dm_list = []
    
    for dm in store["direct_messages"]:
        for member in dm["all_members"]:
            if user["u_id"] == member["u_id"]:
                dm_info_dict = {
                    "dm_id": dm["dm_id"],
                    "name": dm["name"]
                }
                dm_list.append(dm_info_dict)
    return {"dms": dm_list}     
    
# <Removes a direct message chat from the data store if the user attempting to
# remove the dm is the owner.>
#
# Arguments:
#   <token> (<string>): The owner of the chat  
#   <dm_id> (<int>): the dm to be removed. 
#
# Exceptions:
#   AccessError - when user is not the owner of the chat.
#   InputError - when the dm with dm_id does not exist.  
#
# Return Value:
#   empty dict   
def dm_remove_v1(token, dm_id):
    store = data_store.get()
    token_data = decode_jwt(token)
    token_id = token_data["auth_user_id"]
    valid_user = False
    
    # check if dm_id exists
    for dm in store["direct_messages"]:
        if dm["dm_id"] == dm_id:
            if len(dm["owner"]) == 0:
                raise AccessError(description="The original creator is removed from Streams")
            if dm["owner"][0]["u_id"] == token_id:
                valid_user = True
            else:
                raise AccessError(description="User associated with token is not an owner")
    if valid_user == False:
        raise InputError(description="dm_id is invalid.")
    
    for dm in store["direct_messages"]:
        if dm["dm_id"] == dm_id:
            for members in dm["all_members"]:
                # Analytics
                dms_joined = search_for_user(store, "direct_messages", "all_members", members["u_id"]) - 1
                update_userspace(store, members["u_id"], "dms_joined", "num_dms_joined", dms_joined)
                involvement_rate(store, members["u_id"])
            store["direct_messages"].remove(dm)
            
    # Analytics
    update_workspace(store, "dms_exist", "num_dms_exist", "direct_messages")
    total_messages = existing_messages(store)
    update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
    utilization_rate(store)
    data_store.set(store)        
    return {}    
    #check if person trying to delete is the owner. 
    
# <Provides the details of a dm if the user is member>
#
# Arguments:
#   <token> (<string>): A member of the dm
#   <dm_id> (<int>): id of the dm to provide details for
#
# Exceptions:
#   AccessError - when user is not a member
#   InputError - when dm with dm_id does not exist.  
#
# Return Value:
#   A dictionary with types {name, all_members}    
def dm_details_v1(token, dm_id):
    store = data_store.get()
    #check chat is valid and then if the user is a member.
    dm_chat = find_dm(dm_id, store)
    if dm_chat == None:
        raise InputError(description="Invalid dm_id")     
    member = find_member(token, dm_chat, store)
    if member == None:
        raise AccessError(description="User is not a member of dm")

    return {
        "name" : dm_chat["name"], 
        "members": dm_chat["all_members"] 
    }    
    
# <Allows a member of a dm to leave that dm>
#
# Arguments:
#   <token> (<string>): the user to be removed
#
# Exceptions:
#   AccessError - when user is not a member
#   InputError - when dm with dm_id does not exist.  
#
# Return Value:
#   empty dict 
def dm_leave_v1(token, dm_id):
    store = data_store.get()
    user = valid_token(store, token)

    if_invalid_access(user)

    found_dm = find_dm(dm_id, store)
    if found_dm == None:
        raise InputError(description="Invalid dm_id")
        
    member = find_member(token, found_dm, store)    
    if member == None:
        raise AccessError(description="User is Already not a member of the chat.")
    
    for dm in store["direct_messages"]:
        if dm["dm_id"] == dm_id:
            dm["all_members"].remove(member)
            if dm["owner"][0] == member:
                dm["owner"][0] = [{}]
    # Analytics
    dms_joined = search_for_user(store, "direct_messages", "all_members", user["u_id"])
    update_userspace(store, user["u_id"], "dms_joined", "num_dms_joined", dms_joined)
    involvement_rate(store, user["u_id"])
    utilization_rate(store)
    data_store.set(store)
    return {}

# <returns up to 50 messages starting from start index from a dm>
#
# Arguments:
#   <token> (<string>): the user to be removed
#   <dm_id> (<int>): the dm messages are being returned from
#   <start> (<int>): the index where the messages start
# Exceptions:
#   AccessError - when user is not a member
#   InputError - when dm with dm_id does not exist.
#   InputError - when start index is out of bounds.  
#
# Return Value:
#   dictionary with list of string messages, start index and end index. 
            
def dm_messages_v1(token, dm_id, start): 
    store = data_store.get()
    dm = find_dm(dm_id, store)
    if dm == None: 
        raise InputError(description="Invalid dm_id")
        
    member = find_member(token, dm, store)    
    if member == None:
        raise AccessError(description="User is not a member of the chat.")
    if start > len(dm["messages"]):
        raise InputError(description="Invalid index. Start out of bound")
        
    end = -1
    messages = []
    if (start + 50) < len(dm["messages"]):
        end = start + 50
        messages = dm["messages"][start:end]
    else:
        messages = dm["messages"][start:]

    for message in messages:
        if member["u_id"] in message["reacts"][0]["u_ids"]:
            message["reacts"][0]["is_this_user_reacted"] = True
        else:
            message["reacts"][0]["is_this_user_reacted"] = False
    
    return {
        'messages': messages,
        'start': start,
        'end': end
    }           
