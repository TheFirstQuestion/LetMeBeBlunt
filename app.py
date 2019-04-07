from flask import Flask, render_template, redirect, url_for, g, request, make_response
import sqlite3
import payment
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def main():
    if overEighteen():
        return render_template('index.html')
    else:
        return redirect(url_for("ageGate"))


@app.route("/categories")
def categories():
    if overEighteen():
        return render_template('categories.html')
    else:
        return redirect(url_for("ageGate"))


@app.route("/education")
def education():
    if overEighteen():
        return render_template('education.html', data=getArticles())
    else:
        return redirect(url_for("ageGate"))


@app.route("/us")
def us():
    if overEighteen():
        return render_template('us.html')
    else:
        return redirect(url_for("ageGate"))


@app.route("/privacy")
def privacy():
    if overEighteen():
        return render_template('privacy.html')
    else:
        return redirect(url_for("ageGate"))


@app.route("/terms")
def terms():
    if overEighteen():
        return render_template('terms.html')
    else:
        return redirect(url_for("ageGate"))


@app.route("/disclaimer")
def disclaimer():
    if overEighteen():
        return render_template('disclaimer.html')
    else:
        return redirect(url_for("ageGate"))


@app.route('/category/<cat>', methods=['GET'])
def renderCategory(cat):
    return render_template("category.html", data=getCategory(cat + "/"), cat=cat)


@app.route('/product/<pro>', methods=['GET'])
def renderProduct(pro):
    return render_template("product.html", x=getProduct(pro)[0], pro=pro)


@app.route("/age-gate")
def ageGate():
    boo = request.cookies.get('ofAge')
    if boo is None:
        return render_template('age-gate.html')
    else:
        return eighteen()


@app.route("/18")
def eighteen():
    return render_template("18.html")


@app.route("/agecheck", methods = ["POST", "GET"])
def agecheck():
    if request.method == 'POST':
        dob = request.form['myDate']
        if (datetime.now() - datetime.strptime(dob, '%Y-%m-%d')).days > 18*365:
            resp = make_response(render_template("index.html"))
            resp.set_cookie('ofAge', "true")
        else:
            resp = make_response(render_template("18.html"))
            resp.set_cookie('ofAge', "false")

    return resp


def overEighteen():
    boo = request.cookies.get('ofAge')
    try:
        if "true" in boo:
            return True
        else:
            return False
    except Exception:
        return False


@app.route('/cart')
def cart():
    name = request.args.get('item', None)
    rem = request.args.get('rem', None)
    items = request.cookies.get('cartItems')
    if items is None or len(items) == 0:
        items = []
    else:
        items = items.split("BREAK")
    # Add an item
    if name is not None:
        items.append(name)
    # Remove an item
    if rem is not None:
        items.remove(rem)
    sqliteItems = []
    for i in items:
        sqliteItems.append(getProduct(i)[0])
    resp = make_response(render_template("cart.html", items=sqliteItems))
    # Cookie must be a string
    resp.set_cookie("cartItems", "BREAK".join(items))
    return resp


@app.route("/checkout", methods=['POST'])
def checkout():
    if overEighteen():
        f = request.form
        return render_template('checkout.html', formStuff=f)
    else:
        return redirect(url_for("ageGate"))


@app.route('/handlePayment', methods=['POST'])
def handlePayment():
    resp = make_response(render_template("paymentComplete.html"))
    resp.set_cookie("cartItems", expires=0)
    payment.doThePayStuff(request.form)
    return resp


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/favicon.ico'), code=302)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404



# Database stuff
# http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
DATABASE = 'Scraper/LMBB.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def getCategory(name):
    return query_db('SELECT * FROM products WHERE `category` IS (?)', (name,))

def getProduct(name):
    return query_db('SELECT * FROM products WHERE `title` IS (?)', (name,))

def getArticles():
    return query_db('SELECT * FROM articles')



if __name__ == "__main__":
    app.run(host='0.0.0.0')
