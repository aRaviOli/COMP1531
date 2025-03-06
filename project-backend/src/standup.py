from src.channel_helper import valid_token, search_for_user_in_channel, search_for_channel, if_invalid_access
from src.data_store import data_store
from src.error import InputError, AccessError
from src.standup_helper import stop_standup_and_send_message, check_for_active_standup
import threading
import time

def standup_start_v1(token, channel_id, length):
    store = data_store.get()
    
    if length < 0:
        raise InputError("length is a negative integer")
    
    channel = search_for_channel(store, channel_id)
   
    standup_caller = valid_token(store, token)
    if_invalid_access(standup_caller)
    if (search_for_user_in_channel(standup_caller["u_id"], channel) == False):
        raise AccessError("Authorised user is not a member of the channel.")
    
    # Initially sets the standup status to true for the channel.
    
    for chanl in store["channels"]:
        if chanl["channel_id"] == channel_id:
            if chanl["standup"]["is_active"] == False:
                chanl["standup"]["is_active"] = True
                time_finish_timestamp = time.time() + length
                chanl["standup"]["time_finish"] = time.time() + length
                data_store.set(store)
            else:
                raise InputError("Active standup is currently running in the channel")
    
    # delay sending of messages by length. 
    #t = threading.Timer(float(length), stop_standup_and_send_message(store,token, channel_id))
    t = threading.Timer(float(length), stop_standup_and_send_message,[standup_caller["u_id"], channel_id])
    t.start()
    
    return {"time_finish" : time_finish_timestamp}

def standup_active_v1(token, channel_id):
    store = data_store.get()    
    user = valid_token(store, token)
    if_invalid_access(user)
    channel = search_for_channel(store, channel_id)
   
    if (search_for_user_in_channel(user["u_id"], channel) == False):
        raise AccessError("Authorised user is not a member of the channel.")
        
    standup_dict = check_for_active_standup(store, channel_id)     
        
    if check_for_active_standup(store, channel_id) == None:
        time_finish = None
        is_active = False
    else:
        time_finish = standup_dict["time_finish"]
        is_active = True
        
    return {
        "is_active": is_active,
        "time_finish": time_finish
    }    

def standup_send_v1(token, channel_id, message):
    store = data_store.get()
    channel = search_for_channel(store, channel_id)
    
    user = valid_token(store, token)
    if_invalid_access(user)
    if check_for_active_standup(store, channel_id) == None:
        raise InputError("An active standup is not currently running.")
        
    if (search_for_user_in_channel(user["u_id"], channel) == False):
        raise AccessError("Authorised user is not a member of the channel.")    
        
    # add joined message and user handle to stored standup strings to be sent 
    # later. 
    if len(message) > 1000:
        raise InputError("Length of message is over 1000 characters.")
    
    user_handle = user["handle_str"]
    standup_str = f"{user_handle}: {message}"  
    
    for chanl in store["channels"]:
        if chanl["channel_id"] == channel_id:
            chanl["standup"]["stored_standup_strings"].append(standup_str)
            data_store.set(store) 
            
    return {}    
