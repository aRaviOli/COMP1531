from src import config
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, auth_login, channels_create, clear
import json
import pytest

@pytest.fixture
def clear_and_register():
    clear()
    token = auth_register("validemail@gmail.com", "password", "Valid", "Email")["token"]
    return token

#-----------------test_channels_create_server----------------#
def test_create_server_invalid_token_user(clear_and_register):
    invalid_token = create_jwt(1, 0)
    resp = channels_create(invalid_token, "Invalid token", True)["code"]
    assert resp == 403

def test_create_server_invalid_token_session(clear_and_register):
    invalid_token = create_jwt(0, 1)
    resp = channels_create(invalid_token, "Invalid token", True)["code"]
    assert resp == 403

def test_create_server_token_cannot_be_decoded(clear_and_register):
    invalid_token = "LOL"
    resp = channels_create(invalid_token, "Invalid token", True)["code"]
    assert resp == 403

def test_create_server_invalid_channel_name(clear_and_register):
    owner_token = clear_and_register
    resp = channels_create(owner_token, "Channel name is too long", True)["code"]
    assert resp == 400

def test_create_server_name_too_long(clear_and_register):
    owner_token = clear_and_register
    resp = channels_create(owner_token, "Channel name is too long", "True")["code"]
    assert resp == 400

def test_create_server_invalid_is_public_type(clear_and_register):
    owner_token = clear_and_register
    resp = channels_create(owner_token, "Channel name is too long", 0)["code"]
    assert resp == 400

def test_create_server_valid(clear_and_register):
    owner_token = clear_and_register
    channel_id = channels_create(owner_token, "Valid Channel Name", True)["channel_id"]
    assert channel_id == 0

def test_create_server_empty_space(clear_and_register):
    owner_token = clear_and_register
    channel_id1 = channels_create(owner_token, " ", True)["channel_id"]
    channel_id2 = channels_create(owner_token, "  ", True)["channel_id"]
    assert channel_id1 != channel_id2
    resp = channels_create(owner_token, "", True)["code"]
    assert resp == 400

def test_create_server_duplicate_names(clear_and_register):
    owner_token = clear_and_register
    channel_id1 = channels_create(owner_token, "Valid Channel", True)["channel_id"]
    channel_id2 = channels_create(owner_token, "Valid Channel", True)["channel_id"]
    assert channel_id1 != channel_id2

def test_create_server_multiple_users(clear_and_register):
    user1_token = clear_and_register
    user2_token = auth_register("validemail2@gmail.com", "password", "Valid", "Email")["token"]
    user3_token = auth_register("validemail3@gmail.com", "password", "Valid", "Email")["token"]

    channel_id1 = channels_create(user1_token, "Channel 1", True)["channel_id"]
    channel_id2 = channels_create(user2_token, "Channel 2", True)["channel_id"]
    channel_id3 = channels_create(user3_token, "Channel 3", True)["channel_id"]
    assert channel_id1 == 0
    assert channel_id2 == 1
    assert channel_id3 == 2

def test_create_server_different_tokens(clear_and_register):
    user1_token1 = clear_and_register
    user1_token2 = auth_login("validemail@gmail.com", "password")["token"]
    user2_token = auth_register("validemail2@gmail.com", "password2", "Valid", "Email")["token"]
    assert user1_token1 != user1_token2

    channel_id1 = channels_create(user1_token1, "Channel 1", True)["channel_id"]
    channel_id2 = channels_create(user1_token2, "Channel 2", True)["channel_id"]
    channel_id3 = channels_create(user2_token, "Channel 3", True)["channel_id"]
    assert channel_id1 == 0
    assert channel_id2 == 1
    assert channel_id3 == 2