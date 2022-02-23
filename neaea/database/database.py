from typing import Union, List
from motor import motor_asyncio


class AsyncMongo:
    def __init__(self, mongo_db_url: str, database: str):
        self._client = motor_asyncio.AsyncIOMotorClient(mongo_db_url)
        self._DATABASE = database

    async def insert(self, collection: str, post: Union[dict, list]) -> None:
        db = self._client[self._DATABASE]
        collection = db[collection]
        if type(post) is dict:
            await collection.insert_one(post)
        elif type(post) is list:
            await collection.insert_many(post)

    async def find_one(
            self, collection: str,
            post: dict
    ) -> Union[dict, None]:
        db = self._client[self._DATABASE]
        collection = db[collection]
        if res := await collection.find_one(post):
            return res

    async def replace_one(
            self, collection: str, post: dict, post1: dict
    ) -> Union[bool, None]:
        db = self._client[self._DATABASE]
        collection = db[collection]
        if await collection.replace_one(post, post1):
            return True

    async def delete_one(self, collection: str, post: dict) -> Union[bool, None]:
        db = self._client[self._DATABASE]
        collection = db[collection]
        if await collection.delete_one(post):
            return True

    async def count_all(self, collection: str) -> Union[int, str]:
        db = self._client[self._DATABASE]
        collection = db[collection]
        return await collection.count_documents({})

    async def find_all(self, collection: str, post=None) -> List[dict]:
        if post is None:
            post = {}
        collections = []
        db = self._client[self._DATABASE]
        collection = db[collection]
        async for i in collection.find({}, post):
            collections.append(i)
        return collections
