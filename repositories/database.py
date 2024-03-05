import motor.motor_asyncio
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
        client = motor.motor_asyncio.AsyncIOMotorClient(
            config.get('MONGODB_URI'), serverSelectionTimeoutMS=5000)
        Database.DATABASE = client.get_database(db_name)

    @staticmethod
    async def insert(collection, data):
        result = await Database.DATABASE[collection].insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    async def insert_many(collection, data):
        await Database.DATABASE[collection].insert_many(data)

    @staticmethod
    async def find_one(collection, query):
        return await Database.DATABASE[collection].find_one(query)

    @staticmethod
    async def find(collection, query):
        return await Database.DATABASE[collection].find(query).to_list(None)

    @staticmethod
    async def delete(collection, mongo_id):
        await Database.DATABASE[collection].delete_one({'_id': ObjectId(mongo_id)})

    @staticmethod
    async def update(collection, mongo_id, data):
        await Database.DATABASE[collection].update_one({'_id': ObjectId(mongo_id)}, {'$set': data}, upsert=False)


class BaseRepository(ABC):
    def __init__(self, db: Database = Depends()):
        self._db = db

    @property
    @abstractmethod
    def _collection(self):
        pass

    async def find_all(self):
        return await self._db.find(self._collection, {})

    async def find_one(self, mongo_id):
        return await self._db.find_one(self._collection, {'_id': ObjectId(mongo_id)})

    async def insert(self, data: QuestionFactory):
        await self._db.insert(self._collection, data.dict(exclude_none=True))

    async def insert_many(self, data: QuestionFactory):
        await self._db.insert_many(self._collection, data)

    async def delete(self, data_id: str):
        await self._db.delete(self._collection, data_id)

    async def update(self, mongo_id: str, data: BaseModel):
        await self._db.update(self._collection, mongo_id, data.dict(exclude_none=True))
