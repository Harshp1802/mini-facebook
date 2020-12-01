import pickle
def load_data(data_path= "database.pkl"):
    global DATABASE
    f = open(data_path,"rb")
    DATABASE = pickle.load(f)
    f.close()