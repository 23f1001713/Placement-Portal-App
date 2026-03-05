from flask import Flask,render_template,request , flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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






############## Home Page ##############

@app.route('/')
def home():
    return render_template('index.html' )


#######################login###################



@app.route('/login',methods =['GET','POST'])
def login():

    c = len(Company.query.all())
    s = len(Student.query.all())
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if not user:
            flash('Invalid Username')
            return render_template('login.html')
        if not check_password_hash(user.password_hash,password):
            flash('Incorrect Password')
            return render_template('login.html', c=c ,s=s)
        
        if user.is_active != True:
            flash('This user is not active')
            return render_template('login.html', c=c ,s=s)
        
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
                return render_template('login.html', c=c ,s=s)
            
        
        login_user(user)

        if user.role == 'ADMIN':
            return redirect(url_for('admin'))
        if user.role == 'COMPANY':
            return redirect(url_for('company'))
        if user.role == 'STUDENT':
            return redirect(url_for('student'))
        
    else:
        return render_template('login.html', c=c ,s=s)






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
#           STUDENT Register


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




##################### ADMIN Routes ###################################



@app.route("/admin")
@login_required
def admin():
    total_student = len(Student.query.all())
    total_applications = len(Application.query.all())
    total_blocked = Company.query.filter(Company.approval_status != 'APPROVED').all()
    total_approved = len(Student.query.filter(Student.is_blacklisted!= False).all())
    p_d = Drive.query.filter_by(status = "PENDING").all()
    total_active_drives = len(Drive.query.all())
    total_companies = len(Company.query.all())
    return render_template('admin/admin.html',t_s = total_student,
                           t_c = total_companies, 
                           t_a = total_applications,
                           t_a_d = total_active_drives,
                           p_c = len(total_blocked),
                           p_s = total_approved,
                           p_d = len(p_d)
                           )



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



@app.route('/block_unblock_student/<int:student_id>')
@login_required
def Block_unblock_student(student_id):

    stud = Student.query.get_or_404(student_id)
    
    if stud.is_blacklisted:
        stud.is_blacklisted = False
        flash(f"{stud.name} has been Unblocked.", "success")
    else:
        stud.is_blacklisted = True
        flash(f"{stud.name} has been Blocked.", "warning")
    
    db.session.commit()
    
    return redirect(url_for('admin_student'))

@app.route('/admin/student/<int:student_id>')
@login_required
def student_details(student_id):
   
    stud = Student.query.get_or_404(student_id)
    apple = Application.query.filter_by(student_id = stud.id).all()
    
    
    return render_template('admin/student_details.html',r = stud,apple=apple)



@app.route('/admin/companies')
@login_required
def admin_companies():
    com_det = Company.query.all()
    total_blocked = Company.query.filter(Company.approval_status != 'APPROVED').all()
    drive = Drive.query.all()

    return render_template('admin/admin_companies.html', com_det = com_det,drive = drive,t_c = len(com_det) , t_d = len(drive) ,t_b = len(total_blocked) )

@app.route('/search/result/company' , methods = ['POST'])
@login_required
def search_c():
    word = request.form.get("search")
    id ='company'
    r = Company.query.filter_by(company_name = word).first()
    if r:
        drive = Drive.query.filter_by(company_id = r.id).all()
    else:
        drive =''
    return render_template('admin/result.html',
                           r = r,id = id,drive = drive)



@app.route('/search/result/student' , methods = ['POST'])
@login_required
def search_s():
    word = request.form.get("search")
    id ='student'
    r = Student.query.filter_by(name = word).first()
    if r:
        apple = Application.query.filter_by(student_id = r.id).all()
    else:
        apple = ''
    return render_template('admin/result.html',
                           r = r,id = id,apple = apple)




@app.route('/admin/company/<int:company_id>')
@login_required
def company_details(company_id):
   
    company = Company.query.get_or_404(company_id) 
    
    company_drives = Drive.query.filter_by(company_id=company_id).all()
    
    return render_template('admin/company_details.html', r=company, drives=company_drives)





@app.route('/block_unblock/<int:company_id>')
@login_required
def Block_unblock(company_id):

    company = Company.query.get_or_404(company_id)
    
    if company.approval_status == 'PENDING':
        company.approval_status = 'APPROVED'
        flash(f"{company.company_name} has been Unblocked.", "success")
    else:
        company.approval_status = "PENDING"
        flash(f"{company.company_name} has been Blocked.", "warning")
    
    db.session.commit()
    
    return redirect(url_for('admin_companies'))




@app.route('/admin/drives')
@login_required
def admin_drives():
    d = Drive.query.all()
    t_p = len(Drive.query.filter_by(status = 'PENDING').all())
    t_a = len(Drive.query.filter_by(status = 'APPROVED').all())
    t_c = len(Drive.query.filter_by(status = 'CLOSED').all())

    return render_template('admin/admin_drives.html',t_d = len(d),t_p = t_p,t_c = t_c , t_a = t_a,drive = d)

