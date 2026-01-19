from flask import Flask,render_template,request , flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash ,check_password_hash
from portal.models import db , User , Company, Student , Application , Drive,seed_admin
from flask_login import LoginManager,logout_user,login_required,login_user
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

app.config['SECRET_KEY'] = 'MY SECRET KEY'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))











@app.route('/')
def home():
    return render_template('index.html')


#######################login###################



@app.route('/login',methods =['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if not user:
            flash('Invalid Username')
            return render_template('login.html')
        if not check_password_hash(user.password_hash,password):
            flash('Incorrect Password')
            return render_template('login.html')
        
        if user.is_active != True:
            flash('his user is not active')
            return render_template('login.html')
        
        if user.role == "COMPANY":
            company = Company.query.filter_by(user_id=user.id).first()
            if company.is_blacklisted:
                flash('Company is blacklisted')
                return render_template('login.html')
            if company.approval_status != 'APPROVED':
                flash('Company not approved by admin')
                return render_template('login.html')
        
        if user.role == "STUDENT":
            student = Student.query.filter_by(user_id=user.id).first()
            if student.is_blacklisted:
                flash('Student is blacklisted')
                return render_template('login.html')
            
        
        login_user(user)

        if user.role == 'ADMIN':
            return redirect(url_for('admin'))
        if user.role == 'COMPANY':
            return redirect(url_for('company'))
        if user.role == 'STUDENT':
            return redirect(url_for('student'))
    else:
        return render_template('login.html')






########################Register Code###################
@app.route('/register')
def register():
    return render_template('register.html')

#----------------------------------------------------------------

@app.route('/register_company',methods = ['POST'])
def register_company():
    email= request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    comp_name = request.form.get('name')
    hr_contact = request.form.get('hr')
    web = request.form.get('website')

    #----------------------------------------

    new_user = User(
        email = email,
        username = username,
        password_hash = generate_password_hash(password),
        role = 'COMPANY'
    )

    db.session.add(new_user)
    db.session.flush()

    new_company = Company(
        user_id = new_user.id,
        company_name = comp_name,
        hr_contact = hr_contact,
        website =web

    )

    db.session.add(new_company)
    db.session.commit()
    flash('Registration sucessful now you can login')
    return redirect(url_for('login'))



#-----------------------------------------------------
#           STUDENT


@app.route('/student_register' , methods = ['POST'])
def student_register():
    email= request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    student_name = request.form.get('name')
    branch = request.form.get('branch')
    cgpa = request.form.get('cgpa')
    resume_path= request.form.get('resume_path')

    #----------------------------------------

    new_user = User(
        email = email,
        username = username,
        password_hash = generate_password_hash(password),
        role = 'STUDENT'
    )

    db.session.add(new_user)
    db.session.flush()

    new_company = Student(
        user_id = new_user.id,
        name = student_name,
        branch = branch,
        cgpa =cgpa,
        resume_path = resume_path

    )

    db.session.add(new_company)
    db.session.commit()
    flash('Registration sucessful now you can login')
    return redirect(url_for('login'))




########################################################





@app.route("/admin")
@login_required
def admin():
    return render_template('admin.html')


@app.route("/student")
@login_required
def student():
    return render_template('student.html')


@app.route("/company")
@login_required
def company():
    return render_template('company.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

















































if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
