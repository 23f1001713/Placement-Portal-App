from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash


db = SQLAlchemy()




class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer , primary_key = True)
    email = db.Column(db.String(150) , nullable = False , unique = True)
    username = db.Column(db.String(20) , nullable= False , unique = True)
    password_hash = db.Column(db.String(200),nullable = False , unique = True)
    is_active = db.Column(db.Boolean , default = True)
    role = db.Column(db.String(30) ,nullable = False) #ADMIN,STUDENT,COMPANY



class Company(db.Model,UserMixin):
    __tablename__ = 'companies'
    id = db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable = False)
    company_name = db.Column(db.String(100) , unique = True, nullable = False)
    hr_contact = db.Column(db.String(20) , unique = True)
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20) , default = 'APPROVED') #APPROVED , PENDING , REJECTED
    is_blacklisted = db.Column(db.Boolean , default = False)



class Student(db.Model,UserMixin):
    __tablename__ = 'students'
    id = db.Column(db.Integer , primary_key = True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id') , nullable = False)
    name = db.Column(db.String(50),nullable = False)
    branch = db.Column(db.String(30) )
    cgpa = db.Column(db.Float ,nullable = False)
    resume_path = db.Column(db.String(200),nullable= False)
    is_blacklisted = db.Column(db.Boolean , default = False)



class Drive(db.Model,UserMixin):
    __tablename__ = 'placement_drives'
    id = db.Column(db.Integer , primary_key = True)
    company_id = db.Column(db.Integer,db.ForeignKey('companies.id') , nullable = False)
    job_title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(200), nullable = False)
    eligibility = db.Column(db.String(100), nullable = False)
    deadline = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(20), nullable = False,default ='APPROVED') #APPROVED,PENDING,CLOSED


class Application(db.Model,UserMixin):
    __tablename__ = 'applications'
    id = db.Column(db.Integer , primary_key = True)
    student_id = db.Column(db.Integer,db.ForeignKey('students.id'), nullable = False)
    drive_id = db.Column(db.Integer,db.ForeignKey('placement_drives.id') , nullable = False)
    applied_at = db.Column(db.DateTime,default = datetime.utcnow)
    status = db.Column(db.String(30), nullable = False,default = 'PENDING')#PENDING , SHORTLISTED,SELECTED , REJECTED

    __table_args__ = (
    db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),
)








def seed_admin():
    admin = User.query.filter_by(role = 'ADMIN').first()

    if not admin:
        admin = User(
            username='admin',
            email='admin@college.com',
            password_hash=generate_password_hash('admin123'),
            role='ADMIN',
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit() 
