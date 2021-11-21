from src.data_store import data_store

#   given a reacting_user dict and message_id, returns a dict of 
#   notification:
#   - channel_id: if msg in channel return that ch_id else -1
#   - dm_id: if msg in dm return that dm_id else -1
#   - notif_msg: notification of the react

def get_notif_react(reacting_user, message_id):
    store = data_store.get()

    info = {}

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                info = {
                    "channel_id": channel["channel_id"],
                    "channel_name": channel["channel_name"],
                    "dm_id": -1,
                    "dm_name": None,
                    "u_id": message["u_id"]
                }
    
    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message["message_id"] == message_id:
                info = {
                    "channel_id": -1,
                    "channel_name": None,
                    "dm_id": dm["dm_id"],
                    "dm_name": dm["name"],
                    "u_id": message["u_id"]
                }

    user_handle = reacting_user["handle_str"]

    notif_msg = ""
    if info["dm_id"] == -1:
        ch_name = info["channel_name"]
        notif_msg = f"{user_handle} reacted to your message in {ch_name}"
    else:
        dm_name = info["dm_name"]
        notif_msg = f"{user_handle} reacted to your message in {dm_name}"

    return {
        "channel_id": info["channel_id"],
        "dm_id": info["dm_id"],
        "notification_message": notif_msg
    }

#   given a message, extract and return the handle (if existing)
#   if no handle then will return empty str ""

def get_handle_from_msg(message):
    handle = ""
    is_tag = False
    for char in message:
        if char == "@":
            is_tag = True
            continue
        if is_tag:
            if char.isalnum():
                handle += char
            else:
                break

    return handle

#   given a user dict, a channel dict (can be None), a dm dict
#   (can be None) and a message dict, return a notififcation dict
#   of:
#   - channel_id: if msg in channel return that ch_id else -1
#   - dm_id: if msg in dm return that dm_id else -1
#   - notif_msg: notification of the react

def get_notif_tag(user, channel, dm, message):
    tagging_user_handle = user["handle_str"]
    short_msg = message[0:20]

    if dm == None:
        ch_name = channel["channel_name"]
        notif_msg = f"{tagging_user_handle} tagged you in {ch_name}: {short_msg}"
        return {
            "channel_id": channel["channel_id"],
            "dm_id": -1,
            "notification_message": notif_msg
        }
    else:
        dm_name = dm["name"]
        notif_msg = f"{tagging_user_handle} tagged you in {dm_name}: {short_msg}"
        return {
            "channel_id": -1,
            "dm_id": dm["dm_id"],
            "notification_message": notif_msg
        }
