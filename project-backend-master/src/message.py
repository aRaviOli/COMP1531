from src.channel_helper import search_for_channel, valid_token, search_for_user_in_channel, search_for_owner_in_channel, if_invalid_access, search_for_user_in_store
from src.data_store import data_store
from src.direct_messages import dm_details_v1
from src.dm_helper import find_dm, find_member
from src.error import InputError, AccessError
from src.general_helper import get_notif_react, get_handle_from_msg, get_notif_tag
from src.message_helper import search_for_message, search_for_channel_with_message_id, search_for_dm_with_message_id
from src.user_helper import existing_messages, involvement_rate, num_messages_sent, update_userspace, update_workspace, utilization_rate
import time
import threading

MAX_CHARACTERS = 1000
REACT_ID = 1

# <message_send_v1> send a message from the authorised user to the
# channel specified by channel id. It will return a unique message id. 
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <channel_id> (<int>) - the unique channnel id represent the channel
#   <message>(<str>) - the message to be send
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - channel_id does not refer to a valid channel
#                   - length of message is less than 1 or over 1000 characters
#   AccessError - Occurs when channel_id is valid and the user is not a
#                 member of the channel
#
# Return Value:
#   Returns <{message_id}> as dict on <InputError or AccessError not raised>    
def message_send_v1(token, channel_id, message):
    store = data_store.get()

    if (len(message) < 1 or len(message) > MAX_CHARACTERS):
        raise InputError("Message is less than 1 or more than 1000 characters.")

    # input error channel doesnt exist
    channel = search_for_channel(store, channel_id)

    user = valid_token(store, token)

    if_invalid_access(user)

    if not search_for_user_in_channel(user["u_id"], channel):
        raise AccessError(description="User not in channel")
    
    #   TAGS & NOTIFS
    tagged_user_handle = get_handle_from_msg(message)
    
    for users in store["users"]:
        if users["handle_str"] == tagged_user_handle:
            if len(users["notifications"]) == 20:
                users["notifications"].pop(19)
            users["notifications"].insert(0, get_notif_tag(user, channel, None, message))

    #   sending messages
    message_id = len(store["messages"])
    curr_time = int(time.time())
    message_details = {
        "message_id" : message_id,
        "u_id": user["u_id"],
        "message" : message,
        "time_created": curr_time,
        "reacts" : [{
            "react_id" : REACT_ID,
            "u_ids": [],
            "is_this_user_reacted" : False,
        }],
        "is_pinned": False,
    }
    channel["messages"].insert(0, message_details)
    store["messages"].append(message_details)

    # Analytics
    messages_sent = num_messages_sent(store, user["u_id"])
    update_userspace(store, user["u_id"], "messages_sent", "num_messages_sent", messages_sent)
    total_messages = existing_messages(store)
    update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
    involvement_rate(store, user["u_id"])
    utilization_rate(store)
    data_store.set(store)
    
    return {"message_id" : message_id}


