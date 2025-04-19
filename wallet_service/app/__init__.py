from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config
from app.database import db
import threading
from app.kafka.consumer import start_consuming



# Khởi tạo database
# db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Load config từ file config.py
    app.config.from_object(Config)
    
    # Cấu hình CORS (cho phép API nhận request từ frontend)
    CORS(app)

    # Khởi tạo database với app
    db.init_app(app)
    migrate.init_app(app, db)

    # Đăng ký blueprint cho routes
    from app.routes.wallet_routes import wallet_bp
    from app.routes.transaction_routes import wallet_bp_t
    
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(wallet_bp_t, url_prefix='/wallet/transactions')

    threading.Thread(target=start_consuming, daemon=True).start()

    return app
app = create_app()  # Thêm dòng này
