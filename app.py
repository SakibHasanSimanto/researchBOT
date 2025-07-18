from flask import Flask, render_template, request, redirect, url_for
import os
#-- 
from utils.prompt_builder import build_comparison_prompt
from utils.groq_api import call_groq_model
#-- 

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        paper_a = request.form.get("paper_a", "")
        paper_b = request.form.get("paper_b", "")
        selected_model = request.form.get("selected_model", "")

        if not paper_a.strip() or not paper_b.strip():
            return render_template("index.html", error="Please provide both paper abstracts.")

        try:
            # Step 1: Build the comparison prompt
            prompt = build_comparison_prompt(paper_a, paper_b)

            # Step 2: Call Groq model
            result = call_groq_model(prompt, selected_model)

            # Step 3: Render result page
            return render_template("result.html",
                                   paper_a=paper_a,
                                   paper_b=paper_b,
                                   selected_model=selected_model,
                                   result=result)

        except Exception as e:
            return render_template("index.html", error=f"Something went wrong: {str(e)}")

    return render_template("index.html")