# <message_edit_v1> Given a message, update its text with new text.
# If the new message is an empty string, the message is deleted
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <message_id> (<int>) - the unique massage id represent the massage
#   <message>(<str>) - the message to be send
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - message_id does not refer to a valid massage within
#                     a channel the user joined
#                   - length of message is over 1000 characters
#   AccessError - Occurs when message_id is valid and
#                   - the message was not sent by the user making this request
#                   - the user has no owner permissions
#
# Return Value:
#   Returns <{}> as dict on <InputError or AccessError not raised> 
def message_edit_v1(token, message_id, message):
    store = data_store.get()
    if len(message) > MAX_CHARACTERS:
        raise InputError("Message more than 1000 characters.")

    if message == "":
        message_remove_v1(token, message_id)
        return {}

    user = valid_token(store, token)

    if_invalid_access(user)

    for channel in store["channels"]:
        for mess in channel["messages"]:
            if mess["message_id"] == message_id:

                if not search_for_user_in_channel(user["u_id"], channel):
                    raise InputError(description="User not in channel")

                permission = search_for_user_in_store(user["u_id"], store)["permission_id"]
                if mess["u_id"] == user["u_id"] or search_for_owner_in_channel(user["u_id"], channel) or permission == 1:
                    mess["message"] = message
                    
                    #   TAGS & NOTIFS
                    tagged_user_handle = get_handle_from_msg(message)
                    
                    for users in store["users"]:
                        if users["handle_str"] == tagged_user_handle:
                            if len(users["notifications"]) == 20:
                                users["notifications"].pop(19)
                            users["notifications"].insert(0, get_notif_tag(user, channel, None, message))

                    data_store.set(store)
                    return {}
                else:
                    raise AccessError(description="No permission to remove message.")

    for dm in store["direct_messages"]:
        for mess in dm["messages"]:
            if mess["message_id"] == message_id:
                dm_member = find_member(token, dm, store)
                if dm_member == None:
                    raise InputError("User not in dm")
                if mess["u_id"] == user["u_id"] or dm["owner"][0]["u_id"] == user["u_id"]:
                    mess["message"] = message
                    
                    #   TAGS & NOTIFS
                    tagged_user_handle = get_handle_from_msg(message)
                    
                    for users in store["users"]:
                        if users["handle_str"] == tagged_user_handle:
                            if len(users["notifications"]) == 20:
                                users["notifications"].pop(19)
                            users["notifications"].insert(0, get_notif_tag(user, None, dm, message))
                    
                    data_store.set(store)
                    return {}
                else:
                    raise AccessError(description="No permission to remove message.")
    
    raise InputError(description="Invalid Message Id.")

# <message_delete_v1> Given a message_id for a message,
# this message is removed from the channel/DM
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <message_id> (<int>) - the unique massage id represent the massage
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - message_id does not refer to a valid massage within
#                     a channel the user joined
#                   - length of message is over 1000 characters
#   AccessError - Occurs when message_id is valid and
#                   - the message was not sent by the user making this request
#                   - the user has no owner permissions
#
# Return Value:
#   Returns <{}> as dict on <InputError or AccessError not raised> 
def message_remove_v1(token, message_id):
    store = data_store.get()
    
    user = valid_token(store, token)

    if_invalid_access(user)

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if not search_for_user_in_channel(user["u_id"], channel):
                    raise InputError(description="User not in channel")
                permission = search_for_user_in_store(user["u_id"], store)["permission_id"]
                if message["u_id"] == user["u_id"] or search_for_owner_in_channel(user["u_id"], channel) or permission == 1:
                    channel["messages"].remove(message)
                    # Analytics
                    total_messages = existing_messages(store)
                    update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
                    involvement_rate(store, message["u_id"])
                    utilization_rate(store)
                    data_store.set(store)
                    return {}
                else:
                    raise AccessError("No permission to remove message.")

    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message["message_id"] == message_id:
                dm_member = find_member(token, dm, store)
                if dm_member == None:
                    raise InputError(description="User not in dm")
                if message["u_id"] == user["u_id"] or dm["owner"][0]["u_id"] == user["u_id"]:
                    dm["messages"].remove(message)
                    # Analytics
                    total_messages = existing_messages(store)
                    update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
                    involvement_rate(store, message["u_id"])
                    utilization_rate(store)
                    data_store.set(store)
                    return {}
                else:
                    raise AccessError(description="No permission to remove message.")
        
    raise InputError(description="Invalid Message Id.")

