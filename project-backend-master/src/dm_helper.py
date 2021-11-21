#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 14:12:19 2021

@author: z5205018
"""
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import clear_v1
from src.jwt_helpers import decode_jwt

def find_dm(dm_id, store):
    dm_chat = None 
    for dm in store["direct_messages"]:
        if dm["dm_id"] == dm_id:
            dm_chat = dm
        
    return dm_chat

def find_member(token, dm, store):
    token_data = decode_jwt(token)
    token_id = token_data["auth_user_id"]
    dm_member = None
    for member in dm["all_members"]:
        if member["u_id"] == token_id:
            dm_member = member
            
    return dm_member
