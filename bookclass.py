
from sqlalchemy import and_ 
from sqlalchemy import or_
from warnings import filters
from flask import jsonify, request
import json
from db.models import Books
from db.mongo_helper import MongoHelper
from db import get_session

class Book:

    def __init__(self,title,author,year,price,genres):
        self.id=None
        self.title=title
        self.author=author
        self.print_year=year
        self.price=price
        self.genre=genres
      
    @staticmethod
    def valid_book_check(book):
        try:
            book_data={  
               
            'title':book.get('title'),
            'author':book.get('author'),
            'year': int(book.get('year')),
            'price':int(book.get('price')),
            'genres':book.get('genres'),
            #'persistenceMethod':book.get('persistenceMethod')
            
            }
            
        except:
            return None,409,None
        
        if any(value is None for value in book_data.values()):
            return None,409,None
        elif not 1940<= book_data['year']<=2100:
         return f"Error: Can't create new Book that its year [{ book_data['print year']}] is not in the accepted range [1940 -> 2100]",409,None
         
        elif book_data['price']<=0:
         return  "Error: Can't create new Book with negative price",409, None
         
      
        return None,None,book_data  


class Bookstore:
    
   # books_genres = ['SCI_FI', 'NOVEL', 'HISTORY', 'MANGA', 'ROMANCE', 'PROFESSIONAL']
    #change book id to start from the next book id count
    
    def __init__(self):
     # self.postgres = PostgresHelper()
     self.postgres_session = get_session()
     self.mongo = MongoHelper()
     self.books_number = self.postgres_session.query(Books).count()
     self.next_book_id = self.books_number + 1
  
     
     # if self.postgres.count_books() != self.mongo.count_books():
     #    raise ValueError("Inconsistent book count between Postgres and MongoDB")

     #self.books_number = self.postgres.count_books()
     """this row below needed"""
     #self.next_book_id = self.book_number + 1
    # self.storebook={}
  
    #work
    def book_add(self,book):
        try:
            """ check if book exist"""
           
            postgres_book = self.postgres_session.query(Books).filter_by(title = book.title).first()
            if postgres_book :
               return (f'Error: Book with the title [{book.title}] already exists in the system'), None, 409
            
            """ mongodb checking """
            mongo_book = self.mongo.fetch_books(book.title)
            if mongo_book:
               return (f'Error: Book with the title [{book.title}] already exists in the system'), None, 409

            #for value in self.storebook.values():
            #  if value.title.lower() == book.title.lower():
            #   return (f'Error: Book with the title [{book.title}] already exists in the system'),None,409
            
            book.id = self.next_book_id
            #self.storebook[self.next_book_id] = book
            """ add book to postgres"""
            new_book = Books(
            rawid=book.id,
            title=book.title,
            author=book.author,
            year=book.print_year,
            price=book.price,
            genres=json.dumps(book.genre) if isinstance(book.genre, list) else book.genre
        )
            self.postgres_session.add(new_book)
            self.postgres_session.commit()
            
            """ add book to mongodb"""
            self.mongo.create_book(book)
            
            self.next_book_id += 1
            self.books_number += 1
            return None,book.id,200
        except Exception as e:
            return (f'Error: {str(e)}'), None, 500
    
   
    #work
    def check_books_stats_in_store(self,query_params,persistence_method):
     
       total_books_match=0
          
       if all(value is None for value in query_params.values()):
        return None, self.books_number,200
      
       if self.validate_genres(query_params):
           return None,total_books_match,400
       
       filters=self.get_filters(query_params)
       
       if persistence_method == 'POSTGRES':
             conditions = [
         Books.author == filters.get('author') if filters.get('author') is not None else None,
         Books.year > filters.get('year_bigger_than') if filters.get('year_bigger_than') is not None else None,
         Books.year < filters.get('year_less_than') if filters.get('year_less_than') is not None else None,
         Books.price > int(filters.get('price_bigger_than')) if filters.get('price_bigger_than') is not None else None,
         Books.price < int(filters.get('price_less_than')) if filters.get('price_less_than') is not None else None,
         ]

             # Remove None values from the conditions
             conditions = [condition for condition in conditions if condition is not None]

             # Apply filters dynamically
             query = self.postgres_session.query(Books).filter(and_(*conditions))
             
             genres = filters.get('genres')
             if genres:
                 if isinstance(genres, set):
                     genres = ','.join(genres)  # Convert set to string
                 books = books.filter(or_(*[Books.genres.like(f'%{genre}%') for genre in genres]))
                 
             books = query.all()
             total_books_match = len(books)
       elif persistence_method == 'MONGO':
             # MongoDB Logic
             mongo_filters = {}

             # Map filters to MongoDB query structure
             if filters.get('author'):
                 mongo_filters["author"] = filters['author']
             if filters.get('year_bigger_than'):
                 mongo_filters["year"] = {"$gt": filters['year_bigger_than']}
             if filters.get('year_less_than'):
                 mongo_filters.setdefault("year", {})["$lt"] = filters['year_less_than']
             if filters.get('price_bigger_than'):
                 mongo_filters["price"] = {"$gt": filters['price_bigger_than']}
             if filters.get('price_less_than'):
                 mongo_filters.setdefault("price", {})["$lt"] = filters['price_less_than']
             if filters.get('genres'):
                 mongo_filters["genres"] = {"$all": list(filters['genres'])}

             # Fetch matching books from MongoDB
             books = self.mongo.collection.find(mongo_filters)
             total_books_match = books.count() if hasattr(books, "count") else len(list(books))

       # for book in self.storebook.values():
       #    if self.validate_books_follow_query(filters,book):
       #     total_books_match+=1
          
       return None,total_books_match,200
    #work
    def validate_books_follow_query(self,filters,book):
       
        if filters.get('author') is not None:
          if filters['author'].lower()!=book.author.lower():
             return False
            
        if filters.get('price_bigger_than') is not None:
          if book.price <=int( filters['price_bigger_than']):
           return False

        if filters.get('price_less_than')is not None:
           if book.price > int(filters['price_less_than']):
            return False

        if filters.get('year_bigger_than') is not None:
           if book.year < filters['year_bigger_than']:
             return False
       
        if filters.get('year_less_than')is not None:
           if book.year > filters['year_less_than']:
            return False
       
        
        genres = filters.get('genres')
        
        if genres is not None:
            book_converted_genres = set(json.loads(book.genres))
            if not genres.issubset(book_converted_genres):
                return False
            return True

      
    #work
    def validate_genres(self,query_params):
       if query_params.get('genres'):
         query_genres= set(query_params['genres'].split(','))
         for genre in query_genres:
           if query_genres.issubset(genre) is None:
                return True
       return False
    #WORK
    def get_books_data(self, query_params, persistence_method):
         json_books = []

         # Validate genres filter
         if self.validate_genres(query_params):
             return None, None, 400

         # Extract filters
         filters = self.get_filters(query_params)

         if persistence_method == 'POSTGRES':
             # PostgreSQL Logic
             conditions = [
                 Books.author == filters.get('author') if filters.get('author') is not None else None,
                 Books.year > filters.get('year_bigger_than') if filters.get('year_bigger_than') is not None else None,
                 Books.year < filters.get('year_less_than') if filters.get('year_less_than') is not None else None,
                 Books.price > int(filters.get('price_bigger_than')) if filters.get('price_bigger_than') is not None else None,
                 Books.price < int(filters.get('price_less_than')) if filters.get('price_less_than') is not None else None,
             ]

             # Remove None values from the conditions
             conditions = [condition for condition in conditions if condition is not None]

             # Apply filters dynamically
             query = self.postgres_session.query(Books).filter(and_(*conditions))

             # Handle genres filter
             genres = filters.get('genres')
             if genres:
                 if isinstance(genres, set):
                     genres_filters = [Books.genres.like(f'%"{genre}"%') for genre in genres]
                     query = query.filter(and_(*genres_filters))

             # Execute the query
             books = query.all()

         elif persistence_method == 'MONGO':
             # MongoDB Logic
             mongo_filters = {}

             # Map filters to MongoDB query structure
             if filters.get('author'):
                 mongo_filters["author"] = filters['author']
             if filters.get('year_bigger_than'):
                 mongo_filters["year"] = {"$gt": filters['year_bigger_than']}
             if filters.get('year_less_than'):
                 mongo_filters.setdefault("year", {})["$lt"] = filters['year_less_than']
             if filters.get('price_bigger_than'):
                 mongo_filters["price"] = {"$gt": filters['price_bigger_than']}
             if filters.get('price_less_than'):
                 mongo_filters.setdefault("price", {})["$lt"] = filters['price_less_than']
             if filters.get('genres'):
                 mongo_filters["genres"] = {"$all": list(filters['genres'])}

             # Fetch books from MongoDB
             books = self.mongo.collection.find(mongo_filters)

         else:
             return None, None, 400

         # Convert book objects to JSON format
         for book in books:
             if persistence_method == 'POSTGRES':
                 json_books.append({
                     'id': book.rawid,
                     'title': book.title,
                     'author': book.author,
                     'year': book.year,
                     'price': book.price,
                     'genres': json.loads(book.genres) if isinstance(book.genres, str) else book.genres,
                 })
             elif persistence_method == 'MONGO':
                 json_books.append({
                     'id': book['rawid'],
                     'title': book['title'],
                     'author': book['author'],
                     'year': book['year'],
                     'price': book['price'],
                     'genres': book['genres'],
                 })

         # Sort books by title (case insensitive)
         json_books.sort(key=lambda x: x['title'].lower())

         return None, json_books, 200

   #work
    def get_filters(self,query_params):
       
        filters={}
        
        if query_params.get('author') is not None:
           filters['author']=query_params.get('author')
           
        if query_params.get('price_bigger_than') is not None:
           filters['price_bigger_than']=int(query_params.get('price_bigger_than'))
           
        if query_params.get('price_less_than') is not None:
           filters['price_less_than']=int(query_params.get('price_less_than'))
           
        if query_params.get('year_bigger_than') is not None:
           filters['year_bigger_than']=int(query_params.get('year_bigger_than'))  
           
        if query_params.get('year_less_than') is not None:
           filters['year_less_than']=int(query_params.get('year_less_than'))
           
        if query_params.get('genres') is not None:
           filters['genres'] = set(query_params['genres'].split(','))  
        
        
        return filters

    #work    
    def get_book_by_id(self,book_id,persistence_method):
        if persistence_method == 'POSTGRES':
            return self.postgres_session.query(Books).filter_by(rawid = book_id).first()
        else:
           return  self.mongo.collection.find_one({"rawid": book_id})


  #work
    def update_book_price(self,book_id,price):
         try:
            json_books=[]
            # Update price in MongoDB
            self.mongo.update_price(book_id, price)

            # Fetch and update price in PostgreSQL
            book_postgres = self.postgres_session.query(Books).filter_by(rawid=book_id).first()
          
        
     
            #print(f'{book_postgres.price}')
            
            if not book_postgres:
                raise ValueError(f"Book with ID {book_id} not found in PostgreSQL.")

            old_book_price = book_postgres.price
            book_postgres.price = price
            self.postgres_session.commit()
           # print(f'{book_postgres.price}')
            return old_book_price

         except Exception as e:
            self.postgres_session.rollback()  # Rollback changes if something goes wrong
            raise e  
       

    #work
    def delete_book_from_book_store(self,book_id):
        if book_id :
            book = self.postgres_session.query(Books).filter_by(rawid = book_id).first()
        
            if book is not None:
             self.postgres_session.delete(book)
             self.postgres_session.commit()
             
             self.mongo.delete_books(book_id)
            
             self.books_number -= 1
             return None,self.books_number,200
            else:
               return f"Error: no such Book with id {book_id}",None,404
        else:
            return f"Error: no such Book with id {book_id}",None,404
       
       







         
        