# <message_senddm_v1> send a message from the authorised user to the
# dm specified by dm id. It will return a unique message id. 
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <dm_id> (<int>) - the unique dm id represent the dm
#   <message>(<str>) - the message to be send
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - channel_id does not refer to a valid channel
#                   - length of message is less than 1 or over 1000 characters
#   AccessError - Occurs when channel_id is valid and the user is not a
#                 member of the channel
#
# Return Value:
#   Returns <{message_id}> as dict on <InputError or AccessError not raised>
def message_senddm_v1(token, dm_id, message): 
    store = data_store.get()

    if (len(message) < 1 or len(message) > MAX_CHARACTERS):
        raise InputError("Message is less than 1 or more than 1000 characters.")

    user = valid_token(store, token)

    if_invalid_access(user)

    dm = find_dm(dm_id, store)
    if dm == None:
        raise InputError(description="Invalid dm_id")

    dm_member = find_member(token, dm, store)
    if dm_member == None:
        raise AccessError(description="User not in dm")
    
    #   TAGS & NOTIFS
    tagged_user_handle = get_handle_from_msg(message)
    
    for users in store["users"]:
        if users["handle_str"] == tagged_user_handle:
            if len(users["notifications"]) == 20:
                users["notifications"].pop(19)
            users["notifications"].insert(0, get_notif_tag(user, None, dm, message))

    #   sending dm message
    message_id = len(store["messages"])
    curr_time = int(time.time())
    message_details = {
        "message_id" : message_id,
        "u_id": user["u_id"],
        "message" : message,
        "time_created": curr_time,
        "reacts" : [{
            "react_id" : REACT_ID,
            "u_ids": [],
            "is_this_user_reacted" : False,
        }],
        "is_pinned": False
    }
    dm["messages"].insert(0, message_details)
    store["messages"].append(message_details)

    # Analytics
    messages_sent = num_messages_sent(store, user["u_id"])
    update_userspace(store, user["u_id"], "messages_sent", "num_messages_sent", messages_sent)
    total_messages = existing_messages(store)
    update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
    involvement_rate(store, user["u_id"])
    utilization_rate(store)
    data_store.set(store)
    return {"message_id": message_id}

# <message_share_v1> share and send a message from the authorised user to the
# dm/channel specified by dm/channel id. It will return a unique new shared message id. 
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <og_message_id> (<int>) - the unique message id represent the origin message to share
#   <message>(<str>) - the message to be send
#   <channel_id> (<int>) - the unique dm id represent the channel
#   <dm_id> (<int>) - the unique dm id represent the dm
#
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - channel or dm id does not refer to a valid channel or dm
#                   - length of message over 1000 characters
#                   - neither channel_id nor dm_id are -1
#                   - og_message_id does not refer to a valid message within a channel/DM that
#                     the user has joined
#   AccessError - Occurs when channel or dm id are valid and the user is not a
#                 member of the channel or dm
#
# Return Value:
#   Returns <{shared_message_id}> as dict on <InputError or AccessError not raised>
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    
    if len(message) > 1000:
        raise InputError("Invalid message")

    if ((channel_id == -1) ^ (dm_id == -1)) == 0:
        raise InputError("Invalid ids")

    user = valid_token(store, token)

    if_invalid_access(user)
    
    if channel_id != -1:
        search_for_channel(store, channel_id)
        for channel in store["channels"]:
            for mess in channel["messages"]:
                if mess["message_id"] == og_message_id:
                    if not search_for_user_in_channel(user["u_id"], channel):
                        raise AccessError("User not in channel")
                    else:
                        if message != "" and message != None:
                            new_message = mess["message"] + " " + message
                        else:
                            new_message = mess["message"]
                        share_message = message_send_v1(token, channel_id, new_message)
                        return {"shared_message_id": share_message["message_id"]}
  
        raise InputError("Invalid Message Id.")
    
    else:
        direct_message = find_dm(dm_id, store)
        if direct_message == None:
            raise InputError("Invalid dm_id")

        for dm in store["direct_messages"]:
            for mess in dm["messages"]:
                if mess["message_id"] == og_message_id:
                    dm_member = find_member(token, dm, store)
                    if dm_member == None:
                        raise AccessError("User not in dm")
                    else:
                        if message != "" and message != None:
                            new_message = mess["message"] + " " + message
                        else:
                            new_message = mess["message"]
                        share_message = message_senddm_v1(token, dm_id, new_message)
                        return {"shared_message_id": share_message["message_id"]}
                    
        raise InputError("Invalid Message Id.")
    
