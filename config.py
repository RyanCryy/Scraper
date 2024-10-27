# config.py
from flask_pymongo import PyMongo

class Config:
    MONGO_URI = "mongodb://localhost:27017/scraped_data"
