from pymongo import MongoClient

class CollConection:

    def __init__(self,dbName,collection):
        self.client = MongoClient()
        self.db = self.client[dbName]
        self.collection=self.db[collection]

    def addDocument(self,document):
        a=self.collection.insert_one(document)
        print("Inserted", a.inserted_id)
        return a.inserted_id
    
    def addLine(self, autor, chiste):
        document={'chat':chat,
                'user':user,
                'line':line}
        return self.addDocument(document)

    