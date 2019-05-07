from pymongo import MongoClient


class MongodbConnection:
    """"Enables Connections to MongoDb"""

    def __init__(self,
                 mongo_db_address,
                 mongo_db_port,
                 db_name,
                 collection_name):
        self.db_name = db_name
        self.collection_name = collection_name

        self.mongo_db_address = mongo_db_address
        self.mongo_db_port = mongo_db_port

        self.client = self._init_client()
        self.db = self._init_db()
        self.collection = self._init_collection()

    def _init_client(self):
        """
        Initialises a client to MongoDB
        :return: None
        """
        return MongoClient(self.mongo_db_address, self.mongo_db_port)

    def _init_db(self):
        """
        Initialises the client's DB connection
        :return: MongoDb Connection to database
        """

        return self.client[self.db_name]

    def _init_collection(self):
        """
        Initialises the connection to the jobs collection
        :return: MongoDb Connection to specified collection
        """
        return self.db[self.collection_name]
