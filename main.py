from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from models import db, Candidate, Review, Admin
from config import Config
from utils import allowed_file, paginate
from collections import Counter
from functools import wraps
import logging

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG)

# ... (rest of the code remains the same)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
