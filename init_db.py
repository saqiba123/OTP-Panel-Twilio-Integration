import os
from dotenv import load_dotenv
from sqlalchemy import Float, create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    

class VirtualNumber(Base):
    __tablename__ = "virtual_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    number = Column(String(20), unique=True, index=True)
    is_used = Column(Boolean, default=False)


class OTP(Base):
    __tablename__ = "otp_store"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, index=True)
    otp = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  
    status = Column(String(20),nullable=False, default="active")  


print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
