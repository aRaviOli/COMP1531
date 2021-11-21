import json
import pytest
import requests
from src import config 
from tests.server_test_helper import auth_register, auth_login, clear, channels_create, channel_join
from src.error import AccessError, InputError
from src.jwt_helpers import create_jwt

def channels_list(token):
    return requests.get(config.url + "channels/list/v2", params={
            "token": token,
        }).json()
    
    
    
def channels_listall(token):
    return requests.get(config.url + "channels/listall/v2", params={
            "token": token,
        }).json() 
    
    
@pytest.fixture
def clear_register_and_create_channels():
    clear()
    user0 = auth_register("validemail@gmail.com", "password", "Name1", "LastName1")["token"]
    user1 = auth_register("2ndvalidemail@gmail.com", "2ndpassword", "Name2", "LastName2")["token"]
    user2 = auth_register("3rdvalidemail@gmail.com", "3rdpassword", "Name3", "LastName3")["token"]
    user3 = auth_register("4thvalidemail@gmail.com", "4thpassword", "Name4", "LastName4")["token"]
    
    channel0_id = channels_create(user0, "Valid_channel_name", True)["channel_id"]   #ch id 0
    channel1_id = channels_create(user0, "Valid_channel_name2", True)["channel_id"] 
    channel2_id = channels_create(user0, "Valid_channel_name3", False)["channel_id"] 
    
    channel3_id = channels_create(user1, "Valid_channel_name4", False)["channel_id"] 
    channel4_id = channels_create(user2, "Valid_channel_name5", True)["channel_id"]  # ch id 4

    test_list = [user0, user1, user2, user3, channel0_id, channel1_id, channel2_id, channel3_id, channel4_id]
    return test_list


def test_users_in_same_channels(clear_register_and_create_channels):
    # user3 who is in no channels joins a channel with user2
    test_list = clear_register_and_create_channels
    channel_join(test_list[3], test_list[8])
    assert channels_list(test_list[3]) == channels_list(test_list[2])
    

def test_private_channels(clear_register_and_create_channels):
    test_list = clear_register_and_create_channels
    assert channels_list(test_list[1]) == {"channels" : []} 
    
def test_channels_list_invalid_user_id(clear_register_and_create_channels):
    invalid_token = create_jwt("invalidemail@gmail.com", 0)
    resp = channels_list(invalid_token)["code"]
    assert resp == 403
    
def test_listall_invalid_user_id(clear_register_and_create_channels):
    invalid_token = create_jwt("invalidemail@gmail.com", 0)
    resp = channels_listall(invalid_token)["code"]
    assert resp == 403

def test_listall_valid(clear_register_and_create_channels):
    test_list = clear_register_and_create_channels
    assert channels_listall(test_list[0]) == {"channels": [{"channel_id": test_list[4], "name": "Valid_channel_name"}, {"channel_id": test_list[5], "name": "Valid_channel_name2"}, {"channel_id": test_list[6], "name": "Valid_channel_name3"}, {"channel_id": test_list[7], "name": "Valid_channel_name4"}, {"channel_id": test_list[8], "name": "Valid_channel_name5"}]}

def test_private_channel_not_added(clear_register_and_create_channels):
     test_list = clear_register_and_create_channels
     channel_join(test_list[3], test_list[4])
     channel_join(test_list[3], test_list[5])
     channel_join(test_list[3], test_list[8])
     channels_create(test_list[3], "Valid_channel_name6", False)
     assert len(channels_list(test_list[3])["channels"]) == 3   

    
    
    
    