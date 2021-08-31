from flask import Flask, render_template, url_for, flash, redirect, request, send_file
from classroom import app, db, bcrypt, mail
from classroom.forms import Sign_up_form, Login_form, Reset_request_form, \
                                Reset_password_form, Join_class, Create_class, \
                                Assign_assignment
from classroom.models import User, Room, Post, Assignment, AssignmentSubmission
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from werkzeug.utils import secure_filename
import hashlib
hash_file = hashlib.sha256()

import random
import string
import os
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash('Already Logged In. Please Log Out to Register', 'info')
        return redirect(url_for('dashboard'))

    form = Sign_up_form()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, dob=form.dob.data, mobile=form.mobile.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for { form.username.data } ! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title='Join Us Today', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('Already Logged In.', 'info')
        return redirect(url_for('dashboard'))

    form = Login_form()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='login', form=form)


def send_reset_email(user):
    
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='face.dandd@gmail.com', recipients=[user.email])
    msg.body = f'''
    To reset Password, Click on the following link (expires in 30 mins)
    {url_for('reset_password', token=token, _external=True)}
    '''
    mail.send(msg)


@app.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = Reset_request_form()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Please check your mail for reset !', 'info')
        return redirect(url_for('login'))

    return render_template('password_reset.html', title='Forgot Password', form=form)

@app.route('/forget_password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid request or Expired token !!!', 'warning')
        return redirect(url_for('forget_password'))
    
    form = Reset_password_form()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset! ', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', title='Reset Password',form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    cls = []
    if current_user.classes != None:
        for i in current_user.classes.split(',')[:-1]:
            c = Room.query.filter_by(id=i).first()
            cls.append(c)
    return render_template('dashboard.html', title="Dashboard", res=cls)


