from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, Candidate, Review, Admin
from config import Config
from utils import allowed_file, paginate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def create_sample_candidates():
    if Candidate.query.count() == 0:
        sample_candidates = [
            Candidate(name="John Doe", bio="Experienced software developer", contact="john@example.com", photo="john.jpg"),
            Candidate(name="Jane Smith", bio="Marketing specialist", contact="jane@example.com", photo="jane.jpg"),
            Candidate(name="Bob Johnson", bio="Project manager", contact="bob@example.com", photo="bob.jpg"),
        ]
        db.session.add_all(sample_candidates)
        db.session.commit()

with app.app_context():
    db.create_all()
    create_sample_candidates()

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    candidates_query = Candidate.query.filter(Candidate.name.ilike(f'%{search}%')).order_by(Candidate.id)
    candidates_page = paginate(candidates_query, page, per_page=6)
    
    return render_template('index.html', candidates=candidates_page, search=search)

@app.route('/candidate/<int:id>', methods=['GET', 'POST'])
def candidate(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        if rating and 1 <= rating <= 5:
            review = Review(rating=rating, comment=comment, candidate_id=id)
            db.session.add(review)
            db.session.commit()
            flash('Your review has been submitted!', 'success')
        else:
            flash('Invalid rating. Please rate between 1 and 5.', 'error')
    return render_template('candidate.html', candidate=candidate)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    candidates = Candidate.query.filter(Candidate.name.ilike(f'%{query}%')).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'photo': url_for('static', filename=f'img/{c.photo}'),
        'rating': c.average_rating,
        'review_count': len(c.reviews)
    } for c in candidates])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
