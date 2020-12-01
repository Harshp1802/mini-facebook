import pickle
from collections import defaultdict 

DATABASE = {"user1": 
                {
                "Password": "pass",
                "is_online": False,
                "friends": [],
                "posts_visible_friends": [],
                "pending_friend_requests": [],
                "posts_global": [],
                "posts_private": [],
                "is_pending_request": False,
                "is_pending_message": False,
                "messages": defaultdict(list)
                }
            } # Read from the file

f = open("database.pkl", "wb")
pickle.dump(DATABASE,f)
f.close()