@app.route('/new_class', methods=["GET", "POST"])
@login_required
def new_class():
    class_id=''
    for i in range(3):
        class_id+=''.join(random.choice(string.ascii_letters) for x in range(3))
        class_id+='-'
    class_id = class_id[:-2]

    form = Create_class()
    if form.validate_on_submit():
        cls = Room.query.filter_by(name=form.name.data, teacher=current_user.username).first()
        if not cls:
            room = Room(id=class_id, name=form.name.data, teacher=current_user.username, students='')
            db.session.add(room)
            if current_user.classes == None:
                current_user.classes = f'{class_id},'
            else:
                current_user.classes += f'{class_id},'
            db.session.commit()
            print(os.getcwd())
            #os.mkdir(app.config['UPLOAD_FOLDER'])
            print(os.listdir())
            #os.mkdir(f'classroom/uploads/{class_id}')
            up_dir = app.config['UPLOAD_FOLDER']
            print('#'*100)
            print(up_dir)
            os.chdir(up_dir[:])
            os.mkdir(f'{ class_id }')

            flash(f'Class {form.name.data} created!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(f'You have already created a class with this name', 'danger')
            return redirect(url_for('classroom_home', id=cls.id))
        
    return render_template('create_class.html',form=form)

@app.route('/join_class', methods=["GET", "POST"])
@login_required
def join_class():
    
    form = Join_class()
    if form.validate_on_submit():
        room = Room.query.filter_by(id=form.id.data).first()
        if room:
            if current_user.classes == None:
                current_user.classes = f'{form.id.data},'
            elif form.id.data not in current_user.classes:
                current_user.classes += f'{form.id.data},'
            else:
                flash(f'Already a member of this class: {form.id.data}', 'info')
                return redirect(url_for('classroom_home', id=form.id.data))
            
            db.session.commit()
            msg = f'Welcome {current_user.username} !'
            #msg = Post(class_id=id, content=msg, cnt_by=current_user.username)
            msg = Post(class_id=form.id.data, content=msg, cnt_by='Bot')
            db.session.add(msg)
            db.session.commit()

            if room.students == None: 
                room.students = f'{current_user.username},'
            elif form.id.data not in room.students:
                room.students += f'{current_user.username},'
            else:
                flash('Already a memeber', 'info')
            db.session.commit()
        else:
            flash('Invalid Class ID', 'danger')
            return redirect(url_for('join_class'))
        return redirect(url_for('classroom_home', id=form.id.data))
    return render_template('join_class.html', form=form)

@app.route('/class-home/<id>', methods=["GET", "POST"])
@login_required
def classroom_home(id):

    room = Room.query.filter_by(id=id).first()
    if not room:
        flash('Invalid Request!', 'danger')
        return redirect(url_for('dashboard'))

    if id not in current_user.classes:
        return redirect(url_for('dashboard'))

    
    if request.method == "POST":
        msg = request.form['msgbox']
        if msg:
            msg = Post(class_id=id, content=msg, cnt_by=current_user.username)
            db.session.add(msg)
            db.session.commit()

    cls = Room.query.filter_by(id=id).first()
    cnts = []
    asgn_ids = []
    for i in Post.query.filter_by(class_id=id).all():
        val = (i.cnt_by, i.content)
        cnts.append(val)
        if 'Assignment' in val[1] and 'Bot' in val[0]:
            asgn_id = Assignment.query.filter_by(class_id=id, title=val[1][val[1].index('Assignment')+11:]).first()
            #print(val[1][val[1].index('Assignment')+11:])
            for i in Assignment.query.filter_by(class_id=id).all():
                print(i.title == val[1][val[1].index('Assignment')+11:])
            asgn_ids.append(asgn_id.assignment_id)
        else:
            asgn_ids.append(0)
    return render_template('class_main.html', msgs=cnts, id=id, cls=cls, asgn_ids=asgn_ids)

#return render_template('assign_assignment.html', title='Assignments')
@app.route('/class-home/<id>/assignments')
@login_required
def assignments(id):

    room = Room.query.filter_by(id=id).first()
    if not room:
        flash('Invalid Request!', 'danger')
        return redirect(url_for('dashboard'))

    isTeacher = 0
    cls = Room.query.filter_by(id=id).first()
    if current_user.username == cls.teacher:
        isTeacher = 1
    
    asgns = []
    for i in Assignment.query.filter_by(class_id=id).all():
        asgns.append(i)
    return render_template('assignment.html', title='Assignments', asgns=asgns, id=id,isTeacher=isTeacher)


@app.route('/class-home/<id>/assignments/assign', methods=["GET", "POST"])
@login_required
def assign_assignment(id):

    room = Room.query.filter_by(id=id).first()
    if not room:
        flash('Invalid Request!', 'danger')
        return redirect(url_for('dashboard'))

    cls = Room.query.filter_by(id=id).first()
    if current_user.username != cls.teacher: 
        return redirect(url_for('assignments', id=id))
    
    form = Assign_assignment()

    if form.validate_on_submit():
        hash_file.update(form.title.data.encode('utf-8'))
        h = hash_file.hexdigest()
        a_id = id + '_' + h[20:30]
        asgn = Assignment(assignment_id= a_id,class_id=id, title=form.title.data, 
                            description=form.description.data, due=form.due.data)
        db.session.add(asgn)
        db.session.commit()

        msg = f'{current_user.username} assigned a Assignment {asgn.title}'
        #msg = Post(class_id=id, content=msg, cnt_by=current_user.username)
        msg = Post(class_id=id, content=msg, cnt_by='Bot')
        db.session.add(msg)
        db.session.commit()
        
        flash(f'Assignment {form.title.data} Assigned!', 'success')
        return redirect(url_for('assignments', id=id))

    return render_template('assign_assignment.html', form=form)

@app.route('/class-home/<id>/assignments/view/<asgn_id>', methods=["GET", "POST"])
@login_required
def view_assignment(id, asgn_id):

    room = Room.query.filter_by(id=id).first()
    if not room:
        flash('Invalid Request!', 'danger')
        return redirect(url_for('dashboard'))

    cls = Room.query.filter_by(id=id).first()
    isTeacher = 0
    if current_user.username == cls.teacher:
        isTeacher = 1


    assignment = Assignment.query.filter_by(assignment_id=asgn_id).first()
    if not assignment:
        flash('Invalid Request', 'danger')
        return redirect(url_for('assignments', id=id))

    if request.method == "POST":
        if 'file' not in request.files:
            pass
        file = request.files['file']
        if file.filename == '':
            pass
        else:
            #path = f"{ app.config['UPLOAD_FOLDER'] }{ id }"
            path = os.path.join(app.config['UPLOAD_FOLDER'][:], id)
            filename = secure_filename( f'{current_user.username}__{asgn_id}__' + file.filename )
            file.save(os.path.join(path, filename))
            val = AssignmentSubmission(assignment_id=asgn_id,
                                    submission_user=current_user.username, submission_content=filename)
            db.session.add(val)
            db.session.commit()
    
    filenames = []
    if isTeacher:
        for i in AssignmentSubmission.query.filter_by(assignment_id=asgn_id).all():
            a = (i.submission_user, i.submission_content)
            filenames.append(a)
    else:
        for i in AssignmentSubmission.query.filter_by(assignment_id=asgn_id, submission_user=current_user.username).all():      
            a = i.submission_content
            filenames.append(a)
    
    return render_template('view_assignment.html', id=id, asgn_id=asgn_id, isTeacher=isTeacher, 
                            assignment=assignment, filenames=filenames)

@app.route('/<id>/download_file/<filename>')
@login_required
def download_file(id, filename):

    room = Room.query.filter_by(id=id).first()
    if not room:
        flash('Invalid Request!', 'danger')
        return redirect(url_for('dashboard'))
    p = app.config['UPLOAD_FOLDER']
    p = os.path.join(p, id)
    print(id)
    file_path = os.path.join(p, filename)
    print(file_path)
    #print(os.getcwd())
    #file_path = r'C:\Users\rohin\Desktop\class_room\classroom\uploads\ThG-Yyj-Fd\pqr__ThG-Yyj-Fd_5beef229e4__default.jpg'
    return send_file(file_path, as_attachment=True, attachment_filename='')

@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/'+current_user.profile_pic)
    classes = []
    for i in current_user.classes.split(',')[:-1]:
        c = Room.query.filter_by(id=i).first()
        classes.append(c)
    return render_template('account.html', title=f'Account - {current_user.username}', classes=classes, image_file=image_file)


@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully Logged Out!', 'success')
    
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('page_not_found.html')

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('method_not_allowed.html')   