import logging
from logging.handlers import RotatingFileHandler
import os
import time
from flask import Flask, jsonify, request, abort, g
from bookclass import Book, Bookstore
from datetime import datetime
import json

app = Flask(__name__)
book_store = Bookstore()
request_counter = 0

# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

class DateFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = datetime.datetime.fromtimestamp(record.created)
            s = t.strftime("%d-%m-%Y %H:%M:%S")
            s = f"{s}.{int(t.microsecond / 1000):03d}"
        return s

# Request logger
requests_logger = logging.getLogger('request-logger')
requests_logger.setLevel(logging.INFO)
request_handler = RotatingFileHandler('logs/requests.log', maxBytes=10000, backupCount=1)
request_formatter = DateFormatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s | request #%(request_counter)d', datefmt='%d-%m-%Y %H:%M:%S')
request_handler.setFormatter(request_formatter)
requests_logger.addHandler(request_handler)
requests_logger.addHandler(logging.StreamHandler())

# Books logger
books_logger = logging.getLogger('books-logger')
books_logger.setLevel(logging.INFO)
books_handler = RotatingFileHandler('logs/books.log', maxBytes=10000, backupCount=1)
books_formatter = DateFormatter('%(asctime)s.%(msecs)03d %(levelname)s: %(message)s | request #%(request_counter)d', datefmt='%d-%m-%Y %H:%M:%S')
books_handler.setFormatter(books_formatter)
books_logger.addHandler(books_handler)


class RequestCounterFilter(logging.Filter):
    def filter(self, record):
        record.request_counter = g.request_counter
        return True

requests_logger.addFilter(RequestCounterFilter())
books_logger.addFilter(RequestCounterFilter())

def log_request_start(resource, verb):
    global request_counter
    request_counter += 1
    g.request_counter = request_counter
    message = f'Incoming request | #{request_counter} | resource: {resource} | HTTP Verb {verb}'
    requests_logger.info(message)
    return request_counter

def log_request_duration(request_number, duration):
    message = f'request #{request_number} duration: {duration:.3f}ms'
    requests_logger.debug(message)

def log_books_info(message, request_number):
    books_logger.info(message)

def log_books_debug(message, request_number):
    books_logger.debug(message)

def log_books_error(message, request_number):
    books_logger.error(message)

@app.before_request
def log_before_request_info():
    g.start = time.time() * 1000.0
    g.request_counter = request_counter

@app.after_request
def log_after_request_info(response):
    time_to_execute = (time.time() * 1000.0) - g.start
    if response.status_code >= 400:
        log_request_duration(g.request_counter, time_to_execute)
    return response
#done
@app.route('/books/health', methods=['GET'])
def response_health():
    log_request_start('/books/health', 'GET')
    return "OK", 200

@app.route('/book', methods=['POST'])
def response_post():
    request_number = log_request_start('/book', 'POST')
    book_data = request.json
    error_message, status, new_book_data = Book.valid_book_check(book_data)

    if new_book_data is None:
        error_message = "Error: Book data is None"
        log_books_error(error_message, request_number)
        return jsonify({'errorMessage': error_message}), status

    new_book = Book(**new_book_data)
    error_message, book_added_id, stat = book_store.book_add(new_book)

    if stat == 200:
        log_books_info(f"Creating new Book with Title [{new_book.title}]", request_number)
        log_books_debug(f"Currently there are {book_store.books_number} Books in the system. New Book will be assigned with id {book_added_id}", request_number)
    else:
        log_books_error(error_message, request_number)

    return jsonify({'errorMessage': error_message, 'result': new_book.id if stat == 200 else None}), stat

@app.route('/books/total', methods=['GET'])
def check_books_query_param():
    request_number = log_request_start('/books/total', 'GET')
    persistence_method = request.args.get('persistenceMethod')
    query_params = {
        'author': request.args.get('author'),
        'price_bigger_than': request.args.get('price-bigger-than', type=int),
        'price_less_than': request.args.get('price-less-than', type=int),
        'year_bigger_than': request.args.get('year-bigger-than', type=int),
        'year_less_than': request.args.get('year-less-than', type=int),
        'genres': request.args.get('genres')
    }
    
    error_message, number_of_books, stat = book_store.check_books_stats_in_store(query_params,persistence_method)

    if stat == 400:
        error_message = "Error: Invalid genres filter"
        log_books_error(error_message, request_number)
        return jsonify({'errorMessage': error_message}), stat

    log_books_info(f"Total Books found for requested filters is {number_of_books}", request_number)
    return jsonify({'errorMessage': None, 'result': number_of_books})

