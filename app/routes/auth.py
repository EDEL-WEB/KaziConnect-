from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_password

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not validate_email(data.get('email')):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(data.get('password')):
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            phone=data['phone'],
            role=data.get('role', 'customer')
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        token, user = AuthService.login_user(data['email'], data['password'])
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role
            }
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500