@app.route('/drive_details/<int:drive_id>')
@login_required
def drive_detail(drive_id):
    d = Drive.query.filter_by(id = drive_id).first_or_404()
    return render_template('admin/drive_details.html',d = d )





@app.route('/app_drive/<int:drive_id>')
@login_required
def app_drive(drive_id):
    stat = Drive.query.get_or_404(drive_id)

    if stat.status == "APPROVED":
        stat.status = 'PENDING'
    elif stat.status == 'PENDING':
        stat.status = 'APPROVED'
    
    db.session.commit()
    return redirect(url_for('admin_drives'))


@app.route('/close_drive/<int:drive_id>')
@login_required
def close_drive(drive_id):
    stat = Drive.query.get_or_404(drive_id)
    if stat.status != 'CLOSED':
        stat.status = 'CLOSED'
    else:
        stat.status = 'APPROVED'

    db.session.commit()
    user = User.query.filter_by(id = current_user.id).first()
    if user.role == 'ADMIN':
        return redirect(url_for('admin_drives'))
    return redirect(url_for('company_drive'))



@app.route('/admin/<int:student_id>/history')
@login_required
def history_ad(student_id):

    
    apple = Application.query.filter_by(student_id = student_id)

    return render_template('student/student_history.html',
                           apple = apple)




@app.route('/admin/applications')
@login_required
def admin_applications():
    apple = Application.query.all()
    total_application = len(Application.query.all())
    total_pending = len(Application.query.filter_by(status='PENDING').all())
    total_shortlisted = len(Application.query.filter_by(status='SHORTLISTED').all())
    total_rejected = len(Application.query.filter_by(status='REJECTED').all())
    total_selected = len(Application.query.filter_by(status='SELECTED').all())
    return render_template('admin/admin_applications.html',t_a = total_application,
                           t_p = total_pending,t_app = total_selected,
                           t_s = total_shortlisted,
                           t_r = total_rejected,
                           apple = apple)


############################## STUDENT PROFILE ROUTES ############################################################


@app.route("/student")
@login_required
def student():
    t_d = Drive.query.filter(Drive.status != 'CLOSED').all()
    student = Student.query.filter_by(user_id = current_user.id).first_or_404()
    drive = Drive.query.filter_by(status = "APPROVED").limit(2).all()
    application = Application.query.filter_by(student_id = student.id).all()
    short = Application.query.filter(Application.student_id == student.id , Application.status == 'SHORTLISTED').all()
    sele = Application.query.filter(Application.student_id == student.id , Application.status == 'SELECTED').all()
    t_r = Application.query.filter_by(student_id = student.id,status = 'REJECTED').all()

    return render_template('student/student_dashboard.html',
                           t_d = len(t_d) ,
                           applied = len(application),
                           s = student,
                           apple = application,
                           sh = len(short),
                           se = len(sele),
                           drive = drive,
                           re = len(t_r))


@app.route("/student/profile")
@login_required
def student_profile():
    student = Student.query.filter_by(user_id = current_user.id).first_or_404()
    user = User.query.filter_by(id= current_user.id).first_or_404()
    return render_template('student/student_profile.html' ,
                           user = user,
                             student = student)





@app.route("/student/applications")
@login_required
def student_application():
    student = Student.query.filter_by(user_id = current_user.id).first_or_404()
    t_a = Application.query.filter_by(student_id = student.id).all()
    t_sh = Application.query.filter_by(student_id = student.id,status = 'SHORTLISTED').all()
    t_se = Application.query.filter_by(student_id = student.id,status = 'SELECTED').all()
    t_r = Application.query.filter_by(student_id = student.id,status = 'REJECTED').all()
    
    appli = Application.query.filter_by(student_id = student.id).all()
    

    return render_template('student/student_application.html',
                    t_a = len(t_a),
                    t_sh = len(t_sh),
                    t_r = len(t_r),
                    t_se = len(t_se),
                    appli = appli)




@app.route("/student/drive")
@login_required
def student_drive():

    drive = Drive.query.filter(Drive.status == 'APPROVED').all()
    return render_template('student/student_drive.html' , drive = drive)


@app.route('/student/apply/<int:drive_id>')
@login_required
def student_apply(drive_id):

    student = Student.query.filter_by(user_id = current_user.id).first_or_404()
    apple = Application.query.filter(Application.drive_id == drive_id ,
                                      Application.student_id == student.id).all()
    if apple :
        flash('You are already applied for this Drive','warning')
        return redirect(url_for('student_drive'))
    else:
        new_application = Application(
            drive_id =drive_id,
            student_id = student.id

        )

        db.session.add(new_application)
        db.session.commit()
    return redirect(url_for('student_application'))



@app.route('/history')
@login_required
def history_st():

    student = Student.query.filter_by(user_id = current_user.id).first_or_404()
    apple = Application.query.filter_by(student_id = student.id)

    return render_template('student/student_history.html',
                           apple = apple)





