import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://myuser:mysecretpassword@database:5432/wallet")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")


# DATABASE_URL=postgresql://myuser:mysecretpassword@database:5432/mydb
