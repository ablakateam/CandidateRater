from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Candidate, Review, Admin
from utils import allowed_file, paginate
import os
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Candidate.query
    if search:
        query = query.filter(Candidate.name.ilike(f'%{search}%'))
    candidates = paginate(query.order_by(Candidate.name), page, per_page=6)
    
    logging.info(f"Displaying index page with {len(candidates.items)} candidates")
    return render_template('index.html', candidates=candidates, search=search)

@app.route('/candidate/<int:id>', methods=['GET', 'POST'])
def candidate(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        logging.info(f"Received review for Candidate {id} - Rating: {rating}, Comment: {comment}")
        
        review = Review(rating=rating, comment=comment, candidate_id=candidate.id)
        db.session.add(review)
        db.session.commit()
        logging.info(f"New review added for Candidate {candidate.id} ({candidate.name}) - Rating: {rating}")
        
        candidate.recalculate_average_rating()
        logging.info(f"Recalculated average rating for Candidate {candidate.id} ({candidate.name}) - New average: {candidate.average_rating}")
        
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('candidate', id=id))
    
    logging.info(f"Displaying candidate page for Candidate {candidate.id} ({candidate.name})")
    return render_template('candidate.html', candidate=candidate)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please log in to access the admin dashboard', 'error')
        return redirect(url_for('admin_login'))
    candidates = Candidate.query.all()
    return render_template('admin/dashboard.html', candidates=candidates)

# ... (rest of the code remains unchanged)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
