from pymongo import MongoClient, errors

# from constants.defs import MONGO_CONN_STR

class DataDB:
    SAMPLE_COLL = "forex_sample"
    CALENDAR_COLL = "forex_calendar"
    INSTRUMENTS_COLL = "forex_instruments"

    def __init__(self):
        # self.client = MongoClient(MONGO_CONN_STR)
        # self.db = self.client.forex_learning
        pass
    
    
    def query_single(self, collection, **kwargs):
        return {}
        # try:            
        #     r = self.db[collection].find_one(kwargs, {'_id':0})
        #     return r
        # except errors.InvalidOperation as error:
        #     print("query_single error:", error)
        
            
    def query_all(self, collection, **kwargs):
        return {}

        # try:
        #     data = []
        #     r = self.db[collection].find(kwargs, {'_id':0})
        #     for item in r:
        #         data.append(item)
        #     return data
        # except errors.InvalidOperation as error:
        #     print("query_all error:", error)
