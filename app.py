from flask import Flask, render_template
from analyzer import save_report, build_report

app = Flask(__name__)

@app.route("/")
def dashboard():
    report = build_report()
    return render_template("dashboard.html", report = report)


if __name__ == "__main__":
    app.run(debug = True)