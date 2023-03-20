import pymongo
import sys

class ContentMarketBuilder:
    bin_size: int   

def __init__():
    # DAO.get_users()
    args = sys.argv[1:]
    db_name = args[0]
    users_collection_name = args[1]

    db = pymongo.MongoClient()[db_name][users_collection_name]

    for user in db.find():
        supply = {}
    
def split_users():
    
def calculate_demands():

def calculate_supplies():
    # this should be on a user object (or producer / consumer wtv)
    supply = collections.default_dict([])

    for tweet in self.tweets:
        embedding = read_embedding(tweet_id)
        supply[calcualate_embedding_bin(embedding)] = embedding
    


def calcualate_embedding_bin(self, vector):
    return (((dimension // self.bin_size ) * self.bin_size) for dimension in vector)


        

if __name__ == '__main__':
    args = sys.argv[1:]
    config_file_name = args[0]
    db_name = args[1]
    users_collection_name = args[2]