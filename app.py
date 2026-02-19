from flask import Flask,render_template,request , flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash ,check_password_hash
from portal.models import db , User , Company, Student , Application , Drive,seed_admin
from flask_login import LoginManager,logout_user,login_required,login_user,current_user
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

app.config['SECRET_KEY'] = 'MY SECRET KEY'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))











@app.route('/')
def home():
    return render_template('index.html')


#######################login###################



@app.route('/login',methods =['GET','POST'])
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
            flash('This user is not active')
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
    total_student = len(Student.query.all())
    total_applications = len(Application.query.all())
    total_active_drives = len(Drive.query.all())
    total_companies = len(Company.query.all())
    return render_template('admin/admin.html',t_s = total_student,t_c = total_companies, t_a = total_applications,t_a_d = total_active_drives)






@app.route('/admin/student')
@login_required
def admin_student():
    total_student = Student.query.all()
    apple = Application.query.all()
    total_approved = len(Student.query.filter(Student.is_blacklisted!= True).all())
    total_blocked = len(total_student) - total_approved
    return render_template('admin/admin_student.html',
                           t_s = len(total_student),
                           t_app = total_approved,
                           t_b = total_blocked,
                           stud = total_student,
                           apple = apple
                           )








@app.route('/admin/companies')
@login_required
def admin_companies():
    com_det = Company.query.all()
    total_blocked = Company.query.filter(Company.approval_status != 'APPROVED').all()
    drive = Drive.query.all()

    return render_template('admin/admin_companies.html', com_det = com_det,drive = drive,t_c = len(com_det) , t_d = len(drive) ,t_b = len(total_blocked) )











@app.route('/admin/drives')
@login_required
def admin_drives():
    return render_template('admin/admin_drives.html')










@app.route('/admin/report')
@login_required
def admin_reports():
    return render_template('admin/admin_report.html')











@app.route('/admin/applications')
def admin_applications():
    apple = Application.query.all()
    total_application = len(Application.query.all())
    total_pending = len(Application.query.filter_by(status='PENDING').all())
    total_shortlisted = len(Application.query.filter_by(status='SHORTLISTED').all())
    total_rejected = len(Application.query.filter_by(status='REJECTED').all())
    total_selected = len(Application.query.filter_by(status='SELECTED').all())
    return render_template('admin/admin_applications.html',t_a = total_application,t_p = total_pending,t_app = total_selected,t_s = total_shortlisted,t_r = total_rejected,apple = apple)









@app.route("/student")
@login_required
def student():
    return render_template('student/student_dashboard.html')

@app.route("/student/profile")
@login_required
def student_profile():
    return render_template('student/student_profile.html')

@app.route("/student/applications")
@login_required
def student_application():
    return render_template('student/student_application.html')

@app.route("/student/drive")
@login_required
def student_drive():
    return render_template('student/student_drive.html')














@app.route("/company")
@login_required
def company():
    return render_template('company.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/test')
def test():
    com_det = Company.query.all()
    for c in com_det:
        print(c.approval_status)
    return 'done'













































if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
