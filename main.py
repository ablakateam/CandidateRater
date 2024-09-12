from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Candidate, Review, Admin
from utils import allowed_file, paginate
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Candidate.query
    if search:
        query = query.filter(Candidate.name.ilike(f'%{search}%'))
    candidates = paginate(query.order_by(Candidate.id.desc()), page, per_page=9)
    return render_template('index.html', candidates=candidates, search=search)

@app.route('/candidate/<int:id>', methods=['GET', 'POST'])
def candidate(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        review = Review(rating=rating, comment=comment, candidate=candidate)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('candidate', id=id))
    
    reviews = Review.query.filter_by(candidate_id=id).order_by(Review.created_at.desc()).all()
    ratings_data = [0, 0, 0, 0, 0]
    for review in reviews:
        ratings_data[review.rating - 1] += 1
    
    return render_template('candidate.html', candidate=candidate, reviews=reviews, ratings_data=ratings_data)

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

@app.route('/admin/add_candidate', methods=['GET', 'POST'])
def admin_add_candidate():
    if 'admin_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        bio = request.form['bio']
        contact = request.form['contact']
        skills = request.form['skills']
        experience = request.form['experience']
        education = request.form['education']
        photo = request.files['photo']
        
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Invalid file type. Please upload an image.', 'error')
            return redirect(url_for('admin_add_candidate'))
        
        new_candidate = Candidate(name=name, bio=bio, contact=contact, photo=filename, skills=skills, experience=experience, education=education)
        db.session.add(new_candidate)
        db.session.commit()
        flash('New candidate added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_candidate.html')

@app.route('/admin/edit_candidate/<int:id>', methods=['GET', 'POST'])
def admin_edit_candidate(id):
    if 'admin_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    candidate = Candidate.query.get_or_404(id)
    
    if request.method == 'POST':
        candidate.name = request.form['name']
        candidate.bio = request.form['bio']
        candidate.contact = request.form['contact']
        candidate.skills = request.form['skills']
        candidate.experience = request.form['experience']
        candidate.education = request.form['education']
        
        photo = request.files['photo']
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            candidate.photo = filename
        
        db.session.commit()
        flash('Candidate updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_candidate.html', candidate=candidate)

@app.route('/admin/delete_candidate/<int:id>', methods=['POST'])
def admin_delete_candidate(id):
    if 'admin_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    candidate = Candidate.query.get_or_404(id)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    candidates = Candidate.query.filter(Candidate.name.ilike(f'%{query}%')).all()
    results = []
    for candidate in candidates:
        results.append({
            'id': candidate.id,
            'name': candidate.name,
            'photo': candidate.photo,
            'rating': candidate.average_rating,
            'review_count': len(candidate.reviews)
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
