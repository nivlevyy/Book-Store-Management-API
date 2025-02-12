from pymongo import MongoClient

class MongoHelper:
    def __init__(self):
        self.client = MongoClient("mongodb://mongo-db:27017/")
        self.db = self.client['books']
        self.collection = self.db['books']

    def create_book(self, book):
        self.collection.insert_one({
            "rawid": book.id,
            "title": book.title,
            "author": book.author,
            "year": book.print_year,
            "price": book.price,
            "genres": book.genre
        })
    def get_book_by_id(self, rawid):
         """
         Fetch a single book document from the MongoDB collection by its rawid.

         :param rawid: The rawid of the book to fetch.
         :return: A dictionary containing the book data, or None if not found.
         """
         try:
             book = self.collection.find_one({"rawid": rawid})
             if book:
                 # Convert ObjectId to string for compatibility, if needed
                 book['_id'] = str(book['_id']) if '_id' in book else None
                 return book
             else:
                 print(f"[MongoDB] No book found with rawid {rawid}.")
                 return None
         except Exception as e:
             print(f"[MongoDB] Error fetching book by rawid {rawid}: {e}")
             return None
    def fetch_books(self,title):
        book=self.collection.find_one({"title" :title})
        return book if book else None
    
    def delete_books(self,book_id):
       result = self.collection.delete_one({"rawid": book_id})
       
    
    def update_price(self, rawid, price):
       
        # Update price
        self.collection.update_one({"rawid": rawid}, {"$set": {"price": price}})

    def count_books(self):
        return self.collection.count_documents({})
    
    
    def close(self):
        self.client.close()
