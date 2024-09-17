from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging

db = SQLAlchemy()

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Text, nullable=True)
    website = db.Column(db.Text, nullable=True)
    social_media = db.Column(db.Text, nullable=True)
    reviews = db.relationship('Review', backref='candidate', lazy=True)
    average_rating = db.Column(db.Float, default=0.0)
    btc_address = db.Column(db.String(100), nullable=True)
    youtube_snippet = db.Column(db.String(200), nullable=True)

    def recalculate_average_rating(self):
        reviews = self.reviews
        total_reviews = len(reviews)
        logging.info(f"Recalculating average rating for Candidate {self.id} ({self.name}) - Total reviews: {total_reviews}")
        
        if total_reviews == 0:
            logging.info(f"Candidate {self.id} ({self.name}) has no reviews")
            self.average_rating = 0.0
            total_rating = 0
        else:
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = round(total_rating / total_reviews, 2)
        
        logging.info(f"Candidate {self.id} ({self.name}) - Total rating: {total_rating}, Reviews: {total_reviews}, New Average: {self.average_rating:.2f}")
        db.session.commit()

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
