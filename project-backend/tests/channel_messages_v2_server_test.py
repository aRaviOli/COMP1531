from src import config
from src.error import InputError, AccessError
from tests.message_server_test import message_send, message_react
from tests.server_test_helper import auth_register, clear, channels_create, channel_join
import json
import pytest
import requests
from werkzeug import useragents

def channel_messages(token, channel_id, start):
    return requests.get(config.url + "channel/messages/v2", params={
            "token": token,
            "channel_id": channel_id,
            "start": start,
        }).json()

@pytest.fixture
def register():
    clear()
    token = auth_register("abcd123@gmail.com", "password", "Valid", "Email")["token"]
    return token

def test_channel_messages_empty(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    assert channel_messages(register, channel_id, 0) == {"messages": [], "start": 0, "end": -1}

def test_channel_messages_invalid_channel(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    channel_id = -1
    resp = channel_messages(register, channel_id, 0)["code"]
    assert resp == 400

def test_channel_messages_invalid_user(register):
    invalid_user = auth_register("1234jjjj3@gmail.com", "password", "Valid", "Email")
    channel_id = channels_create(register, "channel", True)["channel_id"]
    resp = channel_messages(invalid_user["token"], channel_id, 0)["code"]
    assert resp == 403
        
def test_channel_messages_start_greater(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    resp = channel_messages(register, channel_id, 50)["code"]
    assert resp == 400
    
def test_channel_messages_not_member(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    new_user_id = auth_register("valid@gmail.com", "password1", "First", "Last")
    resp = channel_messages(new_user_id["token"], channel_id, 0)["code"]
    assert resp == 403

def test_messages_order(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    message_send(register, channel_id, "Hello")
    message_send(register, channel_id, "Hello")
    message_send(register, channel_id, "Hello")
    resp = channel_messages(register, channel_id, 0)
    array = [m['message_id'] for m in resp["messages"]]
    assert array == [2, 1, 0]

def test_messages_more_than_fifty(register):
    channel_id = channels_create(register, "channel", True)["channel_id"]
    for _ in range(51):
        message_send(register, channel_id, "Hello")
    resp = channel_messages(register, channel_id, 0)
    assert resp['end'] == 50    
