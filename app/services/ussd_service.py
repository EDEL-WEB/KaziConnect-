from app import db
from app.models.offline import USSDSession
from app.models import User, Job, Category

class USSDService:
    
    @staticmethod
    def handle_ussd_request(session_id, phone, text):
        session = USSDSession.query.filter_by(session_id=session_id).first()
        if not session:
            session = USSDSession(session_id=session_id, phone=phone)
            db.session.add(session)
        
        text_array = text.split('*') if text else []
        user_input = text_array[-1] if text_array else ''
        user = User.query.filter_by(phone=phone).first()
        
        if text == '':
            response = USSDService._main_menu(session, user)
        elif session.state == 'main_menu':
            response = USSDService._handle_main_menu(session, user, user_input)
        elif session.state == 'select_category':
            response = USSDService._handle_category_selection(session, user, user_input)
        elif session.state == 'enter_location':
            response = USSDService._handle_location_input(session, user, user_input)
        elif session.state == 'enter_budget':
            response = USSDService._handle_budget_input(session, user, user_input)
        elif session.state == 'check_jobs':
            response = USSDService._show_customer_jobs(user)
        else:
            response = "END Invalid session."
        
        db.session.commit()
        return response
    
    @staticmethod
    def _main_menu(session, user):
        session.state = 'main_menu'
        if not user:
            return "END Register on KaziConnect first."
        
        if user.role == 'customer':
            return "CON KaziConnect\n1. Book Service\n2. My Jobs\n3. Cancel Job"
        else:
            return "CON KaziConnect\n1. Available Jobs\n2. My Jobs\n3. Update Status"
    
    @staticmethod
    def _handle_main_menu(session, user, choice):
        if user.role == 'customer':
            if choice == '1':
                session.state = 'select_category'
                return USSDService._show_categories()
            elif choice == '2':
                return USSDService._show_customer_jobs(user)
        return "END Invalid option"
    
    @staticmethod
    def _show_categories():
        categories = Category.query.filter_by(is_active=True).limit(5).all()
        response = "CON Select Category:\n"
        for idx, cat in enumerate(categories, 1):
            response += f"{idx}. {cat.name}\n"
        return response
    
    @staticmethod
    def _handle_category_selection(session, user, choice):
        categories = Category.query.filter_by(is_active=True).limit(5).all()
        try:
            idx = int(choice) - 1
            selected = categories[idx]
            session.context_data['category_id'] = selected.id
            session.state = 'enter_location'
            db.session.commit()
            return "CON Enter location:"
        except:
            return "END Invalid selection"
    
    @staticmethod
    def _handle_location_input(session, user, location):
        session.context_data['location'] = location
        session.state = 'enter_budget'
        db.session.commit()
        return "CON Enter budget (KES):"
    
    @staticmethod
    def _handle_budget_input(session, user, budget):
        try:
            budget_amount = float(budget)
            
            from app.services.job_service import JobService
            job = JobService.create_job(
                customer_id=user.id,
                category_id=session.context_data['category_id'],
                title="USSD Job",
                description="Created via USSD",
                location=session.context_data['location'],
                budget=budget_amount
            )
            
            session.is_active = False
            db.session.commit()
            
            return f"END Job created! ID: {job.id[:8]}. SMS updates coming."
        except:
            return "END Invalid budget"
    
    @staticmethod
    def _show_customer_jobs(user):
        jobs = Job.query.filter_by(customer_id=user.id).order_by(Job.created_at.desc()).limit(5).all()
        if not jobs:
            return "END No jobs yet."
        
        response = "END Recent Jobs:\n"
        for job in jobs:
            response += f"{job.title[:20]} - {job.status}\n"
        return response
