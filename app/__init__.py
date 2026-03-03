from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from app.routes import auth, users, workers, categories, jobs, payments, reviews, sync, sms, ussd
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(workers.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(reviews.bp)
    app.register_blueprint(sync.bp)
    app.register_blueprint(sms.bp)
    app.register_blueprint(ussd.bp)
    
    return app
