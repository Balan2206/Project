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
    cart_id=db.Column(db.Integer, primary_key=True, nullable=False)
    quantity=db.Column(db.Integer, nullable=False, default=1)
    product=db.relationship("Product", backref="cart")
    product_name=db.Column(db.String, db.ForeignKey("product.product_name"))   
    category_id=db.Column(db.Integer, db.ForeignKey("categories.category_id"))
    user_id=db.Column(db.Integer, db.ForeignKey("user.user_id"))

    '''
    price=db.Column(db.Integer, db.ForeignKey("product.price"))
    type=db.Column(db.String, db.ForeignKey("categories.type"))
    '''

    # Override get_id method to return the cart_id as a string for the expected id value
    def get_id(self):   
        return str(self.cart_id)

class Admin(db.Model,UserMixin):
    admin_id=db.Column(db.Integer, primary_key=True, nullable=False)
    email= db.Column(db.String, nullable=False, unique=True)
    first_name=db.Column(db.String)
    password=db.Column(db.String, nullable=False)

    # Override get_id method to return the admin_id as a string for the expected id value
    def get_id(self):   
        return str(self.admin_id)


class Categories(db.Model,UserMixin):
    category_id=db.Column(db.Integer, primary_key=True, nullable=False)
    type=db.Column(db.String, nullable=False)
    #product_id=db.Column(db.Integer, nullable= False)
    products=db.relationship("Product")

    # Override get_id method to return the category_id as a string for the expected id value
    def get_id(self):   
        return str(self.category_id)