@app.route('/books', methods=['GET'])
def get_books_data():
    request_number = log_request_start('/books', 'GET')
    persistence_method = request.args.get('persistenceMethod')
    query_params = {
        'author': request.args.get('author'),
        'price_bigger_than': request.args.get('price-bigger-than', type=int),
        'price_less_than': request.args.get('price-less-than', type=int),
        'year_bigger_than': request.args.get('year-bigger-than', type=int),
        'year_less_than': request.args.get('year-less-than', type=int),
        'genres': request.args.get('genres')
    }
    error_message, books, stat = book_store.get_books_data(query_params,persistence_method)

    if stat == 400:
        error_message = "Error: Invalid genres filter"
        log_books_error(error_message, request_number)
        return jsonify({'errorMessage': error_message}), stat

    log_books_info(f"Total Books found for requested filters is {len(books)}", request_number)
    return jsonify({'errorMessage': error_message, 'result': books}), stat

@app.route('/book', methods=['GET'])
def get_single_book_data():
    
    request_number = log_request_start('/book', 'GET')
    book_id = request.args.get('id', type=int)
    persistence_method = request.args.get('persistenceMethod')
    
    book = book_store.get_book_by_id(book_id,persistence_method)
    #genres_list = book.genres.split(',') if book.genres else []
    
    if book is not None:
        log_books_debug(f"Fetching book id {book_id} details", request_number)
        if persistence_method== 'POSTGRES':
            json_book = {
                'id': book.rawid,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'price': book.price,
                'genres':json.loads(book.genres)
            }
        elif persistence_method== 'MONGO':
             json_book = {
                  'id': book['rawid'],
                  'title': book['title'],
                  'author': book['author'],
                  'year': book['year'],
                  'price': book['price'],
                  'genres': book['genres'] 
            }
        return jsonify({'errorMessage': None, 'result': json_book}), 200
    else:
        error_message = f"Error: no such Book with id {book_id}"
        log_books_error(error_message, request_number)
        return jsonify({'errorMessage': error_message, 'result': None}), 404

@app.route('/book', methods=['PUT'])
def change_book_price():
    request_number = log_request_start('/book', 'PUT')
    book_data = {
        'id': request.args.get('id', type=int),
        'price': request.args.get('price', type=int)
    }
    price = book_data['price']
    book = book_store.get_book_by_id(book_data['id'],'POSTGRES')

    if book is None:
        error_message = f"Error: no such Book with id {book_data['id']}"
        log_books_error(error_message, request_number)
        stat = 404
    elif price is None or int(price) <= 0:
        error_message = f"Error: price update for book [{book_data['id']}] must be a positive integer"
        log_books_error(error_message, request_number)
        stat = 409
    else:
        old_price = book.price
        book_store.update_book_price(book_data['id'], price) #change to book.rawid
        error_message = None
        stat = 200
        log_books_info(f"Update Book id [{book_data['id']}] price to {price}", request_number)
        log_books_debug(f"Book [{book.title}] price change: {old_price} --> {price}", request_number)

  

    return jsonify({'errorMessage': error_message, 'result': old_price}), stat

@app.route('/book', methods=['DELETE'])
def delete_book():
    request_number = log_request_start('/book', 'DELETE')
    book_id = request.args.get('id', type=int)
    book = book_store.get_book_by_id(book_id,'POSTGRES')

    if book:
        log_books_info(f"Removing book [{book.title}]", request_number)
        log_books_debug(f"After removing book [{book.title}] id: [{book.rawid}] there are {book_store.books_number - 1} books in the system", request_number)
    error_message, book_deleted, stat = book_store.delete_book_from_book_store(book_id)
    
    if stat != 200:
        log_books_error(error_message, request_number)

    return jsonify({'errorMessage': error_message, 'result': book_deleted}), stat

@app.route('/logs/level', methods=['GET'])
def get_logger_level():
    request_number = log_request_start('/logs/level', 'GET')
    logger_name = request.args.get('logger-name')

    if logger_name == 'request-logger':
        level = logging.getLevelName(requests_logger.level)
    elif logger_name == 'books-logger':
        level = logging.getLevelName(books_logger.level)
    else:
        return "Failure: Invalid logger name", 400

    return level, 200

@app.route('/logs/level', methods=['PUT'])
def set_logger_level():
    request_number = log_request_start('/logs/level', 'PUT')
    logger_name = request.args.get('logger-name')
    logger_level = request.args.get('logger-level').upper()

    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'ERROR': logging.ERROR,
    }

    if logger_name == 'request-logger':
        logger = requests_logger
    elif logger_name == 'books-logger':
        logger = books_logger
    else:
        return "Failure: Invalid logger name", 400

    if logger_level not in log_levels:
        return "Failure: Invalid logger level", 400

    logger.setLevel(log_levels[logger_level])

    for handler in logger.handlers:
        handler.setLevel(log_levels[logger_level])

    return logging.getLevelName(logger.level), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8574)
