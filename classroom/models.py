from classroom import db, login_manager, app
from flask_login import UserMixin
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default="default.jpg")
    dob = db.Column(db.Date, nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    #comma seperated class ids
    classes = db.Column(db.String(40*10))

    def get_reset_token(self, expiry_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expiry_sec)
        return s.dumps( {'user_id': self.id} ).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.dob}', '{self.profile_pic}')"

class Room(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    #unique id of class with which students join
    id = db.Column(db.String(10), unique=True, nullable=False)
    #name of the class
    name = db.Column(db.String(30), nullable=False)
    #teacher 'username'
    teacher = db.Column(db.String(20), nullable=False)
    #comma seperated students ('username')
    students = db.Column(db.String(50*10), nullable=False)

class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    #the class to which this activity belongs to
    class_id = db.Column(db.String(10), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    cnt_by = db.Column(db.String(20), nullable=False)

class Assignment(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.String(30), unique=True, nullable=False)
    class_id = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(30))
    due = db.Column(db.Date, nullable=False)
    
    
class AssignmentSubmission(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    #each students submission is added as a row
    assignment_id = db.Column(db.String(30), nullable=False)
    submission_user = db.Column(db.String(30), nullable=False)
    submission_content = db.Column(db.String(100), nullable=False)

try:
    user = User.query.filter_by(id=1).first()
except:
    db.create_all()
    pass