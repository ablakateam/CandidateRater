from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

    @property
    def average_rating(self):
        if len(self.reviews) == 0:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

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
