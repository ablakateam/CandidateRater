from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Candidate, Review, Admin
from utils import allowed_file, paginate
import os
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

# ... (rest of the file remains unchanged)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
