from app import db
from app.models import User, Wallet
from flask_jwt_extended import create_access_token

class AuthService:
    @staticmethod
    def register_user(email, password, full_name, phone, role='customer'):
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
        
        user = User(email=email, full_name=full_name, phone=phone, role=role)
        user.set_password(password)
        
        db.session.add(user)
        
        wallet = Wallet(user_id=user.id)
        db.session.add(wallet)
        
        db.session.commit()
        return user
    
    @staticmethod
    def login_user(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError('Invalid credentials')
        
        if not user.is_active:
            raise ValueError('Account is inactive')
        
        token = create_access_token(identity=user.id, additional_claims={'role': user.role})
        return token, user
