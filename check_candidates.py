from main import app, db
from models import Candidate

with app.app_context():
    candidates = Candidate.query.all()
    print(f'Total candidates: {len(candidates)}')
    for candidate in candidates[:5]:
        print(f'{candidate.name}: BTC: {candidate.btc_address}, DOGE: {candidate.doge_address}')
