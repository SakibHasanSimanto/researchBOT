from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        paper_a = request.form.get("paper_a", "")
        paper_b = request.form.get("paper_b", "")
        selected_model = request.form.get("selected_model", "")

        # For now, just pass values to result page (no processing yet)
        return render_template("result.html", paper_a=paper_a, paper_b=paper_b, selected_model=selected_model)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
