#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient

# The code to analyze data loaded into MongoDB

def get_db(db_name):
    client = MongoClient('localhost:27017')
    db = client.get_database(db_name)
    return db

# Constrution of analysis pipeline
def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [{"$group" : {"_id" : "$created.user",
                             "count" : {"$sum" : 1} } },
        {"$sort" : {"count" : -1}}]
    return pipeline

# Main pert of the code: getting db, making pipeline, invokation of analysis,
# and result output
db = get_db('test')
pipeline = make_pipeline()
result = db['nizhniy-novgorod_russia'].aggregate(pipeline)
for doc in result:
    print(doc)
#import pprint
#pprint.pprint(result)