class Product(db.Model,UserMixin):
    product_id=db.Column(db.Integer, primary_key=True, nullable=False)
    product_name=db.Column(db.String,nullable=False)
    price=db.Column(db.Integer, nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    unit=db.Column(db.String,nullable=False)
    category_id=db.Column(db.Integer, db.ForeignKey("categories.category_id"))
    category=db.relationship('Categories')

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
        remember=request.form.get('remember')

        admin=Admin.query.filter_by(email=email).first()
        if admin:
            if admin.password == password:
                flash('Logged in successfully as admin!', category='Success')
                login_user(admin)
                if remember:
                    session['remember_me'] = True
                else:
                    session.pop('remember_me', None)
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
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('email does not exist!', category='error')

    return render_template("userlogin.html",user = current_user)

@app.route('/admin',methods=['POST','GET'])
@login_required
def adminselect():
    '''
    if request.method=='POST':
        x=request.form.get('value')
        if x=='add':
            return redirect('/adminadd')
        elif x=='delete':
            return redirect('/admindelete')
        else:
            flash('Enter a valid command (either add or delete)')
     '''   
    c=Categories.query.all()
    #print('-----', c)    
    return render_template('adminselect.html',user=current_user,c=c)

#products add route
@app.route('/adminadd', methods=['POST','GET'])
@login_required
def addproduct():
    if request.method=='POST':
        category_id=request.form.get('category_id')
        product=request.form.get('product')
        price=request.form.get('price')
        quantity=request.form.get('quantity')
        unit=request.form.get('unit')

        #c=Categories.query.filter_by(type=category)
        #category_id=c.category_id

        '''#Get the latest category_id from the database
        latest_category = Categories.query.order_by(Categories.category_id.desc()).first()
        if latest_category:
            category_id = latest_category.category_id + 1
        else:
            category_id = 1
        '''

        '''
        flag=0
        for i in Categories.type:
            if category==i:
                category_id=Categories.category_id
                flag=1
            else:
                continue
        
        if flag:
            p = Product( 
            product_name = product,
            price = price,
            quantity = quantity,
            unit = unit,
            category_id=category_id
            )
            db.session.add(p)

            flag=0
        else:
            c = Categories(
                type = category
                )
        
            p = Product( 
                product_name = product,
                price = price,
                quantity = quantity,
                unit = unit
                )
        '''
        
        p = Product( 
            product_name = product,
            price = price,
            quantity = quantity,
            unit = unit,
            category_id=category_id
        )
        #db.session.add(c)
        db.session.add(p)

        #p.category_id=category_id
        #db.session.add(c)
        #db.session.add(p)
        db.session.commit()
        flash('Added the product to database!')
    else:
        flash('Enter the names before clicking add!')
    x=Categories.query.all()
    return render_template('productadd.html',user=current_user,x=x)

@app.route('/addcategory',methods=['GET','POST'])
@login_required
def addcategory():
    if request.method=='POST':
        name=request.form.get('category')
        y=Categories.query.all()
        flag=0
        for i in y:
            if i.type==name:
                flash('this category already exists')
                flag=1
        if not flag:
            c = Categories(type=name)
            db.session.add(c)
            db.session.commit()
            flash(f'{name} category has been successfully added to the database!')
    return render_template('addcategory.html',user=current_user)

''' admindelete route
@app.route('/admindelete', methods=['POST','GET'])
@login_required
def deletecategory():
    if request.method=='POST':
        category_id=request.form.get('category_id')
        product=request.form.get('product')


        c = Categories.query.get(category_id)
        p = Product.query.filter_by(product_name=product).first()

        db.session.delete(c)
        db.session.delete(p)
        db.session.commit()
        flash('Category and Product deleted successfully!', category='Success')
    else:
        flash('Enter the names before clicking delete!', category='error')
    return render_template('admindelete.html',user=current_user)
'''

@app.route('/categories')
@login_required
def categories():
    all_c=Categories.query.all()
    #all_p=Product.query.all()
    #all_data=zip(all_c,all_p)
    return render_template("categories.html", all_c=all_c,user=current_user)

@app.route('/products')
@login_required
def products():
    all_p=Product.query.all()
    total_price=sum(product.price*product.quantity for product in all_p)
    print('-----',total_price)
    #all_p=Product.query.all()
    #all_data=zip(all_c,all_p)
    return render_template("products.html", all_p=all_p, total_price=total_price, user=current_user)

@app.route('/', methods=['GET','POST'])
@login_required
def home():
    selected_category = None
    search_query=request.args.get('search_query')

    if request.method=='POST':
        selected_category_id = request.form.get('category_id')
        selected_product = request.form.get('product_name')
        selected_product_id=request.form.get('product_id')
        quantity=request.form.get('quantity')
        selected_category = Categories.query.get(selected_category_id)
        #selected_quantity=int(request.form.get('quantity'))
        #adding the product to cart
        selected_product_obj = Product.query.filter_by(product_id=selected_product_id)
        if selected_product_obj:
            selected_product_id=selected_product_id
            #new_cart_category = Categories.query.get(selected_category_id)
            #new_cart_product = Product.query.get(selected_product)
            new_cart_entry = Cart(
                product_name=selected_product,
                category_id=selected_category_id,
                user_id=current_user.user_id,
                quantity=quantity
                )
            db.session.add(new_cart_entry)
            db.session.commit()
            flash('Product successfully added to the cart!', category='Success')
        else:
            flash('no product was selected!')

    if search_query:
        products=Product.query.filter_by(product_name=search_query).all()
    else:
        products= Product.query.all()

    all_c=Categories.query.all()
    all_p=Product.query.all()
    return render_template("home.html", all_c=all_c, all_p=all_p, user = current_user, selected_category=selected_category)

@app.route('/search', methods=['POST','GET'])
def search():

    search_query=request.args.get('search_query')

    #if request.method=='POST':

    if search_query:
        products=Product.query.filter_by(product_name=search_query).all()
    else:
        products= Product.query.all()

    all_p=Product.query.filter_by(product_name=search_query).all()
    all_c=Categories.query.all()
    all_data=zip(all_c,all_p)
    return render_template('search.html', user=current_user, all_data=all_data)

@app.route('/cart', methods=['POST','GET'])
@login_required
def cart():
    user_cart_entries=Cart.query.filter_by(user_id=current_user.user_id).all()
    #product_price=Product.query.filter_by(product_name=user_cart_entries.product_name).first()
    product_prices = []  # Create an empty list to store product prices
    quantities=[]
    for cart_entry in user_cart_entries:
        product = Product.query.filter_by(product_name=cart_entry.product_name).first()
        if product:
            product_prices.append(product.price)
            quantities.append(product.quantity)
        else:
            #product_prices.append(None) 
            product_prices.append(0) 
            quantities.append(0)
    #all_cr=Cart.query.all()
    total_price = sum(price * quantity for price, quantity in zip(product_prices, quantities))
    total=zip(user_cart_entries,product_prices)
   
    
    return render_template("cart.html",user_cart_entries=user_cart_entries, product=product,product_prices=product_prices, total=total,total_price=total_price, user=current_user)

@app.route('/cartdelete', methods=['POST','GET'])
@login_required
def cartdelete():
    if request.method=='POST':
        cart_id=request.form.get('cart_id')
        cart_entry = Cart.query.get(cart_id)  # Retrieve the cart entry using the ID
        if cart_entry:
            db.session.delete(cart_entry)  # Delete the cart entry from the database
            db.session.commit()
            flash('Item removed from cart successfully!', category='Success')
        else:
            flash('Cart entry not found!', category='error')

    return redirect('/cart')  # Redirect back to the cart page

@app.route('/categorydelete', methods=['POST','GET'])
@login_required
def categorydelete():
    if request.method=='POST':
        category_id=request.form.get('category_id')
        category_entry = Categories.query.get(category_id)  # Retrieve the cart entry using the ID
        if category_entry:
            db.session.delete(category_entry)  # Delete the cart entry from the database
            db.session.commit()
            flash(f'{category_entry.type} category removed from database successfully!', category='Success')
        else:
            flash('category entry not found!', category='error')

    return redirect('/categories')

@app.route('/productdelete', methods=['POST','GET'])
@login_required
def productdelete():
    if request.method=='POST':
        product_id=request.form.get('product_id')
        product_entry = Product.query.get(product_id)  # Retrieve the cart entry using the ID
        if product_entry:
            db.session.delete(product_entry)  # Delete the cart entry from the database
            db.session.commit()
            flash('product deleted from database successfully!', category='Success')
        else:
            flash('product entry not found!', category='error')

    return redirect('/products')

@app.route('/productedit', methods=['POST','GET'])
@login_required
def productedit():
    if request.method=='POST':
        product_entry=None #clears all the previous values for this variable
        product_name=request.form.get('new_product')
        product_id=request.form.get('product_id')
        product_entry = Product.query.get(product_id) 
        if product_entry:
            product_entry.product_name=product_name  
            db.session.commit()
            flash('product name updated', category='Success')

    return redirect('/products')

@app.route('/priceedit', methods=['POST','GET'])
@login_required
def priceedit():
    if request.method=='POST':
        product_entry=None #clears all the previous values for this variable
        price=request.form.get('new_price')
        product_id=request.form.get('product_id')
        product_entry = Product.query.get(product_id) 
        if product_entry:
            product_entry.price=price
            db.session.commit()
            flash('product name updated', category='Success')

    return redirect('/products')

@app.route('/quantityedit', methods=['POST','GET'])
@login_required
def quantityedit():
    if request.method=='POST':
        product_entry=None #clears all the previous values for this variable
        quantity=request.form.get('new_quantity')
        product_id=request.form.get('product_id')
        product_entry = Product.query.get(product_id) 
        if product_entry:
            product_entry.quantity=quantity
            db.session.commit()
            flash('product name updated', category='Success')

    return redirect('/products')

@app.route('/unitedit', methods=['POST','GET'])
@login_required
def unitedit():
    if request.method=='POST':
        product_entry=None #clears all the previous values for this variable
        unit=request.form.get('new_unit')
        product_id=request.form.get('product_id')
        product_entry = Product.query.get(product_id) 
        if product_entry:
            product_entry.unit=unit
            db.session.commit()
            flash('product name updated', category='Success')

    return redirect('/products')

@app.route('/categoryedit', methods=['POST','GET'])
@login_required
def categoryedit():
    if request.method=='POST':
        category_entry=None #clears all the previous values for this variable
        category_name=request.form.get('new_category')
        category_id=request.form.get('category_id')
        category_entry = Categories.query.get(category_id)  
        if category_entry:
            category_entry.type=category_name 
            db.session.commit()
            flash('category name updated', category='Success')
        #print('----',category_name)
    return redirect('/categories')

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
    
@app.route('/buy',methods=['POST','GET'])
@login_required
def buy():
    flash('Order placed successfully!')
    return redirect('/')

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