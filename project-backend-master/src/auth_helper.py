from datetime import datetime
from src.data_store import data_store
from src.error import InputError, AccessError
import re

#   Checks whether the email entered is of correct format
def email_check(email): 
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if (re.search(regex, email)):
        return True
    return False

#   Concatenate the full name of the user to 20 characters 
#   and if there is a repeating name add increasing integers after
def handle(store, name_first, name_last):
    first = ''.join(char for char in name_first if char.isalnum())
    last = ''.join(char for char in name_last if char.isalnum())

    conc = first.lower() + last.lower()
    
    if len(conc) > 20:
        conc = conc[slice(20)]
    
    conc_len = len(conc)
    handle_number = 0

    for users in store["users"]:
        if users["handle_str"] == conc:
            conc = conc[slice(conc_len)] + str(handle_number)
            handle_number += 1
    return conc

#   Checks whether the length of password, name_first, name_last
#   entered are within the boundaries
def length_check(password, name_first, name_last):
    if len(password) < 6:
        raise InputError(description="Password must be greater than 6 characters.")
    if len(name_first) < 1 or len(name_first) > 50 or name_first.isspace() == True:
        raise InputError(description="First name must be between 1 to 50 characters")
    if len(name_last) < 1 or len(name_last) > 50 or name_last.isspace() == True:
        raise InputError(description="Last name must be between 1 to 50 characters")
