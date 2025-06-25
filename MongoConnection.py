from pymongo import MongoClient # py -m pip install pymongo

class MongoConnection:
    def __init__(self, conn_name='mongodb://localhost:27017/', db_name='marketplace-images', collection_name='images'):
        self.conn = MongoClient(conn_name)
        self.db = self.conn[db_name]
        self.collection = self.db[collection_name]

    def get_collection(self):
        return self.collection