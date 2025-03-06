import pytest
import requests
import json
from src import config
from src.jwt_helpers import create_jwt
from tests.server_test_helper import auth_register, auth_login, auth_logout, channels_create, channel_invite, admin_user_remove, admin_userpermission_change, clear
from tests.message_server_test import message_send, message_senddm
from tests.dm_server_test import dm_create

@pytest.fixture
def clear_and_reg_owner():
    clear()
    return auth_register("owneremail@gmail.com", "password", "Global", "Owner")

# admin/user/remove/v1

def test_invalid_u_id_rem(clear_and_reg_owner):
    owner = clear_and_reg_owner
    invalid_u_id = -1

    resp = admin_user_remove(owner["token"], invalid_u_id)["code"]
    assert resp == 400

def test_u_id_only_global_rem(clear_and_reg_owner):
    owner = clear_and_reg_owner
    auth_register("validemail@gmail.com", "password", "Valid", "Email")

    resp = admin_user_remove(owner["token"], owner["auth_user_id"])["code"]
    assert resp == 400

def test_auth_not_global_rem(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail@gmail.com", "password", "Nice", "Try")

    resp = admin_user_remove(member["token"], owner["auth_user_id"])["code"]
    assert resp == 403

def test_invalid_token_rem(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail@gmail.com", "password", "Valid", "Email")

    auth_logout(owner["token"])

    resp = admin_user_remove(owner["token"], member["auth_user_id"])["code"]
    assert resp == 403

def test_two_global_owners(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail@gmail.com", "password", "Griefed", "Lmao")
    
    admin_userpermission_change(owner["token"], member["auth_user_id"], 1)

    assert admin_user_remove(member["token"], owner["auth_user_id"]) == {}
    
def test_remove_many_channels(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    channels_create(member_1["token"], "New channel1", True)
    channel_2_id = channels_create(member_2["token"], "New channel2", True)["channel_id"]
    channel_invite(member_2["token"], channel_2_id, member_1["auth_user_id"])

    message_send(member_1["token"], channel_2_id, "Hello")
    message_send(member_2["token"], channel_2_id, "Hello")

    assert admin_user_remove(owner["token"], member_2["auth_user_id"]) == {}

def test_remove_not_channel_owner(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    channel_id = channels_create(member_1["token"], "New channel", True)["channel_id"]
    channel_invite(member_1["token"], channel_id, member_2["auth_user_id"])

    assert admin_user_remove(owner["token"], member_2["auth_user_id"]) == {}

def test_remove_owner_many_dms(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    dm_create(member_1["token"], [owner["auth_user_id"]])
    dm_2_id = dm_create(member_2["token"], [owner["auth_user_id"]])["dm_id"]

    message_senddm(owner["token"], dm_2_id, "Hello")
    message_senddm(member_2["token"], dm_2_id, "Hello")

    assert admin_user_remove(owner["token"], member_2["auth_user_id"]) == {}

def test_remove(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    channel_id = channels_create(member_2["token"], "New channel", True)["channel_id"]
    channel_invite(member_2["token"], channel_id, member_1["auth_user_id"])

    dm_create(member_1["token"], [owner["auth_user_id"], member_2["auth_user_id"]])

    assert admin_user_remove(owner["token"], member_2["auth_user_id"]) == {}

'''def test_remove_existing_messages_channels(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")

    channel_id = channels_create(member_1["token"], "New channel", True)["channel_id"]
    message_id = message_send(member_1["token"], channel_id, "Hello")["message_id"]

    assert admin_user_remove(owner["token"], member_1["auth_user_id"]) == {}
'''

# admin/userpermission/change/v1

def test_invalid_token_perm(clear_and_reg_owner):
    member = auth_register("validemail@gmail.com", "password", "First", "Last")
    invalid_token = create_jwt("invalidemail@gmail.com", 2)

    resp = admin_userpermission_change(invalid_token, member["auth_user_id"], 1)["code"]
    assert resp == 403

def test_invalid_token_perm_2(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail@gmail.com", "password", "First", "Last")

    auth_logout(owner["token"])

    resp = admin_userpermission_change(owner["token"], member["auth_user_id"], 1)["code"]
    assert resp == 403

def test_invalid_u_id_perm(clear_and_reg_owner):
    owner = clear_and_reg_owner

    invalid_u_id = -1

    resp = admin_userpermission_change(owner["token"], invalid_u_id, 1)["code"]
    assert resp == 400

def test_u_id_only_global_perm(clear_and_reg_owner):
    owner = clear_and_reg_owner
    auth_register("validemail1@gmail.com", "password", "First1", "Last")
    auth_register("validemail2@gmail.com", "password", "First2", "Last")

    resp = admin_userpermission_change(owner["token"], owner["auth_user_id"], 2)["code"]
    assert resp == 400

def test_invalid_perm_id(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail1@gmail.com", "password", "First", "Last")

    resp = admin_userpermission_change(owner["token"], member["auth_user_id"], -1)["code"]
    assert resp == 400

def test_auth_not_global_perm(clear_and_reg_owner):
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    resp = admin_userpermission_change(member_1["token"], member_2["auth_user_id"], 1)["code"]
    assert resp == 403

def test_promote(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member = auth_register("validemail1@gmail.com", "password", "First", "Last")

    assert admin_userpermission_change(owner["token"], member["auth_user_id"], 1) == {}

def test_demote(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First1", "Last")
    member_2 = auth_register("validemail2@gmail.com", "password", "First2", "Last")

    assert admin_userpermission_change(owner["token"], member_1["auth_user_id"], 1) == {}
    assert admin_userpermission_change(member_1["token"], member_2["auth_user_id"], 1) == {}
    assert admin_userpermission_change(member_2["token"], owner["auth_user_id"], 2) == {}


def test_promote_demote_multiple_sessions(clear_and_reg_owner):
    owner = clear_and_reg_owner
    member_1 = auth_register("validemail1@gmail.com", "password", "First", "Last")
    auth_register("validemail2@gmail.com", "password", "New", "Member")

    member_1_new_session = auth_login("validemail1@gmail.com", "password")

    admin_userpermission_change(owner["token"], member_1["auth_user_id"], 1)

    assert admin_userpermission_change(member_1_new_session["token"], owner["auth_user_id"], 2) == {}
