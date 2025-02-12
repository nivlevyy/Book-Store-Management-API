# 📚 Book Management API

This project is a **Flask-based Book Management System** that allows users to store, retrieve, update, and delete book records using **PostgreSQL** and **MongoDB**. The project supports **RESTful APIs**, **logging**, and **containerized deployment using Docker**.

---

## 🚀 Features

- **Book Management**: Add, fetch, update, and delete books.
- **Logging**: Tracks API requests and logs actions.
- **Dual Database Support**:
  - **PostgreSQL** (Relational storage)
  - **MongoDB** (NoSQL storage)
- **Dockerized Deployment**: Uses `docker-compose.yml` for easy setup.

---

## 📂 Project Structure

```bash
📂 books-api
 ├── 📂 db
 │   ├── __init__.py        # Database connection
 │   ├── models.py          # SQLAlchemy models
 │   ├── mongo_helper.py    # MongoDB Helper Class
 ├── serverLog.py           # API Logging
 ├── bookclass.py           # Business Logic
 ├── requirements.txt       # Python Dependencies
 ├── Dockerfile             # Container Setup
 ├── docker-compose.yml     # Service Orchestration
 ├── .gitignore             # Git Ignore Configurations
 ├── README.md              # Project Documentation
 ├── book_management_api.postman_collection.json  # API Test Collection
 ├── Books test final_collection.json  # Extended API Tests
```

---

## 🛠 Setup & Installation

### 1️⃣ Prerequisites

Ensure you have:

- Python 3.8+
- PostgreSQL & MongoDB installed
- Docker & Docker Compose (Optional)

### 2️⃣ Installation Steps

#### **Using Docker** (Recommended)

```sh
docker-compose up --build
```

This will start **PostgreSQL, MongoDB, and the Flask API** inside containers.

##### **Troubleshooting Docker Issues**

If you see an error like:

```sh
no configuration file provided: not found
```

Try the following:

1. **Ensure You're in the Correct Directory**

   ```sh
   cd path/to/your/project
   docker-compose up -d
   ```

   Make sure `docker-compose.yml` is inside this folder. If unsure, locate it with:

   ```sh
   dir /s /b docker-compose.yml  # Windows
   find . -name "docker-compose.yml"  # Linux/macOS
   ```

2. **Verify That ********`docker-compose.yml`******** Exists**
   If missing, **download it again**:
   [📥 docker-compose.yml](sandbox:/mnt/data/docker-compose.yml)
   Place it inside your project folder.

3. **Check If ********`docker-compose`******** Is Installed**

   ```sh
   docker-compose --version
   ```

   If missing:

   - **Windows**: Install **Docker Desktop** ([Download Here](https://www.docker.com/products/docker-desktop))
   - **Linux**:
     ```sh
     sudo apt update
     sudo apt install docker-compose -y
     ```

4. **Try Again**

   ```sh
   docker-compose up --build
   ```

#### **Running Without Docker**

If you don't have Docker, follow these steps:

##### **1️⃣ Install PostgreSQL & MongoDB**

###### **Linux (Ubuntu)**

```sh
sudo apt update && sudo apt install postgresql mongodb -y
sudo systemctl start postgresql
sudo systemctl start mongodb
```

###### **Windows**

1. [Download PostgreSQL](https://www.postgresql.org/download/) and install it.
2. [Download MongoDB](https://www.mongodb.com/try/download/community) and install it.
3. Start both services from **Services Manager (services.msc)**.

##### **2️⃣ Configure Database Connections**

Edit `db/__init__.py` to update the PostgreSQL connection string:

```python
CONNECTION_STRING = "postgresql://postgres:yourpassword@localhost:5432/books"
```

For **MongoDB**, update `mongo_helper.py`:

```python
self.client = MongoClient("mongodb://localhost:27017/")
```

##### **3️⃣ Initialize the PostgreSQL Database**

```sh
psql -U postgres
CREATE DATABASE books;
\q
```

##### **4️⃣ Install Dependencies**

```sh
pip install -r requirements.txt
```

##### **5️⃣ Run Flask Server**

```sh
python serverLog.py
```

The server should now be running at `http://localhost:8574`.

---

## 🔥 API Testing with Postman

To test the API using **Postman**, follow these steps:

1. **Download the Postman Collections**:

   - [📥 Basic API Tests](sandbox:/mnt/data/book_management_api.postman_collection.json)
   - [📥 Full API Tests](sandbox:/mnt/data/Books%20test%20final_collection.json)

2. **Import the Collections in Postman**:

   - Open Postman
   - Click **Import** > **Choose File**
   - Select the JSON files you downloaded.

3. **Run the API Requests**:

   - Start your server using Docker or manually.
   - Run the requests in Postman to test API functionality.

---

## 📌 Logging System

Logs are stored in *`logs/requests.log`*\* and **`logs/books.log`** and track API usage and book actions.\*

---

## 📦 Deployment

To deploy the project to production, use Docker or deploy it manually using a WSGI server like Gunicorn.

---

## 📜 License

MIT License

