import datetime
import os.path
import json

from flask import Flask, request, flash, redirect, render_template, session, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, select
from sqlalchemy.sql import text
from sqlalchemy.orm import load_only
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, InputRequired
from wtforms.fields import DateTimeLocalField
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, template_folder='templates')

CORS = (app)

#config uri database -- por causa dos erros de CRUD no db
basedir = os.path.abspath(os.path.dirname(__file__))

# some config of flask, maybe put on another document
# configs sqlite to sqlalchemy connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'bakery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'um-nome-seguro'
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)

# flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Models db
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(150))

    # set hash for password and verify
    @property
    def password(self):
        raise AttributeError("password not readable!")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    # relationship
    orders = db.relationship('Orders', backref='customer')

    def __str__(self):
        return self.name

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=True, unique=True)

    order_details = db.relationship('Order_details', backref='product')

    def __str__(self):
        return self.name

class Order_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orders_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    delivery_date = db.Column(db.DateTime, default=datetime.now())
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    delivery = db.Column(db.Boolean, nullable=False)
    warning = db.Column(db.String(100))

    order_details = db.relationship('Order_details', backref='orders')

# rotas
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

# form login flaskwtf
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user: 
            # check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Logged!")
                return redirect("/")
            else:
                flash("Wrong password!")
        else: 
            flash("Username not registered!")
    return render_template("login.html", form=form)

#segue construção do register
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('confirmation')])
    confirmation = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None:
            #hash password
            hashing =  generate_password_hash(form.password.data)
            insert = Users(username=form.username.data, password_hash=hashing)
            db.session.add(insert)
            db.session.commit()
            flash("Registered!")
            return redirect("/login")
        else:
            flash("Please select another username.")
            # can be incremented to show message if password and confirmation do not match

    form.username.data = ''
    form.password.data = ''

    return render_template("register.html", form=form)

# register orders paths

class OrdersForm(FlaskForm):
    customer = SelectField("Cliente", choices=[])
    product = SelectField("Produto", choices=[])
    quantity = IntegerField("Quantidade")
    ready = DateTimeLocalField("Horário", validators=[InputRequired()], default=datetime.today(), format='%Y-%m-%dT%H:%M') #there was a problem to submit the form caused by the previuos way that I inserted de required field (as DataRequired) and the datetime format being incompatible
    delivery = BooleanField("Para entrega:")
    notes = StringField("Observações")
    submit = SubmitField("Cadastrar")


@app.route("/addorder", methods=['GET', 'POST'])
def addorder():
    form = OrdersForm()
    form.customer.choices = [("")] + [(customer.name) for customer in Product.query.with_entities(Customer.name).all()]
    form.product.choices = [("")] + [(product.name) for product in Product.query.with_entities(Product.name).all()]
    if form.validate_on_submit():
        flash("Pedido cadastrado!")
        return redirect("/addorder")
    else:
        print(form.errors)

    return render_template("addorder.html", form=form)

# add route to receive json and show order details
@app.route("/orderinfo", methods=['POST'])
def orderinfo():

    #search and insert
    data = request.get_json()
    customer = data.get('customer')
    delivery_date_str = data.get('ready') 
    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%dT%H:%M')
    delivery_str = data.get('delivery')
    if delivery_str == 'y':
        delivery = True
    else:
        delivery = False
    notes = data.get('notes')
    produtos = data.get('produtos')
    buscar = db.session.execute(select(Customer.id).where(Customer.name == customer)).first()[0]
    hora = datetime.now()
    add_order = Orders(order_date=hora, delivery_date=delivery_date, customer_id=buscar, delivery=delivery, warning=notes)
    db.session.add(add_order)
    db.session.commit()
    last_id = Orders.query.order_by(Orders.order_date.desc()).first().id    #db.session.execute(text('SELECT id from orders order by order_date DESC LIMIT 1;'))  
    for row in produtos:
        item = row['product']
        quant = row['quantity']
        #search product id
        id_buscado = db.session.execute(select(Product.id).where(Product.name == item))
        passar_id = id_buscado.first()[0]
        #updade da order_details
        add_details = Order_details(orders_id=last_id, product_id=passar_id, quantity=quant)
        db.session.add(add_details)

    db.session.commit()
    return data
        
# add customer class and route
class AddCustomerForm(FlaskForm):
    customer = StringField("Adicionar cliente", validators=[DataRequired()])
    submit = SubmitField("Confirmar")

@app.route("/customer", methods=['GET', 'POST'])
def customer():
    form = AddCustomerForm()
    if form.validate_on_submit():
        search = Customer.query.filter_by(name=form.customer.data).first()
        if search:
            flash("Cliente já cadastrado!")
        else:
            add = Customer(name=form.customer.data)
            db.session.add(add)
            db.session.commit()
            flash("Cadastrado!")
            return redirect("/customer")
    
    # search list of customers
    customers = Customer.query.all()
 
    return render_template("customer.html", form=form, customers=customers)

# delete customer
@app.route('/delete/<int:id>')
def delete(id):
    form = AddCustomerForm()
    customers = Customer.query.all()
    customer_to_delete = Customer.query.get(id)
    # flag de ativo !
    try:
        db.session.delete(customer_to_delete)
        db.session.commit()
        flash("Cliente removido.")
        return redirect("/customer")

    except:
        flash("Cliente não removido. Houve um problema.")
        db.session.rollback()
        return render_template("customer.html", form=form, customers=customers)

# add product class and route
class AddProductForm(FlaskForm):
    product_f = StringField("Adicionar produto", validators=[DataRequired()])
    submit = SubmitField("Confirmar")

@app.route("/product", methods=['GET', 'POST'])
def product():
    form = AddProductForm()
    if form.validate_on_submit():
        search = Product.query.filter_by(name=form.product_f.data).first()
        if search:
            flash("Produto já cadastrado!")
        else:
            add = Product(name=form.product_f.data)
            db.session.add(add)
            db.session.commit()
            flash("Cadastrado!")
            return redirect("/product")
    
    # search list of customers
    products = Product.query.all()
 
    return render_template("product.html", form=form, products=products)

# delete product
@app.route('/rmvproduct/<int:id>')
def rmvproduct(id):
    form = AddProductForm()
    products = Product.query.all()
    product_to_delete = Product.query.get(id)
    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        flash("Produto removido.")
        return redirect("/product")

    except:
        flash("Produto não removido. Houve um problema.")
        db.session.rollback()
        return render_template("product.html", form=form, products=products)

# rota lista de encomendas
@app.route("/orderlist", methods=['GET', 'POST'])
def orderlist():
    todays_date = datetime.now()
    orders = db.session.execute(
        select(
            Orders.id,
            Orders.delivery_date,
            Orders.warning,
            Orders.delivery,
            Customer.name
        )
        .join(Customer)
        .where(Orders.delivery_date >= todays_date)
        .order_by(Orders.delivery_date)
    )
    products = db.session.execute(
        select(
            Order_details.orders_id,
            Order_details.product_id,
            Order_details.quantity,
            Product.name
        )
        .join(Product)
        .join(Orders)
        .where(Orders.delivery_date >= todays_date)
        .where(Product.id == Order_details.product_id)
        .order_by(Orders.delivery_date)
    )

    grouped_products = {}
    for product in products:
        if product.orders_id not in grouped_products:
            grouped_products[product.orders_id] = []
        grouped_products[product.orders_id].append(product)

    return render_template("orderlist.html", orders=orders, grouped_products=grouped_products)


# logout route 
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out!")
    return redirect("/login")

if __name__ == '__main__':
	    app.run(debug = True)