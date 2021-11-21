import json
import os
import os.path

'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    "users": [],
    "channels": [],
    "direct_messages": [],
    "messages" : [],
    "user_stats": [],
    "workspace_stats": {
        "channels_exist": [],
        "dms_exist": [],
        "messages_exist": [],
        "utilization_rate": None
    }
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        if not os.path.isfile("database.json"):
            with open("database.json", "wt") as FILE:
                json.dump(initial_object, FILE)

    def get(self):
        # with open("database.json", "rt") as FILE:
        with open("database.json", "rt") as FILE:
            return json.load(FILE)

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')

        with open("database.json", "wt") as FILE:
            return json.dump(store, FILE)
        

print('Loading Datastore...')

global data_store
data_store = Datastore()

