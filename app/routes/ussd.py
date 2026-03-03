from flask import Blueprint, request
from app.services.ussd_service import USSDService

bp = Blueprint('ussd', __name__, url_prefix='/api/ussd')

@bp.route('/callback', methods=['POST'])
def ussd_callback():
    try:
        session_id = request.values.get('sessionId')
        phone = request.values.get('phoneNumber')
        text = request.values.get('text', '')
        
        response = USSDService.handle_ussd_request(session_id, phone, text)
        
        return response, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f"END Service error. Please try again.", 200, {'Content-Type': 'text/plain'}
