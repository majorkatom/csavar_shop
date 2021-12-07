from flask import Flask, render_template, send_from_directory, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
import json
import random
from datetime import datetime
from math import ceil


app = Flask(__name__)


# Konfig

# ezek a heroku környezethez vannak
# helyi futtatáshoz manuálisan állíthatjuk be a SECRET_KEY-t és az adatbázis szerver címét
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # a session sütihez (Flask feature) kell
database_uri = os.environ.get('DATABASE_URL')
if database_uri.startswith('postgres://'):
    database_uri = database_uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri  # adatbázis elérése


db = SQLAlchemy(app)


# Tábla modellek az adatbáisba

# termékekhez (csavarokhoz)
class Bolts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128), default='')
    nomD = db.Column(db.String(8), default='')
    length = db.Column(db.Integer, default=0)
    threadL = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False)


# a rendelésekhez
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


# a html szövegrészek dinamikus kitöltéséhez
name_dict = {
        'belso_kulcsnyilasu_alacsony_hengeresfeju_csavar': 'Belső kulcsnyílású, alacsony hengeresfejű csavar',
        'belso_kulcsnyilasu_sullyesztettfeju_csavar': 'Belső kulcsnyílású, süllyesztettfejű csavar',
        'd-feju_egyenes_hornyos_csavar': 'D-fejű egyenes hornyos csavar',
        'hengeres_feju_egyenes_hornyos_csavar': 'Hengeres fejű egyenes hornyos csavar',
        'lencsefeju_egyenes_hornyos_csavar': 'Lencsefejű egyenes hornyos csavar',
        'sullyesztett_feju_kereszthornyos_csavar': 'Süllyesztett fejű kereszthornyos csavar'
}


# oldalak

# főoldal
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
    return send_from_directory(filepath, 'ÁSZF.pdf')  # pdf-ként adjuk oda


@app.route('/adatkezelesi_tajekoztato')
def data_processing():
    filepath = os.path.abspath(os.getcwd()) + '/static/files'
    return send_from_directory(filepath, 'Adatkezelési-tájékoztató.pdf')  # pdf-ként adjuk oda


@app.route('/csavar')
def bolt():
    typ = request.args.get('tipus')  # csavar típusa

    bolts = Bolts.query.filter_by(description=typ.replace('_', ' ')).all()  # adott típusba tartozó csavarok lekérése
    bolts_for_tojson = [{column.name: getattr(bolt, column.name) for column in Bolts.__mapper__.columns} for bolt in bolts]  # JSON serializable-lé tesszük, hogy odaadhassuk a JavaScriptnek

    diameters = sorted([bolt.nomD for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('nomD')], key=lambda diam : int(diam[1:]))  # az egyedi átmérők, saját sorbarendezéssel
    lengths = [bolt.length for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('length')]  # egyedi hosszak
    thread_lengths = [bolt.threadL for bolt in Bolts.query.filter_by(description=typ.replace('_', ' ')).distinct('threadL')]  # egyedi menethosszak

    return render_template('product.html', typ=typ, name_dict=name_dict, bolts_for_tojson=bolts_for_tojson,\
        diameters=diameters, lengths=lengths, thread_lengths=thread_lengths)  # paraméterek a html template csavartípusnak megfelelő kitöltéséhez


@app.route('/kosar')
def cart():
    try:
        cart_items = json.loads(request.cookies.get('cart'))  # ellenőrizzük, hogy létezik-e a süti
    except TypeError:
        return render_template('empty_cart.html')  # ha nem, akkor az üres kosár oldalt adjuk oda

    if cart_items:  # megnézzük, hogy a sütiben vannak-e termékek
        bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()  # a sütiben tárolt id-k szerint lekérjük a csavarokat az adatbázisból
        return render_template('cart.html', cart_items=cart_items, name_dict=name_dict, bolts_in_cart=bolts_in_cart)  # paraméterek a kosár html feltöltéséhez
    else:  # ha üres volt a süti, az üres kosár oldalt adjuk oda
        return render_template('empty_cart.html')


