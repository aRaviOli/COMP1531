from src.data_store import data_store
from src.error import InputError

from src.channel_helper import valid_token, if_invalid_access
from src.admin_helper import get_user

#   given a query str, return a collection of messages in all existing ch/dm
#   that the user is part of that contain the str
#
#   notes - currently case-sensitive
#
#   Args:
#       - token <str>: the token of the user
#       - query_str <str>: the str that user is searching for
#
#   Exceptions:
#       AccessError: when given token is invalid
#       InputError: when len of query_str is less than 1 or more than 1000
#
#   Returns:
#       messages - a list of dictionaries { message_id, u_id, message, 
#                  time_created, reacts, is_pinned}

def search_v1(token, query_str):
    store = data_store.get()

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description="Invalid length of query")

    # will raise AccessError upon invalid token
    user = valid_token(store, token)
    if_invalid_access(user)

    # list of dicts {message_id, u_id, message, time_create, reacts, is_pinned}
    messages = []

    for channel in store["channels"]:
        if user in channel["all_members"]:
            for message in channel["messages"]:
                if query_str in message["message"]:
                    messages.append(message)

    for dm in store["direct_messages"]:
        if user in dm["all_members"]:
            for message in dm["messages"]:
                if query_str in message["message"]:
                    messages.append(message)

    return {"messages": messages}

#   returns the given user's most recent 20 notifications
#   ordered from most to least recent
#
#   Args:
#       - token <str>: token of the user
#
#   Exceptions:
#       AccessError - when token is invalid
#
#   Returns:
#       - notifications: a list of dictionaries which contain
#         types {channel_id, dm_id, notification_message}

def notifications_get_v1(token):
    # if token invalid, AccessError will be raised
    user = get_user(token)

    return {"notifications": user["notifications"]}
