"""
Game of 24 Prompting Templates for Tree of Thoughts

Prompts designed for ToT search with proposal generation and value evaluation.
Examples chosen to demonstrate target factorizations (4×6, 3×8, 2×12).
"""

standard_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24.
IMPORTANT: You must use each input number exactly once - no more, no less.
Give ONLY the final equation. Do not explain your reasoning.

Input: 4 4 6 8
Answer: (4 + 8) * (6 - 4) = 24

Input: 2 9 10 12
Answer: 2 * 12 * (10 - 9) = 24

Input: 4 9 10 13
Answer: (13 - 9) * (10 - 4) = 24

Input: 1 4 8 8
Answer: (8 / 4 + 1) * 8 = 24

Input: 5 5 5 9
Answer: 5 + 5 + 5 + 9 = 24

Input: {input}
Answer:'''

# ToT proposal prompt: Generate next intermediate step
propose_prompt = '''Game of 24: Make 24 using these numbers: {input}

RULE: Each number used exactly once using +,-,/ or *. When you combine 2 numbers, replace them with the result.

FORMAT: num1 ⊕ num2 = result (left: all_remaining_including_result) | Reason: brief

EXAMPLE ONLY (for "4 3 2 1" - different numbers, just showing format):
4 * 18 = 72 (left: 72 2 1) | Reason: 2+1=3, then 72/3=24

YOUR PROBLEM: {input}
Generate 3 best operations using {input}:
'''

# Value evaluation for intermediate steps
value_prompt = '''Game of 24 problem: {input}

Step just performed: {operation}
Numbers still available: {remaining}

Remember: The goal is to use ALL the original input numbers exactly once to make 24.

Evaluate this intermediate step with a score from 1 to 10:

Scoring guide:
- Score 10: Clearly leads to 24 (you can see the solution)
- Score 7-9: Very promising, good progress toward 24
- Score 4-6: Possible but unclear if it helps
- Score 1-3: Bad move, makes reaching 24 harder or impossible
- Score 1: Uses numbers not in the input or creates impossible situation

Provide your response in this exact format:
Analysis: [one sentence explaining why this step helps or hurts]
Score: [single number from 1 to 10]
'''

# Value evaluation for final solutions
value_last_step_prompt = '''Check if this equation solves Game of 24.

Input numbers: {input}
Proposed answer: {answer}

Verify ALL three conditions:
1. Does it use each input number exactly once?
2. Is the math correct?
3. Does it equal 24?

Respond in this exact format:
Analysis: [brief check of the three conditions]
Score: [10 if ALL conditions met, otherwise 1]
'''