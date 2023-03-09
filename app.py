from flask import Flask,render_template,flash,redirect,url_for,request
from addproduct import AddproductForm
from checkout import CheckoutForm
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY']="de9e5b220476ba0aba47040eb9b2fea9"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///chasmaghar.db'

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
    picture=file_name+f_ext
    picture_path = os.path.join(app.root_path,"static/images/products",picture)
    form_picture.save(picture_path)
    return f"../static/images/products/{picture}"

@app.route("/addproduct",methods=['GET','POST'])
def addproduct():
    products = Product.query.all()
    print(products)
    form=AddproductForm()
    if form.validate_on_submit():
        if form.productImage.data:
            print("k ho k ho")
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
def viewAllOrders():
    
    orders = Order.query.all()
    print(orders)
    return render_template("viewallorders.html",orders=orders)

@app.route("/adminviewproduct")
def adminViewProducts():
    products = Product.query.all()
    print(products)
    return render_template("adminviewproduct.html",products=products)

@app.route("/delete/<int:id>")
def delete(id):
    print(id)
    product = Product.query.filter_by(id=id).first()
    print(product)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('adminViewProducts'))



if __name__=="__main__":
    app.run(debug=True)