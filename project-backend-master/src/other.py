from sys import path
from src.data_store import data_store
from src.jwt_helpers import reset_session_id
import os

def clear_v1():
    store = data_store.get()
    store["users"] = []
    store["channels"] = []
    store["direct_messages"] = []
    store["messages"] = []
    store["user_stats"] = []
    store["workspace_stats"] = {
        "channels_exist": [],
        "dms_exist": [],
        "messages_exist": [],
        "utilization_rate": None
    }
    reset_session_id()

    for file in os.listdir("src/static/"):
        if file != "default.jpg" and file != ".gitkeep":
            file_path = os.path.join("src/static/", file)
            os.unlink(file_path)
    
    data_store.set(store)
    return {}