# <message_react_v1> add "react" to that particular message of a channel or DM
#                    where the authorised user is part of.
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <message_id> (<int>) - the unique message id represent the message
#   <react_id>(<int>) - the unique react id represent the react feature
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - message_id is not a valid message within a channel or DM that the
#                     authorised user has joined
#                   - react_id is not a valid react ID
#                   - the message already contains a react with ID react_id from the authorised user
#
# Return Value:
#   Returns <{}>  <InputError not raised>
def message_react_v1(token, message_id, react_id):
    if react_id != REACT_ID:
        raise InputError("Invalid React Id.")
    
    store = data_store.get()
    
    user = valid_token(store, token)

    if_invalid_access(user)

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if not search_for_user_in_channel(user["u_id"], channel):
                    raise InputError("User not in channel")
                else:
                    react = message["reacts"][0]
                    if user["u_id"] in react["u_ids"]:
                        raise InputError("message contain react from user")
                    else:
                        # Notifications
                        msg_user_id = message["u_id"]
                        for users in store["users"]:
                            if users["auth_user_id"] == msg_user_id:
                                if len(users["notifications"]) == 20:
                                    users["notifications"].pop(19)
                                users["notifications"].insert(0, get_notif_react(user, message_id))

                        react["u_ids"].append(user["u_id"])
                        react["is_this_user_reacted"] = True
                        data_store.set(store)
                        return {}
                                    
    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message["message_id"] == message_id:
                dm_member = find_member(token, dm, store)
                if dm_member == None:
                    raise InputError("User not in dm")
                else:
                    react = message["reacts"][0]
                    if user["u_id"] in react["u_ids"]:
                        raise InputError("message contain react from user")
                    else:
                        # Notifications
                        msg_user_id = message["u_id"]
                        for users in store["users"]:
                            if users["auth_user_id"] == msg_user_id:
                                if len(users["notifications"]) == 20:
                                    users["notifications"].pop(19)
                                users["notifications"].insert(0, get_notif_react(user, message_id))

                        react["u_ids"].append(user["u_id"])
                        react["is_this_user_reacted"] = True
                        data_store.set(store)
                        return {}

    raise InputError("Invalid Message Id.")

# <message_unreact_v1> remove "react" to that particular message of a channel or DM
#                    where the authorised user is part of.
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <message_id> (<int>) - the unique message id represent the message
#   <react_id>(<int>) - the unique react id represent the react feature
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - message_id is not a valid message within a channel or DM that the
#                     authorised user has joined
#                   - react_id is not a valid react ID
#                   - the message does not contain a react with ID react_id from the authorised user
#
# Return Value:
#   Returns <{}>  <InputError not raised>
def message_unreact_v1(token, message_id, react_id):
    if react_id != REACT_ID:
        raise InputError("Invalid React Id.")
    
    store = data_store.get()
    
    user = valid_token(store, token)

    if_invalid_access(user)

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                if not search_for_user_in_channel(user["u_id"], channel):
                    raise InputError("User not in channel")
                else:
                    react = message["reacts"][0]
                    if user["u_id"] not in react["u_ids"]:
                        raise InputError("message doesn't contain react from user")
                    else:
                        react["u_ids"].remove(user["u_id"])
                        react["is_this_user_reacted"] = False
                        data_store.set(store)
                        return {}                        

    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message["message_id"] == message_id:
                dm_member = find_member(token, dm, store)
                if dm_member == None:
                    raise InputError("User not in dm")
                else:
                    react = message["reacts"][0]
                    if user["u_id"] not in react["u_ids"]:
                        raise InputError("message doesn't contain react from user")
                    else:
                        react["u_ids"].remove(user["u_id"])
                        react["is_this_user_reacted"] = False
                        data_store.set(store)
                        return {}
    
    raise InputError("Invalid Message Id.")

def message_pin_v1(token, message_id):
    store = data_store.get()
    
    user = valid_token(store, token)
    if_invalid_access(user)

    channel = search_for_channel_with_message_id(message_id, store)

    dm = search_for_dm_with_message_id(message_id, store)

    if search_for_message(message_id, store) == None:
        raise InputError("Trying to pin a message that doesn't exist")

    if search_for_message(message_id, store)["is_pinned"]:
        raise InputError("Message already pinned")
        

    if channel != None:   
        if not search_for_owner_in_channel(user["u_id"], channel):
            if search_for_user_in_store(user["u_id"], store)["permission_id"] != 1:
                raise AccessError("User does not have permission to pin message in channel")

        search_for_message(message_id, store)['is_pinned'] = True
        data_store.set(store)

        return {}
    
    if dm != None:
        if not dm["owner"][0]["u_id"] == user["u_id"]:
            raise AccessError("User does not have permission to pin message in dm")
        
        search_for_message(message_id, store)['is_pinned'] = True
        data_store.set(store)

        return {}  

