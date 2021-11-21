import pytest
import requests
import json
from src import config
from tests.server_test_helper import auth_register, auth_login, auth_logout, clear

def test_user_logout_invalid_token():
    clear()
    token = auth_register("validemail@gmail.com", "password", "Valid", "Email")["token"]
    auth_logout(token)
    assert auth_logout(token)["code"] == 403

def test_logout_twice():
    clear()
    register_data = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    auth_logout(register_data["token"])

    resp = auth_logout(register_data["token"])["code"]

    assert resp == 403

def test_user_reg_logout():
    clear()
    register_data = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    assert auth_logout(register_data["token"]) == {}

def test_user_reg_login_logout():
    clear()
    register_data = auth_register("validemail@gmail.com", "password", "Valid", "Email")
    login_data = auth_login("validemail@gmail.com", "password")
    assert auth_logout(register_data["token"]) == {}
    assert auth_logout(login_data["token"]) == {}

def test_user_multiple_login_logout():
    clear()
    register_data = auth_register("validemail@gmail.com", "password", "Valid", "Email")

    login_data = auth_login("validemail@gmail.com", "password")

    assert auth_logout(login_data["token"]) == {}

    login_data = auth_login("validemail@gmail.com", "password")

    assert auth_logout(login_data["token"]) == {}
    assert auth_logout(register_data["token"]) == {}

def test_multiple_users_logout():
    clear()
    register_1_data = auth_register("validemail1@gmail.com", "password", "Valid1", "Email")
    register_2_data = auth_register("validemail2@gmail.com", "password", "Valid2", "Email")
    register_3_data = auth_register("validemail3@gmail.com", "password", "Valid3", "Email")

    assert auth_logout(register_3_data["token"]) == {}
    assert auth_logout(register_2_data["token"]) == {}
    assert auth_logout(register_1_data["token"]) == {}