@app.route('/szemelyes_adatok_megadasa', methods=['POST', 'GET'])
def delivery_information():
    if request.method == 'POST':  # ha a kliens küldi az adatokat
        # eltároljuk az adatokat a session sütiben (titkosított süti, flaskből importálható)
        session['lastName'] = request.form['lastname']
        session['firstName'] = request.form['firstname']
        session['emailAddress'] = request.form['email']
        session['phoneNumber'] = request.form['phone']
        session['address'] = { 'postalCode': request.form['postal'],\
            'town': request.form['town'], 'address': request.form['address'] }
        session['delivery'] = request.form['delivery']

        return redirect('/fizetes')  # ezután a fizetés oldalra irányítunk
    else:  # GET request
        try:
            cart_items = json.loads(request.cookies.get('cart'))  # megnézzük, hogy létezik-e a kosár süti
        except TypeError:
            return redirect('/kosar')  # ha nem visszairányítunk a kosár oldalra (ami üres kosarat fog mutatni)
        if cart_items:  # megnézzük, vannak-e termékek a kosár sütiben
            bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()  # lekérjük a kosárban lévő csavarokat
            sum_price = 0
            for bolt in bolts_in_cart:
                sum_price += cart_items[str(bolt.id)] * bolt.price  # összes árat számolunk
            vat = ceil(sum_price * 0.27)  # ÁFa-t számolunk
            return render_template('delivery_information.html', name_dict=name_dict,\
                cart_items=cart_items, bolts_in_cart=bolts_in_cart, sum_price=sum_price, vat=vat)  # paraméterek a dinamikus kitöltéshez
        else:
            return redirect('/kosar')  # ha üres a kosár süti, a kosár oldalra irányítunk (ami üres kosarat fog mutatni)


@app.route('/fizetes', methods=['POST', 'GET'])
def payment():
    if request.method == 'POST':  # ha a felhasználó elküldte a megrendelést
        # a rendelési táblához még szükséges sütiket eltároljuk a session sütibe, hogy a megerősítésnél még ki tudjuk őket jelezni
        cart_items = json.loads(request.cookies.get('cart'))
        session['payment'] = request.form['payment']
        
        # rendelési azonosítót generálunk
        random.seed()
        order_id_generated = False
        existing_ids = Orders.query.with_entities(Orders.orderID)
        while(not order_id_generated):
            order_id = random.randint(1000000, 9999999)
            order_id_generated = not order_id in existing_ids
        
        session['orderID'] = order_id
        
        # elmentjük a rendelési táblába a rendelést
        db.session.add(Orders(orderID=order_id, orderDate = datetime.now(), lastName=session['lastName'], firstName=session['firstName'],\
            emailAddress=session['emailAddress'], phoneNumber=session['phoneNumber'], address=session['address'],\
                delivery=session['delivery'], payment=session['payment'], products=cart_items))
        
        # a csavar táblában csökkentjük a megfelelő termékek mennyiségét
        for cart_id, cart_qty in cart_items.items():
            in_stock = Bolts.query.get(cart_id)
            in_stock.qty = in_stock.qty - int(cart_qty)

        db.session.commit()  # commitoljuk az adatbázis változásokat
        return redirect('/megerosites')  # átirányítunk a megerősítésre
    else:  # GET request
        try:
            session['lastName']  # megnézzük, hogy megkaptuk-e már a rendelő adatait
        except KeyError:
            return redirect('/szemelyes_adatok_megadasa')  # ha nem, visszairányítunk
        return render_template('payment.html')


@app.route('/megerosites')
def confirm():
    # dictionary-k a dinamikus kitöltéshez
    delivery_dict = { 'delivery': 'Kiszállítás', 'personal': 'Személyes átvétel' }
    payment_dict = { 'online': 'Online fizetés bankkártyával', 'cash': 'Utánvét készpénzzel', 'card': 'Utánvét bankkártyával' }

    try:
        order_id = session['orderID']  # megnézzük, hogy van-e befejezett rendelés
    except KeyError:
        return redirect('/')  # ha nincs, a főoldalra irányítunk
    
    # változók a dinamikus kitöltéshez
    last_name = session['lastName']
    first_name = session['firstName']
    email = session['emailAddress']
    phone = session['phoneNumber']
    address = session['address']
    delivery = delivery_dict[session['delivery']]
    payment = payment_dict[session['payment']]

    cart_items = json.loads(request.cookies.get('cart'))
    bolts_in_cart = Bolts.query.filter(Bolts.id.in_(cart_items.keys())).all()

    session.clear()  # miután változókba mentettük a szükséges adatokat, töröljük a session sütit

    sum_price = 0
    for bolt in bolts_in_cart:
        sum_price += cart_items[str(bolt.id)] * bolt.price
    vat = ceil(sum_price * 0.27)

    return render_template('confirm.html', order_id=order_id, last_name=last_name, first_name= first_name, email=email, phone=phone,\
        address=address, delivery=delivery, payment=payment, cart_items=cart_items, name_dict=name_dict, bolts_in_cart=bolts_in_cart,\
            sum_price=sum_price, vat=vat)  # paraméterek a dinamikus kitöltéshe
        

if __name__ == '__main__':
    app.run()