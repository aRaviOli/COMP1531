import json
import pytest
import requests
from src import config 
from tests.server_test_helper import auth_register, clear
from tests.message_server_test import message_senddm
from src.error import AccessError, InputError

# Helper functions to make requests.

def dm_create(token, u_ids):
    return requests.post(config.url + "dm/create/v1", json={
            "token": token,
            "u_ids": u_ids,
        }).json()
    


def dm_list(token):
    return requests.get(config.url + "dm/list/v1", params={
            "token": token,
        }).json()
    
    
    
def dm_remove(token, dm_id):
    return requests.delete(config.url + "dm/remove/v1", json={
            "token": token,
            "dm_id": dm_id,
        }).json()


def dm_details(token, dm_id):
    return requests.get(config.url + "dm/details/v1", params={
            "token": token,
            "dm_id": dm_id,
        }).json()
    
    
def dm_leave(token, dm_id):
    return requests.post(config.url + "dm/leave/v1", json={
            "token": token,
            "dm_id": dm_id,
        }).json()

def dm_messages(token, dm_id, start):
    return requests.get(config.url + "dm/messages/v1", params={
            "token": token,
            "dm_id": dm_id,
            "start": start
        }).json()
    
    
@pytest.fixture
def clear_and_register():
    clear()
    token = auth_register("validemail@gmail.com", "password", "aFirst", "Last1")["token"]
    return token
  
def test_send_to_invalid_user(clear_and_register):
    owner_token = clear_and_register
    resp = dm_create(owner_token, [3])["code"]
    assert resp == 400


