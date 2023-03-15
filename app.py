from flask import Flask,render_template,flash,redirect,url_for,request
from addproduct import AddproductForm
from checkout import CheckoutForm
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from login import LoginForm
from flask_login import LoginManager,UserMixin, current_user,login_user,logout_user,login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY']="de9e5b220476ba0aba47040eb9b2fea9"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///chasmaghar.db'
bcrypt= Bcrypt(app)
login_mananger = LoginManager(app)
login_mananger.login_view = 'adminlogin'
login_mananger.login_message_category="info"

db=SQLAlchemy(app)

class Product(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    name =db.Column(db.String(20),nullable=False)
    detail =db.Column(db.String(500))
    price =db.Column(db.Integer,nullable=False)
    discounted_price =db.Column(db.Integer,nullable=False,default=0)
    has_discount=db.Column(db.Boolean,default=False)
    images =db.Column(db.String(500))

    def __repr__(self):
        return f"Post({self.name},{self.price},{self.images})"


class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(20),nullable=False)
    lastname = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(20),nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    streetaddress = db.Column(db.String(40),nullable=False)
    city = db.Column(db.String(20),nullable=False)
    country = db.Column(db.String(20),nullable=False)
    product = db.Column(db.Integer,db.ForeignKey('product.id'),nullable=False)
    def __repr__(self):
        return f"Order({self.id}{self.firstname},{self.email},{self.phone},{self.product})"

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(20),nullable=False)
    lastname = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(50),nullable=False)
    isSuperAdmin = db.Column(db.Boolean,default=False)
    def __repr__(self):
        return f"Order({self.id}{self.firstname},{self.email},{self.phone},{self.product})"


@app.route("/")
@app.route("/home")
def home():
    newproducts = Product.query.all()
    print(newproducts)
    return render_template("index.html",products=newproducts)

@app.route("/detail/<int:id>")
def detail(id):
    product = db.session.query(Product).get(id)
    print(product)
    return render_template("detail.html",product=product)


@app.route("/checkout/<int:id>",methods=['GET','POST'])
def checkout(id):
    product = db.session.query(Product).get(id)
    form = CheckoutForm()
    if form.validate_on_submit():
        flash("Order Successful",category="success")
        order = Order(firstname = request.form["firstname"],lastname=request.form["lastname"],email=request.form["email"],phone=request.form["phone"],streetaddress=request.form["streetaddress"],city=request.form["city"],country=request.form["country"],product=product.id)
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("checkoutform.html",form=form,product=product)



def saveProductImage(form_picture,file_name):
    print("product image")
    _,f_ext=os.path.splitext(form_picture.filename)  
           
    random_id = uuid.uuid4()  
    picture=random_id+f_ext
    picture_path = os.path.join(app.root_path,"static/images/products",picture)
    form_picture.save(picture_path)
    return f"../static/images/products/{picture}"

@app.route("/addproduct",methods=['GET','POST'])
@login_required
def addproduct():
    products = Product.query.all()
    print(products)
    form=AddproductForm()
    if form.validate_on_submit():
        if form.productImage.data:  
            picture_file = saveProductImage(form.productImage.data,request.form["name"])
            flash("Product Added Successful",category="success")
            product = Product(name = request.form["name"],detail=request.form["description"],price=request.form["price"],discounted_price=request.form["discountPrice"],has_discount=form.checkbox.data,images=picture_file)
            db.session.add(product)
            db.session.commit()
            return redirect(url_for("adminViewProducts"))
        else:
            flash("Product Could not be added",category="danger")
    return render_template("addproductform.html",form=form,products=products)

@app.route("/viewallorders")
@login_required
def viewAllOrders():
    
    orders = Order.query.all()
    print(orders)
    return render_template("viewallorders.html",orders=orders)

@app.route("/adminviewproduct")
@login_required
def adminViewProducts():
    products = Product.query.all()
    print(products)
    return render_template("adminviewproduct.html",products=products)

@app.route("/delete/<int:id>")
def delete(id):
    print(id)
    product = Product.query.filter_by(id=id).first()
    file_path_str = product.images.replace('../', '')
    if os.path.exists(file_path_str):
        os.remove(file_path_str)    
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('adminViewProducts'))

@app.route("/adminlogin",methods=['GET','POST'])
def adminlogin():
    if current_user.is_authenticated:
        return redirect(url_for('adminViewProducts'))
    else:
        form=LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user,remember = True)
                return redirect(url_for('adminViewProducts'))
            else:
                flash('Invalid Credientials',category="danger")
    return render_template("adminlogin.html",title = "Login",form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('adminlogin'))

@login_mananger.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__=="__main__":
    app.run(debug=True)