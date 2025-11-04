from dotenv import load_dotenv
import os
import json
import openai
import re
import random
import csv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o"       
SAMPLE_SIZE = 100           # number of random questions i'm sampling from the dataset
OUTPUT_FILE = "gpqa_dual_results.csv"
RANDOM_SEED = 42            # for reproducibility


# loading the dataset
with open("GPQA_Diamond_role_prompts_pretty.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)


random.seed(RANDOM_SEED)
sample = random.sample(dataset, SAMPLE_SIZE)
def get_model_answer(prompt, prompt_type):
    """sending prompt to model and returning (raw_output, parsed_letter)."""
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    raw_output = response.choices[0].message.content.strip()
    match = re.search(r"\b([A-D])\b", raw_output, re.IGNORECASE)  # extracting the first A-D answer from the output
    answer = match.group(1).upper() if match else "?"
    return raw_output, answer


results = []

for idx, item in enumerate(sample, 1):
    qid = item["id"]
    correct_option = item["correct_option"].upper()
    subdomain = item.get("subdomain", "")

    print(f"\n ● [{idx}/{SAMPLE_SIZE}] QID {qid} ({subdomain})")

    # baseline evaluation (prompt without role)
    base_prompt = item["question"] + "\n\nExplain your reasoning carefully before giving the final letter answer."
    base_output, base_answer = get_model_answer(base_prompt, "normal")
    base_correct = base_answer == correct_option
    print(f"   Normal -> {base_answer} | {'YES' if base_correct else 'NO'} | Raw: {base_output}")

    results.append({
        "id": qid,
        "subdomain": subdomain,
        "prompt_type": "normal",
        "model_answer": base_answer,
        "correct_option": correct_option,
        "is_correct": base_correct,
        "raw_output": base_output
    })

    # role-based evaluation
    role_prompt = item["role_prompt"] + "\n\nExplain your reasoning carefully before giving the final letter answer."
    role_output, role_answer = get_model_answer(role_prompt, "role")
    role_correct = role_answer == correct_option
    print(f"   Role  -> {role_answer} | {'YES' if role_correct else 'NO'} | Raw: {role_output}")

    results.append({
        "id": qid,
        "subdomain": subdomain,
        "prompt_type": "role",
        "model_answer": role_answer,
        "correct_option": correct_option,
        "is_correct": role_correct,
        "raw_output": role_output
    })

import json

with open("gpqa_dual_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Results saved to gpqa_dual_results.json")
from collections import defaultdict
from pathlib import Path
import json

with open("gpqa_dual_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# grouping entries by question ID
by_id = defaultdict(list)
for row in data:
    by_id[row.get("id")].append(row)

# prettifying texts for md format
def to_md(text: str) -> str:
    if not text:
        return ""
    return (
        text.replace("\\n", "\n")                # real newlines
            .replace("\\(", "$").replace("\\)", "$")  # inline math
            .replace("\\[", "$$").replace("\\]", "$$")  # display math
    )

# order for prompt types: normal first, then role-based
order = {"normal": 0, "role": 1}

lines = []
for qid in sorted(by_id):
    entries = sorted(by_id[qid], key=lambda r: order.get(r.get("prompt_type",""), 99))
    subdomain = entries[0].get("subdomain", "Unknown")
    lines.append(f"## Q{qid} — {subdomain}")
    correct = entries[0].get("correct_option", "")
    if correct:
        lines.append(f"**Correct option:** {correct}")
    lines.append("")
    for e in entries:
        ptype = e.get("prompt_type", "")
        lines.append(f"### {ptype.title()} prompt\n")
        lines.append(to_md(e.get("raw_output","")).strip())
        lines.append("\n---\n")
    lines.append("\n")

Path("gpqa_readable_grouped.md").write_text("\n".join(lines), encoding="utf-8")