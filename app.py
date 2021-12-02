from flask import Flask, render_template, send_from_directory, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import json
import random
from datetime import datetime
from math import ceil

app = Flask(__name__)

# Config

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
database_uri = os.environ.get('DATABASE_URL')
if database_uri.startswith('postgres://'):
    database_uri = database_uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri


db = SQLAlchemy(app)


# Database models
class Bolts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128), default='')
    nomD = db.Column(db.String(8), default='')
    length = db.Column(db.Integer, default=0)
    threadL = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderID = db.Column(db.Integer, nullable=False)
    orderDate = db.Column(db.DateTime, nullable=False)
    lastName = db.Column(db.String(32), nullable=False)
    firstName = db.Column(db.String(32), nullable=False)
    emailAddress = db.Column(db.String(64), nullable=False)
    phoneNumber = db.Column(db.String(16), nullable=False)
    address = db.Column(db.JSON, nullable=False)
    delivery = db.Column(db.String(16), nullable=False)
    payment = db.Column(db.String(16), nullable=False)
    products = db.Column(db.JSON, nullable=False)


name_dict = {
        'belso_kulcsnyilasu_alacsony_hengeresfeju_csavar': 'Belső kulcsnyílású, alacsony hengeresfejű csavar',
        'belso_kulcsnyilasu_sullyesztettfeju_csavar': 'Belső kulcsnyílású, süllyesztettfejű csavar',
        'd-feju_egyenes_hornyos_csavar': 'D-fejű egyenes hornyos csavar',
        'hengeres_feju_egyenes_hornyos_csavar': 'Hengeres fejű egyenes hornyos csavar',
        'lencsefeju_egyenes_hornyos_csavar': 'Lencsefejű egyenes hornyos csavar',
        'sullyesztett_feju_kereszthornyos_csavar': 'Süllyesztett fejű kereszthornyos csavar'
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rolunk')
def about_us():
    return render_template('about_us.html')


@app.route('/kapcsolat')
def contact():
    return render_template('contact.html')


@app.route('/fizetes_szallitas')
def delivery_payment():
    return render_template('delivery_payment.html')


@app.route('/egyeb_infok')
def other_information():
    return render_template('other_information.html')


@app.route('/aszf')
def terms():
    filepath = os.path.abspath(os.getcwd()) + '/static/files'
    return send_from_directory(filepath, 'ÁSZF.pdf')


@app.route('/adatkezelesi_tajekoztato')
def data_processing():
    filepath = os.path.abspath(os.getcwd()) + '/static/files'
    return send_from_directory(filepath, 'Adatkezelési-tájékoztató.pdf')


@app.route('/csavar')
def bolt():
    typ = request.args.get('tipus')

    bolts = Bolts.query.filter_by(description=typ.replace('_', ' ')).all()
    bolts_for_tojson = [{column.name: getattr(bolt, column.name) for column in Bolts.__mapper__.columns} for bolt in bolts]

    diameters = sorted([bolt.nomD for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('nomD')], key=lambda diam : int(diam[1:]))
    lengths = [bolt.length for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('length')]
    thread_lengths = [bolt.threadL for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('threadL')]

    return render_template('product.html', typ=typ, name_dict=name_dict, bolts_for_tojson=bolts_for_tojson,\
        diameters=diameters, lengths=lengths, thread_lengths=thread_lengths)


@app.route('/kosar')
def cart():
    try:
        cart_items = json.loads(request.cookies.get('cart'))
    except TypeError:
        return render_template('empty_cart.html')

    if cart_items:
        bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()
        return render_template('cart.html', cart_items=cart_items, name_dict=name_dict, bolts_in_cart=bolts_in_cart)
    else:
        return render_template('empty_cart.html')


@app.route('/szemelyes_adatok_megadasa', methods=['POST', 'GET'])
def delivery_information():
    if request.method == 'POST':
        session['lastName'] = request.form['lastname']
        session['firstName'] = request.form['firstname']
        session['emailAddress'] = request.form['email']
        session['phoneNumber'] = request.form['phone']
        session['address'] = { 'postalCode': request.form['postal'],\
            'town': request.form['town'], 'address': request.form['address'] }
        session['delivery'] = request.form['delivery']

        return redirect('/fizetes')
    else:
        try:
            cart_items = json.loads(request.cookies.get('cart'))
        except TypeError:
            return redirect('/kosar')
        if cart_items:
            bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()
            sum_price = 0
            for bolt in bolts_in_cart:
                sum_price += cart_items[str(bolt.id)] * bolt.price
            vat = ceil(sum_price * 0.27)
            return render_template('delivery_information.html', name_dict=name_dict,\
                cart_items=cart_items, bolts_in_cart=bolts_in_cart, sum_price=sum_price, vat=vat)
        else:
            return redirect('/kosar')


@app.route('/fizetes', methods=['POST', 'GET'])
def payment():
    if request.method == 'POST':
        cart_items = json.loads(request.cookies.get('cart'))
        session['payment'] = request.form['payment']

        random.seed()
        order_id_generated = False
        existing_ids = Orders.query.with_entities(Orders.orderID)
        while(not order_id_generated):
            order_id = random.randint(1000000, 9999999)
            order_id_generated = not order_id in existing_ids
        
        session['orderID'] = order_id

        db.session.add(Orders(orderID=order_id, orderDate = datetime.now(), lastName=session['lastName'], firstName=session['firstName'],\
            emailAddress=session['emailAddress'], phoneNumber=session['phoneNumber'], address=session['address'],\
                delivery=session['delivery'], payment=session['payment'], products=cart_items))

        for cart_id, cart_qty in cart_items.items():
            in_stock = Bolts.query.get(cart_id)
            in_stock.qty = in_stock.qty - int(cart_qty)

        db.session.commit()
        return redirect('/megerosites')
    else:
        try:
            session['lastName']
        except KeyError:
            return redirect('/szemelyes_adatok_megadasa')
        return render_template('payment.html')


@app.route('/megerosites')
def confirm():
    delivery_dict = { 'delivery': 'Kiszállítás', 'personal': 'Személyes átvétel' }
    payment_dict = { 'online': 'Online fizetés bankkártyával', 'cash': 'Utánvét készpénzzel', 'card': 'Utánvét bankkártyával' }
    try:
        order_id = session['orderID']
    except KeyError:
        return redirect('/')
    last_name = session['lastName']
    first_name = session['firstName']
    email = session['emailAddress']
    phone = session['phoneNumber']
    address = session['address']
    delivery = delivery_dict[session['delivery']]
    payment = payment_dict[session['payment']]

    cart_items = json.loads(request.cookies.get('cart'))
    bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()

    session.clear()

    sum_price = 0
    for bolt in bolts_in_cart:
        sum_price += cart_items[str(bolt.id)] * bolt.price
    vat = ceil(sum_price * 0.27)

    return render_template('confirm.html', order_id=order_id, last_name=last_name, first_name= first_name, email=email, phone=phone,\
        address=address, delivery=delivery, payment=payment, cart_items=cart_items, name_dict=name_dict, bolts_in_cart=bolts_in_cart,\
            sum_price=sum_price, vat=vat)
        

if __name__ == '__main__':
    app.run()