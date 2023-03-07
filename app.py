from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detail")
def detail():
    return render_template("detail.html")


@app.route("/checkout")
def checkout():
    return render_template("checkoutform.html")

if __name__=="__main__":
    app.run(debug=True)