from main import app, db
from models import Candidate
import random

def generate_btc_address():
    return ''.join(random.choices('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', k=34))

def add_sample_wallets():
    with app.app_context():
        candidates = Candidate.query.all()
        for candidate in candidates:
            if not candidate.btc_address:
                candidate.btc_address = generate_btc_address()
        db.session.commit()
        print(f"Updated {len(candidates)} candidates with sample BTC wallet addresses.")

if __name__ == '__main__':
    add_sample_wallets()
