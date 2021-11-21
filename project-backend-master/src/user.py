from os import PRIO_PGRP
from flask import url_for
from PIL import Image
from src.auth_helper import email_check, handle, length_check
from src.channel_helper import valid_token, if_invalid_access
from src.data_store import data_store
from src.error import AccessError, InputError
from src.jwt_helpers import decode_jwt
from src.user_helper import cropping, user_set
from urllib.error import HTTPError
from urllib.request import urlretrieve
import datetime

#   Returns the user_profile of the u_id
#
#   Args:
#       - token <str>: The token of the user looking
#           for the u_id 
#       - u_id <int>: The u_id being searched for
#
#   Returns:
#       - user <dict>: Basic details of the user, not
#           not including the password
#       - AccessError <error>: If the user calling the
#           function does not exist in database or the
#           token is invalid
#       - InputError <error>: If the u_id doesn't exist
#           in the database
def user_profile_v1(token, u_id):
    store = data_store.get()
    auth_user = valid_token(store, token)
    if_invalid_access(auth_user)
    profile = {}

    for user in store["users"]:
        if u_id == user["auth_user_id"]:
            profile = {
                "u_id": user["auth_user_id"],
                "email": user["email"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "profile_img_url": user["profile_img_url"]
            }
    
    if profile == {}:
        raise InputError(description="The user you are looking for doesn't exist")
    
    return {
        "user": profile
    }

#   Changes the user's email then stores it
#
#   Args:
#       - token <str>: The token of the user that wants to
#           change their names
#       - email <str>: The email to be changed into
#
#   Errors:
#       - AccessError: token is invalid
#       - InputError: email is invalid or taken
def user_profile_setemail_v1(token, email):
    store = data_store.get()
    user = valid_token(store, token)
    
    if_invalid_access(user)

    if not email_check(email):
        raise InputError(description="Email is of invalid format.")
    
    for users in store["users"]:
        if users["email"] == email:
            raise InputError(description="Email is already taken.")

    store["users"][user["u_id"]]["email"] = email
    
    user_set(store, "channels", "all_members", user, None, email, "email")
    user_set(store, "channels", "owner_members", user, None, email, "email")
    user_set(store, "direct_messages", "owner", user, None, email, "email")
    user_set(store, "direct_messages", "all_members", user, None, email, "email")
    data_store.set(store)

    return {} 

#   Changes the user's email then stores it
#
#   Args:
#       - token <str>: The token of the user that wants to
#           change their names
#       - handle_str <str>: The email to be changed into
#
#   Errors:
#       - AccessError: token is invalid
#       - InputError: handle_str is invalid
def user_profile_sethandle_v1(token, handle_str):
    store = data_store.get()
    user = valid_token(store, token)
    
    if_invalid_access(user)
    
    if not handle_str.isalnum() or len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Handle is not of alphanumeric format")
    
    for users in store["users"]:
        if users["handle_str"] == handle_str:
            raise InputError(description="Handle is already taken")

    store["users"][user["u_id"]]["handle_str"] = handle_str
    
    user_set(store, "channels", "all_members", user, None, handle_str, "handle_str")
    user_set(store, "channels", "owner_members", user, None, handle_str, "handle_str")
    user_set(store, "direct_messages", "owner", user, None, handle_str, "handle_str")
    user_set(store, "direct_messages", "all_members", user, None, handle_str, "handle_str")
    data_store.set(store)

    return {} 

#   Changes the user's first and last name then stores it
#
#   Args:
#       - token <str>: The token of the user that wants to
#           change their names
#       - name_first <str>: The first name to be changed into
#       - name_last <str>: The last name to be changed into
#
#   Errors:
#       - AccessError: token is invalid
#       - InputError: name_first or name_last is invalid
def user_profile_setname_v1(token, name_first, name_last):
    store = data_store.get()
    user = valid_token(store, token)
    
    if_invalid_access(user)

    length_check(store["users"][user["u_id"]]["password"], name_first, name_last)

    store["users"][user["u_id"]]["name_first"] = name_first
    store["users"][user["u_id"]]["name_last"] = name_last
    
    input = {
        "name_first": name_first,
        "name_last": name_last
    }

    user_set(store, "channels", "all_members", user, "setname", input, None)
    user_set(store, "channels", "owner_members", user, "setname", input, None)
    user_set(store, "direct_messages", "owner", user, "setname", input, None)
    user_set(store, "direct_messages", "all_members", user, "setname", input, None)
    data_store.set(store)

    return {}

#   Checks if the token is valid by checking auth_user_id
#   and sesion_id after decoding and then uploads the photo
#
#   Args:
#       - token <str>: The token of the user uploading photo
#       - img_url <str>: The url of the img
#       - x_start <str>: The start distance from the top left position
#                       in the x-axis
#       - y_start <str>: The start distance from the top left position
#                       in the y-axis
#       - x_end <str>: The end distance from the top left position
#                       in the x-axis
#       - y_end <str>: The end distance from the top left position
#                       in the y-axis
#   Errors:
#       - AccessError: token is invalid
#       - InputError: img_url returns HTTP status other than 200
#                   or image is not JPG,
#                   x_start, y_start, x_end, y_end outside dimesions,
#                   x_end or y_end is less than x_start or y_start
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()
    user = valid_token(store, token)

    if_invalid_access(user)
    # if img_url[0:5] == "https":
    #     raise InputError(description="Url must be non-HTTPS")
    try:
        urlretrieve(img_url, f"src/static/{user['u_id']}.jpg")
    except HTTPError as error:
        raise InputError(description="Url is invalid") from error
    
    profile_image = Image.open(f"src/static/{user['u_id']}.jpg")
    
    if profile_image.format != "JPEG":
        raise InputError(description="The image link is not of JPG or JPEG format") 

    width, height = profile_image.size
    cropping(profile_image, x_start, y_start, x_end, y_end, width, height).save(f"src/static/{user['u_id']}.jpg")

    profile_img_url = url_for("static", filename=f"{user['u_id']}.jpg", _external=True)

    store["users"][user["u_id"]]["profile_img_url"] = profile_img_url
    user_set(store, "channels", "all_members", user, None, profile_img_url, "profile_img_url")
    user_set(store, "channels", "owner_members", user, None, profile_img_url, "profile_img_url")
    user_set(store, "direct_messages", "owner", user, None, profile_img_url, "profile_img_url")
    user_set(store, "direct_messages", "all_members", user, None, profile_img_url, "profile_img_url")
    data_store.set(store)
    
    return {}

#   Shows the statistics of the user's usage during the runtime
#
#   Args:
#       - token <str>: The authorised user 
#
#   Returns:
#       - user_stats <dict>: the statistics of the user
#       - AccessError <error>: If the token calling the
#           function does not exist in database or the
#           token is invalid
def user_stats_v1(token):
    store = data_store.get()
    auth_user = valid_token(store, token)

    if_invalid_access(auth_user)

    return {
        "user_stats": store["user_stats"][auth_user["u_id"]]
    }

#   Checks if the token is valid by checking email and
#   sesion_id after decoding
#
#   Args:
#       - token <str>: The authorised user 
#
#   Returns:
#       - users <list>: List of all user_profile <dict>
#       - AccessError <error>: If the user calling the
#           function does not exist in database or the
#           token is invalid
def users_all_v1(token):
    store = data_store.get()
    auth_user = valid_token(store, token)
    
    if_invalid_access(auth_user)

    users = []
    
    for user in store["users"]:
        if user["email"] != None:
            profile = {
                "u_id": user["auth_user_id"],
                "email": user["email"],
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle_str"],
                "profile_img_url": user["profile_img_url"]
            }
            users.append(profile)
    return {
        "users": users
    }

#   Shows the statistics of every usage during the runtime
#
#   Args:
#       - token <str>: The authorised user 
#
#   Returns:
#       - workspace_stats <dict>: the statistics of Streams
#       - AccessError <error>: If the token calling the
#           function does not exist in database or the
#           token is invalid
def users_stats_v1(token):
    store = data_store.get()
    auth_user = valid_token(store, token)

    if_invalid_access(auth_user)
    
    return {
        "workspace_stats": store["workspace_stats"]
    }