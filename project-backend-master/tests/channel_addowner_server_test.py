from src import config
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, auth_login, channel_addowner, channel_details, channel_invite, channel_join, channel_leave, channels_create, clear
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
    user2 = auth_register("validemail2@gmail.com", "password", "Valid", "Email")
    channel_join(user2["token"], channel_id)
    resp = channel_addowner(invalid_token, channel_id, user2["auth_user_id"])["code"]
    assert resp == 403

def test_create_server_invalid_channel_id(clear_and_register):
    owner_token = clear_and_register["token"]
    user2 = auth_register("validemail2@gmail.com", "password", "Valid", "Email")
    channel_join(user2["token"], 1)
    resp = channel_addowner(owner_token, 101, user2["auth_user_id"])["code"]
    assert resp == 400

def test_addowner_server_u_id_does_not_exist(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "name", True)["channel_id"]
    resp = channel_addowner(owner_token, channel_id, 1)["code"]
    assert resp == 400

def test_addowner_server_token_not_member(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Channel 1", True)["channel_id"]
    user2 = auth_register("validemail2@gmail.com", "password", "first", "last")  
    user3 = auth_register("validemail3@gmail.com", "password", "first", "last")
    channel_invite(owner_token, channel_id, user3["auth_user_id"]) 
    resp = channel_addowner(user2["token"], channel_id, user3["auth_user_id"])["code"]
    assert resp == 400

def test_addowner_server_u_id_not_in_channel(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "name", True)["channel_id"]
    user2 = auth_register("email@gmail.com", "password", "first", "last")
    resp = channel_addowner(owner_token, channel_id, user2["auth_user_id"])["code"]
    assert resp == 400

def test_addowner_server_u_id_already_owner(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "name", True)["channel_id"]
    resp = channel_addowner(owner_token, channel_id, clear_and_register["auth_user_id"])["code"]
    assert resp == 400

def test_addowner_server_u_id_addowner_twice(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "name", True)["channel_id"]
    user2 = auth_register("email@gmail.com", "password", "first", "last")
    channel_join(user2["token"], channel_id)
    channel_addowner(owner_token, channel_id, user2["auth_user_id"])
    resp = channel_addowner(owner_token, channel_id, user2["auth_user_id"])["code"]
    assert resp == 400

def test_addowner_server_token_not_global_owner(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "name", True)["channel_id"]
    user2 = auth_register("validemail2@gmail.com", "password", "first", "last")
    user3 = auth_register("validemail3@gmail.com", "password", "Valid", "Email")
    channel_invite(owner_token, channel_id, user2["auth_user_id"])
    channel_join(user3["token"], channel_id)
    resp = channel_addowner(user2["token"], channel_id, user3["auth_user_id"])["code"]
    assert resp == 403

def test_create_join_server_valid(clear_and_register):
    owner_token = clear_and_register["token"]
    channel_id = channels_create(owner_token, "Valid Channel Name", True)["channel_id"]
    id2 = auth_register("validemail2@gmail.com", "password", "Valid","Email")
    channel_join(id2["token"], channel_id)
    channel_leave(id2["token"], channel_id)
    channel_addowner(owner_token, channel_id, id2["auth_user_id"])

def test_addowner_server_token_not_owner_but_global(clear_and_register):
    owner_token = clear_and_register["token"]
    owner_u_id = clear_and_register["auth_user_id"]
    user2 = auth_register("validemail2@gmail.com", "password", "Valid","Email")
    channel_id = channels_create(user2["token"], "Valid Channel Name", True)["channel_id"]
    channel_invite(user2["token"], channel_id, owner_u_id)
    channel_addowner(owner_token, channel_id, owner_u_id)
    