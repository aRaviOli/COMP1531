from src.admin_helper import get_user, search_for_user_in_dm, get_channel_member, get_dm_member
from src.channel_helper import search_for_user_in_store, search_for_user_in_channel
from src.data_store import data_store
from src.error import InputError, AccessError
from src.jwt_helpers import decode_jwt
from src.user_helper import utilization_rate

#   <allows a global owner to remove another user from Streams>
#
#   Args:
#       - token <str>: the token of the authorised user
#       - u_id <int>: the u_id of the user being removed
#
#   Exceptions:
#       InputError:
#           - u_id does not correspond to a valid user
#           - u_id corresponds to a user who is the only global owner
#       AccessError:
#           - token does not correspond to a valid user
#           - token does not correspond to a global owner
#
#   Returns:
#       - empty

def admin_user_remove_v1(token, u_id):
    store = data_store.get()
    auth_user = get_user(token)

    rem_user = {}
    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            rem_user = user
    
    # u_id not valid
    if rem_user == {}:
        raise InputError(description="The user_id is not a valid user")

    # token not global owner    
    if not auth_user["permission_id"] == 1:
        raise AccessError(description="The authorised user is not a global owner")

    # u_id only global owner
    if rem_user["permission_id"] == 1:
        global_owners = 0
        for user in store["users"]:
            if user["permission_id"] == 1:
                global_owners += 1
        if global_owners == 1:
            raise InputError(description="The user you want to remove is the only global owner")

    # removing from all channels & dms

    for channel in store["channels"]:
        if search_for_user_in_channel(u_id, channel):
            channel_member = get_channel_member(u_id, channel)
            if channel_member in channel["owner_members"]:
                channel["owner_members"].remove(channel_member)
            channel["all_members"].remove(channel_member)

    for dm in store["direct_messages"]:
        if search_for_user_in_dm(u_id, dm):
            dm_member = get_dm_member(u_id, dm)
            if dm_member == dm["owner"][0]:
                dm["owner"][0] = [{}]
            dm["all_members"].remove(dm_member)

    # changing all message contents of removed user to "Removed user"
    for channel in store["channels"]:
        for message_details in channel["messages"]:
            if message_details["u_id"] == u_id:
                message_details["message"] = "Removed user"

    for dm in store["direct_messages"]:
        for message_details in dm["messages"]:
            if message_details["u_id"] == u_id:
                message_details["message"] = "Removed user"
    
    for message in store["messages"]:
        if message["u_id"] == u_id:
            message["message"] = "Removed user"

    # modifying their user_info
    rem_user["email"] = None
    rem_user["name_first"] = "Removed"
    rem_user["name_last"] = "user"
    rem_user["handle_str"] = None
    rem_user["password"] = None
    rem_user["sessions"] = []
    rem_user["permission_id"] = None
    rem_user["reset_code"] = None
    rem_user["profile_img_url"] = None
    rem_user["notifications"] = None

    utilization_rate(store)

    data_store.set(store)

    return {}

#   <allows a global owner to change the permission of another user of
#   Streams>
#
#   Args:
#       - token <str>: the token of the authorised user
#       - u_id <int>: the u_id of the user whose perms are being changes
#       - permission_id <int>: what type of permission is being granted
#
#   Exceptions:
#       InputError:
#           - u_id does not correspond to a valid user
#           - u_id corresponds to the only global owner and is being
#             demoted to a member
#           - permission_id is an invalid number
#       AccessError:
#           - token does not correspond to a valid user
#           - token does not correspond to a global owner
#
#   Returns:
#       - empty

def admin_userpermission_change_v1(token, u_id, permission_id):
    store = data_store.get()
    auth_user = get_user(token)

    # u_id not valid
    perms_change_user = {}
    for user in store["users"]:
        if user["auth_user_id"] == u_id:
            perms_change_user = user
    
    if perms_change_user == {}:
        raise InputError(description="The user_id is not a valid user")

    # token not global owner    
    if not auth_user["permission_id"] == 1:
        raise AccessError(description="The authorised user is not a global owner")

    # u_id only global owner
    if permission_id == 2 and perms_change_user["permission_id"] == 1:
        global_owners = 0
        for user in store["users"]:
            if user["permission_id"] == 1:
                global_owners += 1
        if global_owners == 1:
            raise InputError(description="The authorised user is the only global owner")

    # permission_id invalid
    if not permission_id in [1, 2]:
        raise InputError(description="The permission_id is not valid")

    perms_change_user["permission_id"] = permission_id
    data_store.set(store)

    return {}
