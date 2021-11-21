from src import config
from src.error import AccessError, InputError
from src.other import clear_v1
from tests.server_test_helper import auth_register, clear
import json
import pytest
import requests

@pytest.fixture
def clear_and_register():
    clear()
    auth_register("validemail@gmail.com", "password", "Valid", "Email")

def test_register_server_duplicate_email(clear_and_register):
    auth_reg = auth_register("validemail@gmail.com", "password",  "Valid", "Email")
    assert auth_reg["code"] == 400

def test_register_server_invalid_email(clear_and_register):
    auth_reg = auth_register("invalidemail.com", "password", "Invalid", "Email")
    assert auth_reg["code"] == 400

def test_register_server_invalid_password(clear_and_register):
    auth_reg = auth_register("invalidpassword@gmail.com", "passw", "Invalid", "Password")
    assert auth_reg["code"] == 400

def test_register_server_invalid_name_first(clear_and_register):
    auth_reg = auth_register("invalidfirst@gmail.com", "password",  "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz", "Last")
    assert auth_reg["code"] == 400

def test_register_server_invalid_name_last(clear_and_register):
    auth_reg = auth_register("invalidlast@gmail.com", "password", "First", "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz")
    assert auth_reg["code"] == 400

def test_reigster_server_invalid_name_first2(clear_and_register):
    auth_reg = auth_register("invalidfirst@gmail.com", "password", " ", "Email")
    assert auth_reg["code"] == 400

def test_register_server_invalid_name_last2(clear_and_register):
    auth_reg = auth_register("invalidlast@gmail.com", "password", "Invalid", "")
    assert auth_reg["code"] == 400

def test_register_server_duplicate_names(clear_and_register):
    auth_reg = auth_register("validemail2@gmail.com", "password", "Valid", "Email")
    assert auth_reg["auth_user_id"] == 1
    
def test_register_server_long_handle(clear_and_register):
    auth_register("validemail2@gmail.com", "password", "Very Long Handle", "Very Long Handle")
