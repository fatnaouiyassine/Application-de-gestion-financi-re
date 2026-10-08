from app import app, db
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('ALTER TABLE account ADD COLUMN account_number VARCHAR(20)'))
        db.session.commit()
        print('Added account_number column.')
    except OperationalError as e:
        if 'duplicate column name' in str(e):
            print('account_number column already exists.')
        else:
            print('Error adding account_number:', e)

    try:
        db.session.execute(text('ALTER TABLE account ADD COLUMN rib VARCHAR(30)'))
        db.session.commit()
        print('Added rib column.')
    except OperationalError as e:
        if 'duplicate column name' in str(e):
            print('rib column already exists.')
        else:
            print('Error adding rib:', e) 