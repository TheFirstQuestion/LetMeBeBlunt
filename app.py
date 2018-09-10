from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/favicon.ico'), code=302)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
