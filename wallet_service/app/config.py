import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://myuser:mysecretpassword@database:5432/wallet")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    VNP_TMNCODE = os.getenv("VNP_TMNCODE")
    VNP_HASH_SECRET = os.getenv("VNP_HASH_SECRET")
    VNP_URL = os.getenv("VNP_URL")
    VNP_RETURN_URL = os.getenv("VNP_RETURN_URL")


# DATABASE_URL=postgresql://myuser:mysecretpassword@database:5432/mydb
