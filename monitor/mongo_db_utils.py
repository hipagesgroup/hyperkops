import os
from pymongo import MongoClient


class MongodbConnection:
    """"Enables Connections to MongoDb"""

    def __init__(self,
                 mongo_db_address=None,
                 mongo_db_port=None):

        self._mongo_db_address = mongo_db_address if mongo_db_address is not None else os.environ['MONGO_DB_ADDRESS']
        self._mongo_db_port = mongo_db_port if mongo_db_port is not None else int(os.environ['MONGO_DB_PORT'])
        self._client = None
        self._db = None
        self._collection = None

    def _init_client(self):
        """
        Initialises a client to MongoDB
        :return: None
        """
        if self._client is None:
            self._client = MongoClient(self._mongo_db_address, self._mongo_db_port)

    def _init_db(self, db_name):
        """
        Initialises the client's DB connection
        :param db_name: Name of the database to connect to
        :return: None
        """
        if self._db is None:
            self._db = self._client[db_name]

    def _init_collection(self, collection_name):
        """
        Initialises the connection to the jobs collection
        :param collection_name : Name of the collection within the database
        :return: None
        """
        self._collection = self._db[collection_name]

    def init_connection_to_collection(self, db_name, collection_name):
        self._init_client()
        self._init_db(db_name)
        self._init_collection(collection_name)
