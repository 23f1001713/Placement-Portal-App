from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from portal.models import db , User , Company, Student , Application , Drive,seed_admin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

app.config['SECRET_KEY'] = 'MY SECRET KEY'
db.init_app(app)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
