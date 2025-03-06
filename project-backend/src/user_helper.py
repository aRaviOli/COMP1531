from datetime import date, datetime
from email import message
from src.error import InputError

#   Function that crops the photo
def cropping(image, x1, y1, x2, y2, width, height):
    if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
        raise InputError(description="Start and end cannot exceed original dimensions")
    elif x2 < x1 or y2 < y1:
        raise InputError(description="End cannot be smaller than start")
    cropped = image.crop((x1, y1, x2, y2))
    return cropped

#   Updates the Streams message
def existing_messages(store):
    messages_exist = 0
    for channel in store["channels"]:
        messages_exist += len(channel["messages"])
    for dms in store["direct_messages"]:
        messages_exist += len(dms["messages"])
    return messages_exist

#   Updates the user's involvement rate on Streams
def involvement_rate(store, u_id):
    numerator = sum([search_for_user(store, "channels", "all_members", u_id), search_for_user(store, "direct_messages", "all_members", u_id), num_messages_sent(store, u_id)])
    denominator = sum([len(store["channels"]), len(store["direct_messages"]), existing_messages(store)])
    if denominator == 0:
        return 0
    rate = float(numerator/ denominator)
    if rate > 1:
        rate = 1
    store["user_stats"][u_id]["involvement_rate"] = rate

#   Counts the number of messages the user has sent
def num_messages_sent(store, u_id):
    msgs_sent = 0
    for message in store["messages"]:
        if message["u_id"] == u_id:
            msgs_sent += 1
    return msgs_sent

#   Searches for the user in the store types
def search_for_user(store, type, store_type, u_id):
    joined = 0
    for data in store[type]:
        for items in data[store_type]:
            if u_id == items["u_id"]:
                joined += 1
    return joined

#   Updates the user's usage everytime user leaves or joins channels, joins
#   or leaves dms, sends or deletes messages
def update_userspace(store, u_id, type, number, num_joined):
    store["user_stats"][u_id][type].append({number: num_joined, "time_stamp": int(datetime.now().timestamp())})

#   Updates the Streams usage statistics every time channels are created, dms 
def update_workspace(store, type, number, store_type=None, messages=None):
    if messages == None:
        item = len(store[store_type])
    else:
        item = messages
    store["workspace_stats"][type].append({number: item, "time_stamp": int(datetime.now().timestamp())})

# Function to set the chosen type
def user_set(store, store_type, member_type, user, func, input, type):
    for item in store[store_type]:
        for members in item[member_type]:
            if members["u_id"] == user["u_id"]:
                if func == "setname":
                    members["name_first"] = input["name_first"]
                    members["name_last"] = input["name_last"]
                else:
                    members[type] = input

#   Updates the utilization rate of Streams
def utilization_rate(store):
    user_in = []
    num_user = 0

    for u_id in range(len(store["users"])):
        for channel in store["channels"]:
            for member in channel["all_members"]:
                if u_id == member["u_id"] and u_id not in user_in:
                    user_in.append(u_id)
        for dm in store["direct_messages"]:
            for member in dm["all_members"]:
                if u_id == member["u_id"] and u_id not in user_in:
                    user_in.append(u_id)
        if store["users"][u_id]["email"] != None:
            num_user += 1
    store["workspace_stats"]["utilization_rate"] = float(len(user_in) / num_user)
