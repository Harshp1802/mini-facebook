import pickle
DATABASE = {"user1": 
                {
                "Password": "pass",
                "is_online": False,
                "friends": [],
                "posts_visible_friends": [],
                "pending_friend_requests": [],
                "posts_global": [],
                "posts_private": [],
                }
            } # Read from the file

f = open("database.pkl", "wb")
pickle.dump(DATABASE,f)
f.close()
