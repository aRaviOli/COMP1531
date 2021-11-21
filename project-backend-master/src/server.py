from flask import Flask, request
from flask_cors import CORS
from json import dumps
from src import config
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.general import search_v1, notifications_get_v1
from src.data_store import data_store
from src.channel import channel_details_v2, channel_invite_v2, channel_join_v2, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1, channel_messages_v2
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.message import message_send_v1, message_remove_v1, message_edit_v1, message_senddm_v1, message_share_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.error import InputError
from src.other import clear_v1
from src.user import user_profile_v1, user_profile_setemail_v1,  user_profile_sethandle_v1, user_profile_setname_v1, user_profile_uploadphoto_v1, user_stats_v1, users_all_v1, users_stats_v1
from src.direct_messages import dm_create_v1, dm_list_v1, dm_details_v1, dm_leave_v1, dm_remove_v1, dm_messages_v1
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1  
import signal
import sys

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route("/admin/user/remove/v1", methods={"DELETE"})
def admin_user_remove():
    data = request.get_json()
    admin_user_remove_v1(data["token"], data["u_id"])
    return dumps({})

@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def admin_userpermission_change():
    data = request.get_json()
    admin_userpermission_change_v1(data["token"], data["u_id"], data["permission_id"])
    return dumps({})

@APP.route("/auth/login/v2", methods=["POST"])
def auth_login():
    data = request.get_json()
    login = auth_login_v2(data["email"], data["password"])
    return dumps(login)

@APP.route("/auth/logout/v1", methods=["POST"])
def auth_logout():
    data = request.get_json()
    logout = auth_logout_v1(data["token"])
    return dumps(logout)

@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def auth_passwordreset_request():
    data = request.get_json()
    passwordreset_request = auth_passwordreset_request_v1(data["email"])
    return dumps(passwordreset_request)

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def auth_passwordreset_reset():
    data = request.get_json()
    passwordreset_reset = auth_passwordreset_reset_v1(data["reset_code"], data["new_password"])
    return dumps(passwordreset_reset)

@APP.route("/auth/register/v2", methods=["POST"])
def auth_register():
    data = request.get_json()
    register = auth_register_v2(data["email"], data["password"], data["name_first"], data["name_last"])
    return dumps(register)

@APP.route("/search/v1", methods=["GET"])
def search():
    token = request.args.get("token")
    query_str = str(request.args.get("query_str"))
    search = search_v1(token, query_str)
    return dumps(search)

@APP.route("/notifications/get/v1", methods=["GET"])
def notifications_get():
    token = request.args.get("token")
    notifications = notifications_get_v1(token)
    return dumps(notifications)

@APP.route("/channel/addowner/v1", methods=["POST"])
def channel_addowner():
    data = request.get_json()
    deets = channel_addowner_v1(data["token"], data["channel_id"], data["u_id"])
    return dumps(deets)

@APP.route("/channel/details/v2", methods=["GET"])
def channel_details():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    deets = channel_details_v2(token, channel_id)
    return dumps(deets)

@APP.route("/channel/invite/v2", methods=["POST"])
def channel_invite():
    data = request.get_json()
    invite = channel_invite_v2(data["token"], data["channel_id"], data["u_id"])
    return dumps(invite)

@APP.route("/channel/join/v2", methods=["POST"])
def channel_join():
    data = request.get_json()
    deets = channel_join_v2(data["token"], data["channel_id"])
    return dumps(deets)

@APP.route("/channel/leave/v1", methods=["POST"])
def channel_leave():
    data = request.get_json()
    deets = channel_leave_v1(data["token"], data["channel_id"])
    return dumps(deets)

@APP.route("/channel/removeowner/v1", methods=["POST"])
def channel_removeowner():
    data = request.get_json()
    deets = channel_removeowner_v1(data["token"], data["channel_id"], data["u_id"])
    return dumps(deets)

@APP.route("/channels/create/v2", methods=["POST"])
def channels_create():
    data = request.get_json()
    channel = channels_create_v2(data["token"], data["name"], data["is_public"])
    return dumps(channel)

@APP.route("/channels/list/v2", methods=['GET'])
def channel_list():
    token = request.args.get("token")
    channel_dict = channels_list_v2(token)
    return dumps(channel_dict)
    
@APP.route("/channels/listall/v2", methods=['GET'])
def channel_listall():
    token = request.args.get("token")
    channel_dict = channels_listall_v2(token)
    return dumps(channel_dict)

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    start = int(request.args.get("start"))
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    messages = channel_messages_v2(token, channel_id, start)
    return dumps(messages)

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    dm_id = dm_create_v1(data["token"], data["u_ids"])
    return dumps(dm_id)

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    detail_dict = dm_details_v1(token, dm_id)
    return dumps(detail_dict)

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data["token"], data["dm_id"])
    return dumps({})

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get("token")
    dms = dm_list_v1(token)
    return dumps(dms)

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
     data = request.get_json()
     dm_remove_v1(data["token"], data["dm_id"])
     return dumps({})

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    start = int(request.args.get("start"))
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    message_dict = dm_messages_v1(token, dm_id, start)
    return dumps(message_dict)

