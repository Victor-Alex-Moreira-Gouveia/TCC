import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'mariadb')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT', 3306))
    DATABASE_USER = os.getenv('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '19032007')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'MeusTratosDB')
    
    # Cache
    CACHE_HOST = os.getenv('CACHE_HOST', 'memcached')
    CACHE_PORT = int(os.getenv('CACHE_PORT', 11211))
    
    # Flask
    ENV = os.getenv('APP_ENV', 'production')
    DEBUG = ENV != 'production'
