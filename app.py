from flask import Flask, render_template, request
from utils.groq_api import call_groq_model, split_thoughts 

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        paper_a = request.form.get("paper_a", "")
        paper_b = request.form.get("paper_b", "")
        selected_model = request.form.get("selected_model", "")

        # Prompt construction
        full_prompt = f"""
Compare the two research papers below *strictly* based on their scientific content, and rate on a scale of 10. Include final rating in the end of your response. Be very concise with your response.

Explain shortly, evaluate, and compare the following dimensions:
1. Novelty and originality
2. Scientific rigor and methodology
3. Clarity of research goal and execution
4. Depth of analysis and significance of findings
5. Limitations and transparency
6. Potential research impact

### Paper A
{paper_a}

### Paper B
{paper_b}
"""

        try:
            output = query_groq(full_prompt, selected_model)
            reasoning, final_result = split_thoughts(output)

            return render_template(
                "result.html",
                paper_a=paper_a,
                paper_b=paper_b,
                selected_model=selected_model,
                result=final_result,
                reasoning=reasoning
            )
        except Exception as e:
            return render_template("error.html", message=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
