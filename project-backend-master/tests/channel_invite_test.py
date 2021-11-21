from src import config
from src.error import InputError, AccessError
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, channels_create, channel_invite, channel_details, clear
import pytest

@pytest.fixture
def clear_and_register():
    clear()
    owner = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    return owner

def test_invite_invalid_channel(clear_and_register):
    owner = clear_and_register
    user = auth_register("user@gmail.com", "password", "User", "Email")

    invalid_channel_id = -1

    resp = channel_invite(owner["token"], invalid_channel_id, user["auth_user_id"])["code"]
    assert resp == 400

def test_invite_invalid_user(clear_and_register):
    owner = clear_and_register

    invalid_user_id = -1

    c_id = channels_create(owner["token"], "new_channel", True)["channel_id"]

    resp = channel_invite(owner["token"], c_id, invalid_user_id)["code"]
    assert resp== 400

def test_invite_invalid_auth(clear_and_register):
    owner = clear_and_register
    
    user = auth_register("validemail1@gmail.com", "password", "User", "Email")

    c_id = channels_create(owner["token"], "new_channel", True)["channel_id"]

    invalid_token = create_jwt("invalid@gmail.com", 2)

    resp = channel_invite(invalid_token, c_id, user["auth_user_id"])["code"]
    assert resp == 403


def test_invite_user_already_in_channel(clear_and_register):
    owner = clear_and_register

    auth_register("validemail1@gmail.com", "password", "User", "Email")

    c_id = channels_create(owner["token"], "new_channel", True)["channel_id"]

    resp = channel_invite(owner["token"], c_id, owner["auth_user_id"])["code"]
    assert resp == 400


def test_invite_auth_user_not_in_channel(clear_and_register):
    owner = clear_and_register
    
    user_1 = auth_register("validemail1@gmail.com", "password", "User1", "Email")
    user_2 = auth_register("validemail2@gmail.com", "password", "User2", "Email")
    
    c_id = channels_create(owner["token"], "new_channel", True)["channel_id"]

    resp = channel_invite(user_1["token"], c_id, user_2["auth_user_id"])["code"]
    assert resp == 403

def test_invite_owner_and_member_invite(clear_and_register):
    owner = clear_and_register

    user_1 = auth_register("validemail1@gmail.com", "password", "User1", "Email")
    user_2 = auth_register("validemail2@gmail.com", "password", "User2", "Email")
    
    c_id = channels_create(owner["token"], "new_channel", True)["channel_id"]

    assert channel_invite(owner['token'], c_id, user_1['auth_user_id']) == {}
    assert channel_invite(user_1['token'], c_id, user_2['auth_user_id']) == {}
    assert channel_details(owner["token"], c_id)["all_members"] == [{'email': 'validemail@gmail.com','handle_str': 'validemail','name_first': 'Valid','name_last': 'Email', 'u_id': 0, "profile_img_url": f"{config.url}static/default.jpg"}, {"email": "validemail1@gmail.com", "name_first": "User1", "name_last": "Email", "handle_str": "user1email", "u_id": 1, "profile_img_url": f"{config.url}static/default.jpg"}, {"email": "validemail2@gmail.com", "name_first": "User2", "name_last": "Email", "handle_str": "user2email", "u_id": 2, "profile_img_url": f"{config.url}static/default.jpg"}]