from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, Candidate, Review, Admin
from utils import allowed_file, paginate
import logging

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Candidate.query
    if search:
        query = query.filter(Candidate.name.ilike(f'%{search}%'))
    candidates = paginate(query.order_by(Candidate.name), page)
    return render_template('index.html', candidates=candidates, search=search)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process the form data (you can add email sending logic here)
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/candidate/<int:id>', methods=['GET', 'POST'])
def candidate(id):
    candidate = Candidate.query.get_or_404(id)
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form['comment']
        new_review = Review(rating=rating, comment=comment, candidate_id=candidate.id)
        db.session.add(new_review)
        db.session.commit()
        candidate.recalculate_average_rating()
        flash('Your review has been submitted successfully!', 'success')
        return redirect(url_for('candidate', id=id))
    return render_template('candidate.html', candidate=candidate)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    candidates = Candidate.query.filter(Candidate.name.ilike(f'%{query}%')).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'photo': c.photo,
        'average_rating': c.average_rating,
        'reviews': len(c.reviews)
    } for c in candidates])

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
        flash('Please log in to access this page', 'error')
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
        phone = request.form['phone']
        website = request.form['website']
        social_media = request.form['social_media']
        btc_address = request.form['btc_address']
        doge_address = request.form['doge_address']
        
        if 'photo' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['photo']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_candidate = Candidate(
                name=name,
                bio=bio,
                contact=contact,
                phone=phone,
                website=website,
                social_media=social_media,
                photo=filename,
                btc_address=btc_address,
                doge_address=doge_address
            )
            
            db.session.add(new_candidate)
            db.session.commit()
            
            flash('New candidate added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid file type', 'error')
    
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
        candidate.phone = request.form['phone']
        candidate.website = request.form['website']
        candidate.social_media = request.form['social_media']
        candidate.btc_address = request.form['btc_address']
        candidate.doge_address = request.form['doge_address']
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

@app.route('/admin/manage_reviews/<int:candidate_id>')
def admin_manage_reviews(candidate_id):
    if 'admin_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    reviews = Review.query.filter_by(candidate_id=candidate_id).order_by(Review.created_at.desc()).all()
    return render_template('admin/manage_reviews.html', candidate=candidate, reviews=reviews)

@app.route('/admin/delete_review/<int:review_id>', methods=['POST'])
def admin_delete_review(review_id):
    if 'admin_id' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('admin_login'))
    
    review = Review.query.get_or_404(review_id)
    candidate = review.candidate
    db.session.delete(review)
    db.session.commit()
    candidate.recalculate_average_rating()
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('admin_manage_reviews', candidate_id=candidate.id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