@APP.route("/message/edit/v1", methods=["PUT"])
def message_edit():
    data = request.get_json()
    message_edit_v1(data["token"], data["message_id"], data["message"])
    return dumps({})

@APP.route("/message/react/v1", methods=["POST"])
def message_react():
    data = request.get_json()
    message_react_v1(data["token"], data["message_id"], data["react_id"])
    return dumps({})

@APP.route("/message/remove/v1", methods=["DELETE"])
def message_remove():
    data = request.get_json()
    message_remove_v1(data["token"], data["message_id"])
    return dumps({})

@APP.route("/message/send/v1", methods=["POST"])
def message_send():
    data = request.get_json()
    message_dict = message_send_v1(data["token"], data["channel_id"], data["message"])
    return dumps(message_dict)

@APP.route("/message/senddm/v1", methods=["POST"])
def message_senddm():
    data = request.get_json()
    senddm_message = message_senddm_v1(data["token"], data["dm_id"], data["message"])
    return dumps(senddm_message)

@APP.route("/message/share/v1", methods=["POST"])
def message_share():
    data = request.get_json()
    message_share = message_share_v1(data["token"], data["og_message_id"], data["message"], data["channel_id"], data["dm_id"])
    return dumps(message_share)

@APP.route("/message/unreact/v1", methods=["POST"])
def message_unreact():
    data = request.get_json()
    message_unreact_v1(data["token"], data["message_id"], data["react_id"])
    return dumps({})

@APP.route("/message/pin/v1", methods=["POST"])
def message_pin():
    data = request.get_json()
    message_pin_v1(data["token"], data["message_id"])
    return dumps({})

@APP.route("/message/unpin/v1", methods=["POST"])
def message_unpin():
    data = request.get_json()
    message_unpin_v1(data["token"], data["message_id"])
    return dumps({})

@APP.route("/user/profile/v1", methods=["GET"])
def user_profile():
    token = request.args.get("token")
    u_id = int(request.args.get("u_id"))
    profile = user_profile_v1(token, u_id)
    return dumps(profile)

@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def user_profile_setemail():
    data = request.get_json()
    user_profile_setemail_v1(data["token"], data["email"])
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def user_profile_sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data["token"], data["handle_str"])
    return dumps({})

@APP.route("/user/profile/setname/v1", methods=["PUT"])
def user_profile_setname():
    data = request.get_json()
    user_profile_setname_v1(data["token"], data["name_first"], data["name_last"])
    return dumps({})

@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def user_profile_uploadphoto():
    data = request.get_json()
    user_profile_uploadphoto_v1(data["token"], data["img_url"], data["x_start"], data["y_start"], data["x_end"], data["y_end"])
    return dumps({})

@APP.route("/user/stats/v1", methods=["GET"])
def user_stats():
    token = request.args.get("token")
    stats = user_stats_v1(token)
    return dumps(stats)

@APP.route("/users/all/v1", methods=["GET"])
def users_all():
    token = request.args.get("token")
    users = users_all_v1(token)
    return dumps(users)

@APP.route("/users/stats/v1", methods=["GET"])
def users_stats():
    token = request.args.get("token")
    stats = users_stats_v1(token)
    return dumps(stats)

@APP.route("/standup/start/v1", methods=["POST"])
def standup_start():
    data = request.get_json()
    time_fin_dict = standup_start_v1(data["token"], int(data["channel_id"]), int(data["length"]))
    return dumps(time_fin_dict)

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    standup_info = standup_active_v1(token, channel_id)
    return dumps(standup_info)


@APP.route("/standup/send/v1", methods=["POST"])
def standup_send():
    data = request.get_json()
    standup_send_v1(data["token"], data["channel_id"], data["message"])
    return dumps({})

# @APP.route("/store", methods=["GET"])
# def get_store():
#     return data_store.get()

@APP.route("/message/sendlater/v1", methods=["POST"])
def message_sendlater():
    data = request.get_json()
    message_id = message_sendlater_v1(data["token"], data["channel_id"], data["message"], data["time_sent"])
    return dumps(message_id)

@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def message_sendlaterdm():
    data = request.get_json()
    message_id = message_sendlaterdm_v1(data["token"], data["dm_id"], data["message"], data["time_sent"])
    return dumps(message_id)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
