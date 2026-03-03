from app import db
from app.models import Review, Job
from app.services.worker_service import WorkerService

class ReviewService:
    @staticmethod
    def create_review(job_id, customer_id, rating, comment=None):
        job = Job.query.get_or_404(job_id)
        
        if job.customer_id != customer_id:
            raise ValueError('Only the customer can review this job')
        
        if job.status != 'completed':
            raise ValueError('Job must be completed before reviewing')
        
        if Review.query.filter_by(job_id=job_id).first():
            raise ValueError('Review already exists for this job')
        
        if rating < 1 or rating > 5:
            raise ValueError('Rating must be between 1 and 5')
        
        review = Review(job_id=job_id, customer_id=customer_id, worker_id=job.worker_id, 
                       rating=rating, comment=comment)
        db.session.add(review)
        
        WorkerService.update_worker_rating(job.worker_id, rating)
        
        db.session.commit()
        return review
    
    @staticmethod
    def get_worker_reviews(worker_id, limit=20):
        reviews = Review.query.filter_by(worker_id=worker_id).order_by(Review.created_at.desc()).limit(limit).all()
        return reviews
