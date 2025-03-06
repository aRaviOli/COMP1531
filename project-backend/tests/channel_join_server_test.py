from src import config
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, auth_login, channels_create, clear, channel_details, channel_join
import json
import pytest

@pytest.fixture
def clear_and_register():
    clear()
    token = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    return token

#-----------------test_channels_create_server----------------#
def test_join_server_invalid_token(clear_and_register):
    invalid_token = create_jwt("invalidemail@gmail.com", 0)
    channel_id = channels_create(clear_and_register["token"], "Invalid token", True)["channel_id"]
    resp = channel_join(invalid_token, channel_id)["code"]
    assert resp == 403

def test_join_server_invalid_channel_id(clear_and_register):
    resp = channel_join(clear_and_register["token"], 1)["code"]
    assert resp == 400

def test_join_server_valid(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Valid Channel Name", True)["channel_id"]
    token2 = auth_register("validemail2@gmail.com", "password", "Valid","Email")["token"]
    channel_join(token2, channel_id)
    assert channel_details(owner_token, channel_id) == {'name': 'Valid Channel Name', 'is_public': True, 'owner_members': [{'u_id': 0, 'email': 'validemail@gmail.com', 'name_first': 'Valid', 'name_last': 'Email', 'handle_str': 'validemail', "profile_img_url": f"{config.url}static/default.jpg"}], 'all_members': [{'u_id': 0, 'email': 'validemail@gmail.com', 'name_first': 'Valid', 'name_last': 'Email', 'handle_str': 'validemail', "profile_img_url": f"{config.url}static/default.jpg"}, {'u_id': 1, 'email': 'validemail2@gmail.com', 'name_first': 'Valid', 'name_last': 'Email', 'handle_str': 'validemail0', "profile_img_url": f"{config.url}static/default.jpg"}]}

def test_join_server_not_global_owner(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)["channel_id"]
    token2 = auth_register("validemail2@gmail.com", "password", "Valid","Email")["token"]
    resp = channel_join(token2, channel_id)["code"]
    assert resp == 403

def test_join_server_already_in(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Channel 1", False)["channel_id"]
    assert channel_join(owner_token, channel_id)["code"] == 400
    