import pytest
import requests
import json
from src import config
from tests.server_test_helper import auth_register, auth_login, clear

def test_login_v2_invalid_email():
    clear()
    auth_register("validemail@gmail.com", "password", "Valid", "Email")
    
    resp = auth_login("invalidemail@gmail.com", "password")["code"]
    assert resp == 400

def test_login_v2_invalid_password():
    clear()
    auth_register("validemail@gmail.com", "password", "Valid", "Email")
    
    resp = auth_login("validemail@gmail.com", "wrongpassword")["code"]
    assert resp == 400

def test_login_v2_valid_credentials():
    clear()
    register_data = auth_register("validemail@gmail.com", "password", "Valid", "Email")

    login_data = auth_login("validemail@gmail.com", "password")

    assert login_data['auth_user_id'] == register_data['auth_user_id']

def test_login_v1_multiple_users_mixed_order():
    clear()

    register_1_data = auth_register("validemail1@gmail.com", "password", "Valid", "Email")
    register_2_data = auth_register("validemail2@gmail.com", "password", "Valid1", "Email")
    register_3_data = auth_register("validemail3@gmail.com", "password", "Valid2", "Email")

    login_3_data = auth_login("validemail3@gmail.com", "password")
    login_1_data = auth_login("validemail1@gmail.com", "password")
    login_2_data = auth_login("validemail2@gmail.com", "password")

    assert login_1_data['auth_user_id'] == register_1_data['auth_user_id']
    assert login_2_data['auth_user_id'] == register_2_data['auth_user_id']
    assert login_3_data['auth_user_id'] == register_3_data['auth_user_id']
