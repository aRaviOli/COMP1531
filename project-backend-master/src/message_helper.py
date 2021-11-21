from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import clear_v1
from src.jwt_helpers import decode_jwt

def search_for_message(message_id, store):

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message_id == message["message_id"]:
                return message

    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message_id == message["message_id"]:
                return message

    return None

def search_for_channel_with_message_id(message_id, store):

    for channel in store["channels"]:
        for message in channel["messages"]:
            if message_id == message["message_id"]:
                return channel
    return None

def search_for_dm_with_message_id(message_id, store):

    for dm in store["direct_messages"]:
        for message in dm["messages"]:
            if message_id == message["message_id"]:
                return dm
    return None