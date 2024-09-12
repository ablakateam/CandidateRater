from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, Candidate, Review, Admin
from config import Config
from utils import allowed_file, paginate
from collections import Counter
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def create_sample_candidates():
    if Candidate.query.count() == 0:
        sample_candidates = [
            Candidate(name="John Doe", bio="Experienced software developer", contact="john@example.com", photo="https://via.placeholder.com/150?text=John+Doe"),
            Candidate(name="Jane Smith", bio="Marketing specialist", contact="jane@example.com", photo="https://via.placeholder.com/150?text=Jane+Smith"),
            Candidate(name="Bob Johnson", bio="Project manager", contact="bob@example.com", photo="https://via.placeholder.com/150?text=Bob+Johnson"),
        ]
        db.session.add_all(sample_candidates)
        db.session.commit()

def create_admin_user():
    if Admin.query.count() == 0:
        admin = Admin(username="admin", password=generate_password_hash("admin123"))
        db.session.add(admin)
        db.session.commit()

with app.app_context():
    db.create_all()
    create_sample_candidates()
    create_admin_user()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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
    
    # Calculate ratings distribution
    ratings = [review.rating for review in candidate.reviews]
    ratings_counter = Counter(ratings)
    ratings_data = [ratings_counter[i] for i in range(1, 6)]
    
    return render_template('candidate.html', candidate=candidate, ratings_data=ratings_data)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    candidates = Candidate.query.filter(Candidate.name.ilike(f'%{query}%')).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'photo': c.photo,
        'rating': c.average_rating,
        'review_count': len(c.reviews)
    } for c in candidates])

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@admin_required
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    candidates = Candidate.query.all()
    return render_template('admin/dashboard.html', candidates=candidates)

@app.route('/admin/candidate/add', methods=['GET', 'POST'])
@admin_required
def admin_add_candidate():
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        contact = request.form.get('contact')
        photo = request.files.get('photo')
        
        if name and bio and contact and photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            
            new_candidate = Candidate(name=name, bio=bio, contact=contact, photo=filename)
            db.session.add(new_candidate)
            db.session.commit()
            
            flash('Candidate added successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Please fill in all fields and upload a valid image.', 'error')
    
    return render_template('admin/add_candidate.html')

@app.route('/admin/candidate/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_candidate(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        candidate.name = request.form.get('name')
        candidate.bio = request.form.get('bio')
        candidate.contact = request.form.get('contact')
        
        photo = request.files.get('photo')
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            candidate.photo = filename
        
        db.session.commit()
        flash('Candidate updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_candidate.html', candidate=candidate)

@app.route('/admin/candidate/delete/<int:id>', methods=['POST'])
@admin_required
def admin_delete_candidate(id):
    candidate = Candidate.query.get_or_404(id)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
