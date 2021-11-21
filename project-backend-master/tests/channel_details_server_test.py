from src import config
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, auth_login, channels_create, clear, channel_details
import json
import pytest

@pytest.fixture
def clear_and_register():
    clear()
    token = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    return token

#-----------------test_channels_create_server----------------#
def test_create_server_invalid_token(clear_and_register):
    invalid_token = create_jwt("invalidemail@gmail.com", 0)
    channel_id = channels_create(clear_and_register["token"], "Invalid token", True)["channel_id"]
    resp = channel_details(invalid_token, channel_id)["code"]
    assert resp == 403

def test_create_server_invalid_channel_id(clear_and_register):
    resp = channel_details(clear_and_register["token"], 1)["code"]
    assert resp == 400

def test_create_details_server_valid(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Valid Channel Name", True)["channel_id"]
    assert channel_details(owner_token, channel_id) == {'all_members': [{'email': 'validemail@gmail.com','handle_str': 'validemail','name_first': 'Valid','name_last': 'Email', 'u_id': 0, "profile_img_url": f"{config.url}static/default.jpg"}], 'is_public': True, 'name': 'Valid Channel Name', 'owner_members': [{'email': 'validemail@gmail.com', 'handle_str': 'validemail', 'name_first': 'Valid', 'name_last': 'Email', 'u_id': 0, "profile_img_url": f"{config.url}static/default.jpg"}]}

def test_details_server_user_not_in_channel(clear_and_register):
    owner_token = clear_and_register["token"]
    user2_token = auth_register("validemail2@gmail.com", "password", "Valid2", "Email2")["token"]
    channel_id = channels_create(owner_token, "Channel 2", True)["channel_id"]
    resp = channel_details(user2_token, channel_id)["code"]
    assert resp == 403