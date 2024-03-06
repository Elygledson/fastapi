from pymongo import MongoClient
from fastapi import Depends
from pydantic import BaseModel
from bson.objectid import ObjectId
from abc import ABC, abstractmethod
from models.question import QuestionFactory
from config.environment import config


class Database(object):
    DATABASE = None

    @staticmethod
    def initialize(db_name):
        client = MongoClient(config.get('MONGODB_URI'),
                             serverSelectionTimeoutMS=5000)
        Database.DATABASE = client.get_database(db_name)

    @staticmethod
    def insert(collection, data):
        result = Database.DATABASE[collection].insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def insert_many(collection, data):
        Database.DATABASE[collection].insert_many(data)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def delete(collection, mongo_id):
        Database.DATABASE[collection].delete_one({'_id': ObjectId(mongo_id)})

    @staticmethod
    def update(collection, mongo_id, data):
        Database.DATABASE[collection].update_one(
            {'_id': ObjectId(mongo_id)}, {'$set': data}, upsert=False)


class BaseRepository(ABC):
    def __init__(self, db: Database = Depends()):
        self._db = db

    @property
    @abstractmethod
    def _collection(self):
        pass

    def find_all(self):
        return self._db.find(self._collection, {})

    def find_one(self, mongo_id):
        return self._db.find_one(self._collection, {'_id': ObjectId(mongo_id)})

    def insert(self, data: QuestionFactory):
         self._db.insert(self._collection, data.dict(exclude_none=True))

    def insert_many(self, data: QuestionFactory):
         self._db.insert_many(self._collection, data)

    def delete(self, data_id: str):
         self._db.delete(self._collection, data_id)

    def update(self, mongo_id: str, data: BaseModel):
         self._db.update(self._collection, mongo_id, data.dict(exclude_none=True))
