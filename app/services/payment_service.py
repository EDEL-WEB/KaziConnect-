from app import db
from app.models import Payment, Wallet, Transaction, Job
from datetime import datetime

class PaymentService:
    @staticmethod
    def release_payment(job_id):
        payment = Payment.query.filter_by(job_id=job_id).first_or_404()
        
        if payment.status != 'held':
            raise ValueError('Payment already processed')
        
        job = Job.query.get(job_id)
        if job.status != 'completed':
            raise ValueError('Job must be completed before releasing payment')
        
        worker_wallet = Wallet.query.filter_by(user_id=job.worker.user_id).with_for_update().first()
        
        if not worker_wallet:
            raise ValueError('Worker wallet not found')
        
        worker_wallet.balance += payment.worker_payout
        
        transaction = Transaction(
            wallet_id=worker_wallet.id,
            payment_id=payment.id,
            type='credit',
            amount=payment.worker_payout,
            description=f'Payment for job: {job.title}',
            balance_after=worker_wallet.balance
        )
        db.session.add(transaction)
        
        payment.status = 'released'
        payment.released_at = datetime.utcnow()
        
        db.session.commit()
        return payment
    
    @staticmethod
    def refund_payment(job_id):
        payment = Payment.query.filter_by(job_id=job_id).first_or_404()
        
        if payment.status != 'held':
            raise ValueError('Payment cannot be refunded')
        
        job = Job.query.get(job_id)
        customer_wallet = Wallet.query.filter_by(user_id=job.customer_id).with_for_update().first()
        
        customer_wallet.balance += payment.amount
        
        transaction = Transaction(
            wallet_id=customer_wallet.id,
            payment_id=payment.id,
            type='credit',
            amount=payment.amount,
            description=f'Refund for job: {job.title}',
            balance_after=customer_wallet.balance
        )
        db.session.add(transaction)
        
        payment.status = 'refunded'
        
        db.session.commit()
        return payment
    
    @staticmethod
    def get_wallet_balance(user_id):
        wallet = Wallet.query.filter_by(user_id=user_id).first_or_404()
        return wallet
    
    @staticmethod
    def get_transaction_history(user_id, limit=50):
        wallet = Wallet.query.filter_by(user_id=user_id).first_or_404()
        transactions = Transaction.query.filter_by(wallet_id=wallet.id).order_by(Transaction.created_at.desc()).limit(limit).all()
        return transactions
