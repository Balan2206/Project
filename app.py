from flask import Flask, render_template,flash
from jinja2 import Template
from flask import redirect,url_for,request
#from models import User
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from os import path
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager



app=Flask(__name__)
app.secret_key = 'ragasiyam'
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///database.sqlite"
db=SQLAlchemy(app)
#db.init_app(app)

class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150), nullable=False)

    # Override get_id method to return the user_id as a string
    def get_id(self):   
        return str(self.user_id)



#from models import User

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        remember=request.form.get('remember')

        user = User.query.filter_by(email=email).first() #filter_by is used when we want to look in our database in a specific column or attribute
        if user: #this condition will be true only when there is such user in the database
            #in this case we need to check if the hash value of the typed in password is equal to the hash value of that respective user id in database
            if check_password_hash(user.password, password):#this function will return 1 when the hash values are equal
                flash('Logged in Successfully!', category='Success')
                if remember:
                    login_user(user, remember=remember) #this remember attribute will remember that the user is logged in until they clear the browsing history or logout manually or refreshes the server
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('email does not exist!', category='error')

    return render_template("login.html",user = current_user)

@app.route('/', methods=['GET','POST'])
@login_required
def home():
    return render_template("home.html",user = current_user)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email=request.form.get('email')
        firstname=request.form.get('firstname')
        password1=request.form.get('password1')
        password2=request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user: #i.e if the user already exists
            flash('Email already exists, procees with login.', category='error')
            return redirect(url_for('login'))
        else:
            if len(email) < 4:
                flash('email must be greater than 3 characters!', category='error')
            elif len(firstname) < 2:
                flash('firstname must be greater than 1 character!', category='error')
            elif password1 != password2:
                flash('the passwords doesnt match', category='error')
            elif len(password1) < 7:
                flash('the password is too short(minimum 7 characters)', category='error')
            else:
            #add user to database
                new_user = User(email=email, first_name=firstname, password=generate_password_hash(password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Account created!', category='Success')
                login_user(new_user, remember=True)
                return redirect(url_for('home'))        

    
    return render_template('signup.html', user = current_user)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')
    

#creating database
if not path.exists('instance/database.sqlite'):
    app.app_context().push()
    db.create_all()
    print('Database Created!')
else:
    print('Database already exists!')

login_manager = LoginManager()
login_manager.login_view = 'login' #if the user is not logged in, this will redirect the user to the login page
login_manager.init_app(app) #this tells the login_manager which app we are using

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) #get() is similar to filter_by() but instead here it will by default only look for the primary key variable

    

if __name__=="__main__":
    app.run(debug=True, port=5000)