def message_unpin_v1(token, message_id):
    store = data_store.get()
    
    user = valid_token(store, token)
    if_invalid_access(user)

    channel = search_for_channel_with_message_id(message_id, store)

    dm = search_for_dm_with_message_id(message_id, store)

    if search_for_message(message_id, store) == None:
        raise InputError("Trying to unpin a message that doesn't exist")

    if not search_for_message(message_id, store)["is_pinned"]:
        raise InputError("Message is not pinned")
        

    if channel != None:   
        if not search_for_owner_in_channel(user["u_id"], channel):
            if search_for_user_in_store(user["u_id"], store)["permission_id"] != 1:
                raise AccessError("User does not have permission to pin message in channel")

        search_for_message(message_id, store)['is_pinned'] = False
        data_store.set(store)

        return {}
    
    if dm != None:
        if not dm["owner"][0]["u_id"] == user["u_id"]:
            raise AccessError("User does not have permission to pin message in dm")
        
        search_for_message(message_id, store)['is_pinned'] = False
        data_store.set(store)

        return {}

# <message_sendlater_v1> Send a message from the authorised user to the channel specified by
#                       channel_id automatically at a specified time in the future.
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <channel_id> (<int>) - the unique channel id represent the channel
#   <message>(<str>) - the message to be send
#   <time_sent>(<int>) - the future unix timestamp to send message
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - channel_id does not refer to a valid channel
#                   - length of message is over 1000 characters
#                   - time_sent is a time in the past
#   AccessError  - Occurs when any of the either:
#                   - channel_id is valid and the authorised user is not a member of
#                     the channel they are trying to post to
#
# Return Value:
#   Returns <{message_id}> as dict on <InputError or AccessError not raised> 
def message_sendlater_v1(token, channel_id, message, time_sent):
    if len(message) > 1000:
        raise InputError("Invalid message")
    
    store = data_store.get()
    
    user = valid_token(store, token)

    if_invalid_access(user)

    channel = search_for_channel(store, channel_id)
    if not search_for_user_in_channel(user["u_id"], channel):
        raise AccessError(description="User not in channel")
    curr_time = int(time.time())
    if time_sent < curr_time:
        raise InputError("Past time given")

    duration = time_sent - curr_time
    thread = threading.Thread(target = message_sleep, args = (duration,))
    thread.start()
    return message_send_v1(token, channel_id, message)
    
# a helper function that act as timer   
def message_sleep(duration):
    time.sleep(duration)

# <message_sendlaterdm_v1> Send a message from the authorised user to the DM specified by
#                       dm_id automatically at a specified time in the future.
#
# Arguments:
#   <token> (<str>) - encoded string of token with user information
#   <dm_id> (<int>) - the unique dm id represent the dm
#   <message>(<str>) - the message to be send
#   <time_sent>(<int>) - the future unix timestamp to send message
# 
# Exceptions:
#   InputError - Occurs when any of the either:
#                   - dm_id does not refer to a valid channel
#                   - length of message is over 1000 characters
#                   - time_sent is a time in the past
#   AccessError  - Occurs when any of the either:
#                   - dm_id is valid and the authorised user is not a member of
#                     the dm they are trying to post to
#
# Return Value:
#   Returns <{message_id}> as dict on <InputError or AccessError not raised> 
def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    if len(message) > 1000:
        raise InputError("Invalid message")
    
    store = data_store.get()
    
    user = valid_token(store, token)

    if_invalid_access(user)

    dm = find_dm(dm_id, store)
    if dm == None:
        raise InputError("Invalid dm_id")

    dm_member = find_member(token, dm, store)
    if dm_member == None:
        raise AccessError("User not in dm")

    curr_time = int(time.time())
    if time_sent < curr_time:
        raise InputError("Past time given")

    duration = time_sent - curr_time
    thread = threading.Thread(target = message_sleep, args = (duration,))
    thread.start()
    return message_senddm_v1(token, dm_id, message)
