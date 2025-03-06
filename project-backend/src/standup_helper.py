from datetime import timezone
from src.data_store import data_store
from src.user_helper import existing_messages, involvement_rate, num_messages_sent, update_userspace, update_workspace, utilization_rate
import time

REACT_ID = 1

def stop_standup_and_send_message(u_id, channel_id):
    store = data_store.get()
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            standup_message = '\n'.join(channel["standup"]["stored_standup_strings"])
            if len(standup_message) > 0:    
                message_id = len(store["messages"])
                curr_time = int(time.time())
                message_details = {
                    "message_id" : message_id,
                    "u_id": u_id,
                    "message" : standup_message,
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
                messages_sent = num_messages_sent(store, u_id)
                update_userspace(store, u_id, "messages_sent", "num_messages_sent", messages_sent)
                total_messages = existing_messages(store)
                update_workspace(store, "messages_exist", "num_messages_exist", None, total_messages)
                involvement_rate(store, u_id)
                utilization_rate(store)
                            
            channel["standup"]["stored_standup_strings"] = []
            channel["standup"]["time_finish"] = None
            channel["standup"]["is_active"] = False
            data_store.set(store)

def check_for_active_standup(store, channel_id):
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            if channel["standup"]["is_active"] == True:
                return channel["standup"]
    return None  


    