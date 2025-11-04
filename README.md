# Contextual_Boost_LLMs

A statistical framework for testing how role-conditioning influences LLM reasoning, accuracy, and cognitive behavior

## Overview

This project explores whether assigning explicit roles (e.g., “You are a scientist” or “You are a teacher”) improves reasoning accuracy in large language models (LLMs).
We test this hypothesis using ChatGPT-4o on 100 graduate-level multiple-choice questions from the GPQA dataset.

Each question was asked twice:

* **No-Role:** Standard prompt
* **Role:** Prompt with an assigned expert identity

## Method Summary

* **Design:** Paired (within-question) comparison
* **Independent variable:** Prompt type (Role vs. No-Role)
* **Dependent variable:** Binary correctness of model output
* **Main test:** McNemar’s exact test (paired binary)
* **Additional checks:** Wilcoxon and paired t-tests for effect-size estimation

## How to Reproduce

### 1. Setup

Create a `.env` file containing your OpenAI key:

`OPENAI_API_KEY=your_key_here`

### 2. Install dependencies

`pip install -r requirements.txt`

**Required libraries:** openai, pandas, numpy, scipy, dotenv, json

### 3. Run data collection

`python experiment.py`

This script:

* Randomly samples 100 GPQA questions
* Sends each question twice (normal + role) to ChatGPT-4o
* Saves outputs to `gpqa_dual_results.json`

### 4. Run statistical analysis

`python experiment-analysis.py`

This script:

* Verifies independence and normality assumptions
* Runs McNemar’s exact test
* Computes paired t- and Wilcoxon tests and effect sizes (Cohen’s h, d)
* Exports cleaned and summarized results to `analysis_results.csv`

## Key Findings

* **Overall accuracy:** No-Role = 44 %, Role = 47 % (Δ = +3 %, p = 0.65)
* **Domain trends:**

  * Physics / Astrophysics → slight improvement
  * Chemistry / Organic Chemistry → slight decline
* **Conclusion:** Role prompts alter tone and reasoning style more than factual correctness.

## Data

* **Raw data:** Model responses stored in `gpqa_dual_results.json`
* **Cleaned data:** Processed results and statistical outputs in `analysis_results.csv`
* GPQA content is licensed; only derived metrics (not full questions) are included.

## Collaboration and Version Control

Each contributor worked on a dedicated branch (`data-collection`, `analysis`, `reporting`), submitting at least one pull request to `main`.
All PRs underwent peer review before merging, following best practices for collaborative Git workflows.
