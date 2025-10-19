# src/tot/prompts/gsm8k/gsm8k.py
"""
GSM8K Prompting Templates

This module contains the prompting templates used for the GSM8K mathematical
reasoning task. These prompts are designed to elicit numerical answers from
language models for grade school math word problems.

"""

standard_prompt = '''Solve the following math word problem.

Input: {input}
Answer: '''