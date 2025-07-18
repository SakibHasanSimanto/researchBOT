def build_comparison_prompt(paper_a: str, paper_b: str) -> str:
    prompt = f"""
You are a neutral scientific reviewer.

Compare the two research papers *strictly* based on their content only. Avoid any bias based on journal, institution, author, or citations.

Evaluate based on these criteria:
1. Novelty and originality
2. Scientific rigor and methodology
3. Clarity of research question and execution
4. Depth and significance of results
5. Limitations and transparency
6. Potential impact in its field

Give each paper a score out of 10 (decimal allowed). At the end, show the scores like:

Final Score:
Paper A: X.X / 10
Paper B: Y.Y / 10

### Paper A
{paper_a}

### Paper B
{paper_b}
"""
    return prompt.strip()
