"""
Mini Crosswords Sequential Refinement Prompts

Three-stage iterative process:
1. Natural generation: Initial solving attempt with clear format requirements
2. Reflection: Analysis of constraint conflicts and word choices
3. Refinement: Generate improved solution based on insights
"""

# Stage 1: Natural initial attempt with explicit format requirements
natural_prompt = '''Solve the 5x5 mini crossword. Each answer is exactly 5 letters.

{input}

Your response MUST end with 5 rows of 5 letters separated by spaces:

Output:
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]
'''

# Stage 2: Focused failure analysis on constraint conflicts
reflect_prompt_brief = '''Problem:
{input}

Failed attempts:
{attempts}

Analyze:
1. Which words are likely correct?
2. Which intersections are causing conflicts?
3. What specific words should be reconsidered?

Your analysis:'''

# Stage 3: Targeted refinement based on reflection
refine_prompt = '''Problem:
{input}

PREVIOUS ATTEMPT:
{failed_attempt}

ANALYSIS:
{reflection}

HISTORY:
{history}

Generate a NEW solution. Your response MUST end with:

Output:
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]
[5 letters with spaces]

Your new solution:'''