@app.route("/company")
@login_required
def company():
    
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    d_p = Drive.query.filter_by(company_id = current_user.id , status = "PENDING").all()
    drive = Drive.query.filter_by(company_id = company.id).all()
    applications = db.session.query(Application).join(Drive).filter(
    Drive.company_id == company.id
).all()
    students = db.session.query(Student).join(Application).filter(
        Application.student_id == Student.id
    ).all()
    t_shortlist = db.session.query(Application).join(Drive).filter(
    Drive.company_id == company.id , Application.status == 'SHORTLISTED'
).all()
    a_d = Drive.query.filter_by(company_id = company.id , status = "APPROVED").all()
    return render_template('company/company.html',c = company , 
                           d_p = len(d_p), drives = drive , a_d = len(a_d),
                           t_a = len(applications),
                           t_s = len(t_shortlist),
                           applications = applications)













@app.route("/company/applications")
@login_required
def company_app():
    c = Company.query.filter_by(user_id = current_user.id).first_or_404()
    applications = db.session.query(Application).join(Drive).filter(
    Drive.company_id == c.id
).all()
    return render_template('company/company_app.html',
                           applications = applications)



@app.route('/shortlist/<int:apple_id>')
@login_required
def shortlist(apple_id):
    a = Application.query.filter_by(id = apple_id).first_or_404()

    a.status = 'SHORTLISTED'
    db.session.commit()
    return redirect(url_for('company_app'))


@app.route('/reject/<int:apple_id>')
@login_required
def reject(apple_id):
    a = Application.query.filter_by(id = apple_id).first_or_404()

    a.status = 'REJECTED'
    db.session.commit()
    return redirect(url_for('company_app'))


@app.route('/select/<int:apple_id>')
@login_required
def select(apple_id):
    a = Application.query.filter_by(id = apple_id).first_or_404()

    a.status = 'SELECTED'
    db.session.commit()
    return redirect(url_for('company_app'))



@app.route('/pending/<int:apple_id>')
@login_required
def pending(apple_id):
    a = Application.query.filter_by(id = apple_id).first_or_404()

    a.status = 'PENDING'
    db.session.commit()
    return redirect(url_for('company_app'))




@app.route("/company/drives")
@login_required
def company_drive():
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    drive = Drive.query.filter_by(company_id = company.id).all()
    
    return render_template('company/company_drive.html',c = company , drives = drive)

@app.route("/company/create_drive")
@login_required
def company_create_drive():
    return render_template('company/create_drive.html',d = None,user = 'COMPANY')


@app.route('/create_drive',methods = ['POST'])
@login_required
def create_drive():
    job_title= request.form.get('job_title')
    job_description = request.form.get('description')
    eligibility = request.form.get('eligibility')
    deadline_s = request.form.get('deadline')
    company_id = Company.query.filter_by(user_id = current_user.id).first_or_404()
    try:
        deadline_obj = datetime.strptime(deadline_s, '%Y-%m-%dT%H:%M')
    except ValueError:
        
        deadline_obj = datetime.strptime(deadline_s, '%Y-%m-%dT%H:%M:%S')
    

    #----------------------------------------

    new_drive = Drive(
        company_id = company_id.id ,
        job_title = job_title,
        description = job_description,
        eligibility = eligibility,
        deadline = deadline_obj
    )

    db.session.add(new_drive)
    
    db.session.commit()
    flash('Drive Created sucessfully')
    return redirect(url_for('company_drive'))


@app.route('/edit/drive/<int:drive_id>')
@login_required
def edit_drive(drive_id):
    d = Drive.query.filter_by(id = drive_id).first_or_404()
    user = User.query.filter_by(id = current_user.id).first()
    return render_template('company/create_drive.html' , d = d, user = user.role)



@app.route('/update_drive/<int:drive_id>' ,methods = ['POST'])
@login_required
def update_drive(drive_id):
   
    job_title= request.form.get('job_title')
    job_description = request.form.get('description')
    eligibility = request.form.get('eligibility')
    deadline_s = request.form.get('deadline')
    
    try:
        deadline_obj = datetime.strptime(deadline_s, '%Y-%m-%dT%H:%M')
    except ValueError:
        
        deadline_obj = datetime.strptime(deadline_s, '%Y-%m-%dT%H:%M:%S')
    
    d = Drive.query.filter_by(id = drive_id).first()
    if job_title:
        d.job_title = job_title
    if job_description:
        d.description = job_description
    if eligibility:
        d.eligibility = eligibility
    if deadline_s:
        d.deadline = deadline_obj
    

    
    db.session.commit()
    flash('Drive Updated sucessfully')
    user = User.query.filter_by(id = current_user.id).first()
    if user.role == 'ADMIN':
        return redirect(url_for('admin_drives'))
    return redirect(url_for('company_drive'))




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