def test_send_to_invalid_users(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")
    auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")
    resp = dm_create(owner_token, [1, 2, 3, 7])["code"]
    assert resp == 400
        
      
def test_invalid_dm_create_owner_in_u_id_list(clear_and_register):
     owner_token = clear_and_register
     auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")
     resp = dm_create(owner_token, [0,1])["code"]
     assert resp == 400 
    
def multiple_dms(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")
    assert dm_create(owner_token, [1,2])["dm_id"] == 0
    assert dm_create(owner_token, [1])["dm_id"] == 1
    
    
def test_dm_between_2_users(clear_and_register):
     owner_token = clear_and_register
     member_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
     dm_create(owner_token, [1])
     dms_dict_owner = dm_list(owner_token)
     dms_dict_member = dm_list(member_token)
     
     assert dms_dict_member == dms_dict_owner
     assert dms_dict_member["dms"][0] == {"dm_id": 0, "name": "afirstlast1, bfirstlast2"}
     
     
def test_dm_between_3_users(clear_and_register):     
    owner_token = clear_and_register
    member1_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    member2_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_create(owner_token, [1])
    dm_create(owner_token, [1,2])     
    dms_dict_owner = dm_list(owner_token)
    dms_dict_member1 = dm_list(member1_token)
    dms_dict_member2 = dm_list(member2_token)
    
    # both the owner of the dms and member 1 are in the same dms. 
    assert dms_dict_member1 == dms_dict_owner 
    assert dms_dict_member1 != dms_dict_member2
    
    assert dms_dict_owner["dms"][0]["dm_id"] == 0
    assert dms_dict_owner["dms"][1]["dm_id"] == 1  
    assert dms_dict_owner["dms"][0]["name"] == "afirstlast1, bfirstlast2"  
    assert dms_dict_owner["dms"][1]["name"] == "afirstlast1, bfirstlast2, cfirstlast3"
    
    assert dms_dict_member2["dms"][0]["dm_id"] == 1
    assert dms_dict_member2["dms"][0]["name"] ==  dms_dict_owner["dms"][1]["name"]
    

def test_not_in_any_dm(clear_and_register):
    user_token = clear_and_register
    assert dm_list(user_token)["dms"] == []
    
    
def test_non_owner_attempted_removal(clear_and_register):
    owner_token = clear_and_register
    member1_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_create(owner_token, [1,2])
    resp = dm_remove(member1_token, 0)["code"]
    assert resp == 403
    
        
def test_multiple_owners_attempted_removal_of_unowned_dm(clear_and_register):
    owner_chat_1 = clear_and_register
    owner_chat_2 = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]        
    dm_create(owner_chat_1, [1])
    dm_create(owner_chat_2, [0]) 
    
    # owner of a chat tries to remove the chat they do not own. 
    resp = dm_remove(owner_chat_2, 0)["code"]
    assert resp == 403
    
def test_invalid_dm_id(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_create(owner_token, [1,2])  
    resp = dm_remove(owner_token, 1)["code"]
    assert resp == 400
        
def test_basic_removal(clear_and_register): 
    owner_token = clear_and_register
    member1_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    member2_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_create(owner_token, [1,2])  
    
    assert dm_list(owner_token)["dms"] != []
    assert dm_list(member1_token)["dms"] != []   
    assert dm_list(member2_token)["dms"] != []
    dm_remove(owner_token, 0)
    assert dm_list(owner_token)["dms"] == []
    assert dm_list(member1_token)["dms"] == []   
    assert dm_list(member2_token)["dms"] == []    
    
            
def test_dm_remove_middle_dm(clear_and_register):
    owner_chat_1 = clear_and_register
    owner_chat_2 = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"] 
    member1_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    member2_token = auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")["token"]
    
    dm_create(owner_chat_1, [1, 3])
    dm_create(owner_chat_1, [1, 2])
    dm_create(owner_chat_2, [0, 2, 3]) 
    dm_create(owner_chat_2, [3]) 
    
    
    dm_dict_member1 = dm_list(member1_token) 
    dm_dict_member2 = dm_list(member2_token)
    
    assert dm_dict_member1["dms"] == [{"dm_id": 1, "name": "afirstlast1, bfirstlast2, cfirstlast3"}, {"dm_id": 2, "name": "afirstlast1, bfirstlast2, cfirstlast3, dfirstlast4"}]
    
    assert dm_dict_member2["dms"][0] == {"dm_id": 0, "name": "afirstlast1, bfirstlast2, dfirstlast4"}
    assert dm_dict_member2["dms"][1] == {"dm_id": 2, "name": "afirstlast1, bfirstlast2, cfirstlast3, dfirstlast4"}
    assert dm_dict_member2["dms"][2] == {"dm_id": 3, "name": "bfirstlast2, dfirstlast4"}
    
    dm_remove(owner_chat_2, 2)
    dm_dict_member1 = dm_list(member1_token) 
    assert dm_dict_member1["dms"] == [{"dm_id": 1, "name": "afirstlast1, bfirstlast2, cfirstlast3"}]
    
    dm_remove(owner_chat_1, 1)
    dm_dict_member1 = dm_list(member1_token) 
    assert dm_dict_member1["dms"] == []
    
    dm_dict_member2 = dm_list(member2_token)
    assert dm_dict_member2["dms"][1] == {"dm_id": 3, "name": "bfirstlast2, dfirstlast4"}
    
    
def test_provide_details(clear_and_register):
    owner_chat_1 = clear_and_register
    owner_chat_2 = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"] 
    member1_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")["token"]
    
    dm_create(owner_chat_1, [1, 3])
    dm_create(owner_chat_1, [1, 2])
    dm_create(owner_chat_2, [0, 2, 3]) 
    dm_create(owner_chat_2, [3]) 
        
    # both members of dm 1. 
    assert dm_details(member1_token, 1) == dm_details(owner_chat_2, 1)
    print(dm_details(member1_token, 1))     
    assert dm_details(owner_chat_2, 1)["members"][0]["email"] == "validemail@gmail.com" 
    assert dm_details(owner_chat_2, 1)["members"][1]["email"] == "validemail2@gmail.com" 
    assert dm_details(owner_chat_2, 1)["members"][2]["email"] == "validemail3@gmail.com" 
    
    assert dm_details(owner_chat_2, 1)["members"][0]["u_id"] == 0 
    assert dm_details(owner_chat_2, 1)["members"][1]["u_id"] == 1
    assert dm_details(owner_chat_2, 1)["members"][2]["u_id"] == 2
    
    dm_remove(owner_chat_1, 1)
    
    resp = dm_details(owner_chat_2, 1)["code"]
    # chat should not exist anymore. 
    assert resp == 400
        
        
def test_user_not_part_of_dm(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]   
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    non_member_token = auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")["token"]
    dm_create(owner_token, [1,2])
    
    resp = dm_details(non_member_token, 0)["code"]
    assert resp == 403
        
        
def test_dm_leave_non_member(clear_and_register):
    owner_chat_1 = clear_and_register
    owner_chat_2 = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"] 
    member1_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")["token"]
    
    dm_create(owner_chat_1, [1, 3])
    dm_create(owner_chat_1, [1, 2])
    dm_create(owner_chat_2, [0, 2, 3]) 
    dm_create(owner_chat_2, [3]) 
    
    resp = dm_leave(member1_token, 3)["code"]
    assert resp == 403
    
def test_dm_leave_dm_id_valid(clear_and_register):
    owner_token = clear_and_register
    user2 = auth_register("validemail2@gmail.com", "password", "Valid", "Email")
    dm_create(owner_token, [user2["auth_user_id"]])
    dm_leave(user2["token"], 0)
    assert dm_details(owner_token, 0)["members"] == [{"u_id": 0, "email": "validemail@gmail.com", "handle_str": "afirstlast1", "name_first": "aFirst", "name_last": "Last1", "profile_img_url": f"{config.url}static/default.jpg"}]
    assert dm_list(owner_token)["dms"][0]["dm_id"] == 0 
    assert dm_list(user2["token"])["dms"] == []

def test_dm_leave_invalid_dm_id(clear_and_register):
    owner_chat_1 = clear_and_register
    owner_chat_2 = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"] 
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    auth_register("validemail4@gmail.com", "password", "dFirst", "Last4")["token"]
    
    dm_create(owner_chat_1, [1, 3])
    dm_create(owner_chat_1, [1, 2])
    dm_create(owner_chat_2, [0, 2, 3]) 
    dm_create(owner_chat_2, [3]) 
    
    resp = dm_leave(owner_chat_1, 7)["code"]
    assert resp == 400
    
def test_dm_leave_basic_case(clear_and_register):
    owner_token = clear_and_register
    member_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    dm_create(owner_token, [1])
    assert len(dm_details(owner_token, 0)["members"]) == 2
    dm_leave(member_token, 0)
    assert len(dm_details(owner_token, 0)["members"]) == 1
    assert dm_details(owner_token, 0)["members"][0]["name_first"] == "aFirst"

def test_creator_leave(clear_and_register):
    owner_token = clear_and_register
    member_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    dm_create(owner_token, [1])
    assert len(dm_details(member_token, 0)["members"]) == 2
    dm_leave(owner_token, 0)
    assert len(dm_details(member_token, 0)["members"]) == 1
    assert dm_details(member_token, 0)["members"][0]["name_first"] == "bFirst" 

def test_messages_non_member(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    dm_create(owner_token, [1])
    non_member_token = auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    resp = dm_messages(non_member_token, 0, 0)["code"]
    assert resp == 403
    
def test_messages_invalid_dm_id(clear_and_register):
    owner_token = clear_and_register
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    dm_create(owner_token, [1])
    resp = dm_messages(owner_token, 2, 0)["code"]
    assert resp == 400

def test_messages_order(clear_and_register):
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_id = dm_create(clear_and_register, [1])["dm_id"]
    message_senddm(clear_and_register, dm_id, "Hello")
    message_senddm(clear_and_register, dm_id, "Hello")
    message_senddm(clear_and_register, dm_id, "Hello")
    resp = dm_messages(clear_and_register, dm_id, 0)
    array = [m['message_id'] for m in resp["messages"]]
    assert array == [2, 1, 0]

def test_messages_more_than_fifty(clear_and_register):
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    dm_id = dm_create(clear_and_register, [1])["dm_id"]
    for _ in range(51):
        message_senddm(clear_and_register, dm_id, "Hello")
    resp = dm_messages(clear_and_register, dm_id, 0)
    assert resp["end"] == 50    
   
        
def test_start_out_of_bounds(clear_and_register):
    owner_token = clear_and_register
    member_token = auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    dm_create(owner_token, [1])
    resp = dm_messages(member_token, 0, 1)["code"]
    assert resp == 400

def test_no_creation_duplicate_dm_id_after_removal(clear_and_register):
    owner_token = clear_and_register    
    auth_register("validemail2@gmail.com", "password", "bFirst", "Last2")["token"]
    auth_register("validemail3@gmail.com", "password", "cFirst", "Last3")["token"]
    resp_1 = dm_create(owner_token, [1])
    resp_2 = dm_create(owner_token, [1,2])
    resp_3 = dm_create(owner_token, [2])
    assert resp_1["dm_id"] == 0
    assert resp_2["dm_id"] == 1
    assert resp_3["dm_id"] == 2
    
    dm_remove(owner_token, 1)
    resp_4 = dm_create(owner_token, [1,2])    
    assert resp_4["dm_id"] != 2
    assert resp_4 == resp_2
