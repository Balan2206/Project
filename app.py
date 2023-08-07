from flask import Flask, render_template,flash
from jinja2 import Template
from flask import redirect,url_for,request, session
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from os import path
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager
from datetime import datetime

app=Flask(__name__)
app.secret_key = 'ragasiyam'
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///database.sqlite"
db=SQLAlchemy(app)
#db.init_app(app)

#database model
class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150), nullable=False)

    # Override get_id method to return the user_id as a string for the expected id value
    def get_id(self):   
        return str(self.user_id)


class Cart(db.Model,UserMixin):
    cart_id=db.Column(db.Integer, primary_key=True)
    product_name=db.Column(db.String)   
    product_quantity=db.Column(db.String)

    # Override get_id method to return the cart_id as a string for the expected id value
    def get_id(self):   
        return str(self.cart_id)

class Admin(db.Model,UserMixin):
    admin_id=db.Column(db.Integer, primary_key=True)
    email= db.Column(db.String, nullable=False, unique=True)
    first_name=db.Column(db.String)
    password=db.Column(db.String, nullable=False)

    # Override get_id method to return the admin_id as a string for the expected id value
    def get_id(self):   
        return str(self.admin_id)


class Categories(db.Model,UserMixin):
    category_id=db.Column(db.Integer, primary_key=True)
    type=db.Column(db.String, nullable=False)
    products=db.relationship("Product",backref="categories")

    # Override get_id method to return the category_id as a string for the expected id value
    def get_id(self):   
        return str(self.category_id)

class Product(db.Model,UserMixin):
    product_id=db.Column(db.Integer, primary_key=True)
    price=db.Column(db.Integer, nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    unit=db.Column(db.String,nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey("categories.category_id"))

    # Override get_id method to return the product_id as a string for the expected id value
    def get_id(self):   
        return str(self.product_id)


#app routes
@app.route('/select', methods=['POST','GET'])
def select():
    return render_template('selectlogin.html', user=current_user)

@app.route('/adminlogin', methods=['POST','GET'])
def adminlogin():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        admin=Admin.query.filter_by(email=email).first()
        if admin:
            if admin.password == password:
                flash('Logged in successfully as admin!', category='Success')
                login_user(admin)
                return redirect('/admin')
            else:
                flash('incorrect password! try again', category='error')
        else:
            flash('email does not exist!', category='error')

    return render_template('adminlogin.html', user=current_user)

@app.route('/userlogin',methods=['GET','POST'])
def userlogin():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        remember=request.form.get('remember')

        user = User.query.filter_by(email=email).first() #filter_by is used when we want to look in our database in a specific column or attribute
        if user: #this condition will be true only when there is such user in the database
            #in this case we need to check if the hash value of the typed in password is equal to the hash value of that respective user id in database
            if check_password_hash(user.password, password):#this function will return 1 when the hash values are equal
                flash('Logged in Successfully!', category='Success')
                login_user(user)
                if remember:
                    session['remember_me'] = True
                else:
                    session.pop('remember_me', None)

                return redirect(url_for('home'))
            
                '''
                if remember:
                    login_user(user, remember=True) #this remember attribute will remember that the user is logged in until they clear the browsing history or logout manually or refreshes the server
                    return redirect(url_for('home'))
                else:
                    login_user(user, remember=False)
                    return redirect(url_for('home'))
                '''
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('email does not exist!', category='error')

    return render_template("userlogin.html",user = current_user)

@app.route('/admin', methods=['POST','GET'])
@login_required
def admin():
    return render_template("adminhome.html", user=current_user)

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
            return redirect(url_for('userlogin'))
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
    return redirect('/select')
    

#creating database
#we will use these two lines for creating database during the development stage
app.app_context().push()
db.create_all()
#the below code checks if there is database or not if there is then it wont create any more table to the database, though we can populate the already existing tables as usual in above codes this is used after completing the app development inorder not to create any more tables by mistake
'''
if not path.exists('instance/database.sqlite'):
    app.app_context().push()
    db.create_all()
    #db.create_all(bind=None, tables=[User.__table__, Cart.__table__, Admin.__table__, Categories.__table__, Product.__table__])
    print('Database Created!')
else:
    print('Database already exists!')
'''

login_manager = LoginManager()
login_manager.login_view = 'select' #if the user is not logged in, this will redirect the user to the login page
login_manager.init_app(app) #this tells the login_manager which app we are using

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) #get() is similar to filter_by() but instead here it will by default only look for the primary key variable

    

if __name__=="__main__":
    app.run(debug=True, port=5000)