import sys
import ijson
import pymongo

def main():
    args = sys.argv[1:]
    user_tweets_json_path = args[0]
    db_name = args[1]
    users_collection_name = args[2]

    db = pymongo.MongoClient()[db_name][users_collection_name]

    with open(user_tweets_json_path) as user_tweets_json_file:
        for record in ijson.items(user_tweets_json_file, "item"):
            # TODO: try turning this into an upsert
            create_user_if_not_exist(db, record['user_id'])

            db.update_one({'user_id': record['user_id']}, { '$push': { 'retweets': record['id'] }} )
            if record['retweet_id'] is not None: # we have retweet
                create_user_if_not_exist(db, record['retweet_user_id'])
                db.update_one({'user_id': record['retweet_user_id']}, { '$push': { 'retweets_in_community': record['retweet_id'] }})
                db.update_one({'user_id': record['user_id']}, { '$push': { 'retweets': record['id'] }} )
            else: # insert
                db.update_one({'user_id': record['user_id']}, { '$push': { 'tweets': record['id'] }} )
                
def create_user_if_not_exist(db, user_id):
    if not db.find_one({'user_id': user_id}): # insert a new record for this user
        db.insert_one({'user_id': user_id, 'tweets': [], 'retweets': [], 'retweets_in_community': []})

if __name__ == '__main__':
    main()