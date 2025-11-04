# Contextual_Boost_LLMs
A statistical framework for testing how role-conditioning influences LLM reasoning, accuracy, and cognitive behavior

## Overview

This project explores whether assigning explicit roles (e.g., “You are a scientist” or “You are a teacher”) improves reasoning accuracy in large language models (LLMs).
We test this hypothesis using ChatGPT-4o on 100 graduate-level multiple-choice questions from the GPQA dataset.

Each question was asked twice:

No-Role: Standard prompt

Role: Prompt with an assigned expert identity

## Method Summary

Design: Paired (within-question) comparison

Independent variable: Prompt type (Role vs. No-Role)

Dependent variable: Binary correctness of model output

Main test: McNemar’s exact test (paired binary)

Additional checks: Wilcoxon and paired t-tests for effect size estimation

## How to Reproduce

Prepare API key
Create a .env file:

OPENAI_API_KEY=your_key_here


Run data collection

python experiment.py


Randomly samples 100 GPQA questions

Sends each question twice (normal + role) to ChatGPT-4o

Saves outputs to gpqa_dual_results.json

Run statistical analysis

python experiment-analysis.py

This script:

Verifies independence and normality assumptions

Runs McNemar’s exact test

Computes paired t- and Wilcoxon tests, effect sizes (Cohen’s h, d)

## Key Findings

Overall accuracy: No-Role = 44 %, Role = 47 % (Δ = +3 %, p = 0.65)

Domain trends:

Physics / Astrophysics → slight improvement

Chemistry / Organic Chemistry → decline

Conclusion: Role prompts change tone and reasoning style, not factual correctness.