Assume space are included in the characters limits  \n
Assume channels are created just using the register functions  \n
Assume channel names with just spaces are acceptable (spaces are counted as characters as well)  \n
Since is_public is not checked in this iteration all boolean are left as True  \n
Assume when user has an existing token and logins from somewhere else a new token is generated for that session  \n

Iteration 3  \n
For user_stats kept in data_store as a list of dictionaries -> [{"u_id": 0, "stats":{...}}, ...] for easier accessibility  \n