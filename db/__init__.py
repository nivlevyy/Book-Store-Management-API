from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Connection string
CONNECTION_STRING = "postgresql://postgres:docker@postgres-db:5432/books"

# Create SQLAlchemy engine
engine = create_engine(CONNECTION_STRING)

# Create session factory
Session = sessionmaker(bind=engine)

# Base for ORM models
Base = declarative_base()

# Function to initialize the database session
def get_session():
    return Session()
