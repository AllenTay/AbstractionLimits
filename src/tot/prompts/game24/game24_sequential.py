"""
Game of 24 Sequential Refinement Prompts

Three-stage iterative process:
1. Natural generation: Initial problem-solving attempts
2. Reflection: Systematic analysis of failure patterns
3. Refinement: Generate improved solutions based on insights
"""

# Stage 1: Natural initial attempt with strategic hints
natural_prompt = '''Use numbers and basic arithmetic operations (+ - * /) to obtain 24.
IMPORTANT: You must use each input number exactly once - no more, no less.

Winning patterns to look for:
- Make 4 and 6, then multiply: 4 × 6 = 24
- Make 3 and 8, then multiply: 3 × 8 = 24  
- Make 2 and 12, then multiply: 2 × 12 = 24

Try to create these intermediate numbers from your input.

Your response MUST end with:
Answer: [equation] = 24

Examples:
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

# Stage 2: Systematic failure analysis
reflect_prompt = '''Problem: Use {input} to make 24 (each number exactly once with +, -, *, /)

ALL failed attempts:
{attempts}

Analyze systematically:

1. RESULTS CHECK
For each attempt above:
- Is it a valid equation? If yes, what does it equal?
- If it equals something other than 24, how far off is it?
- Which attempt got closest to 24?

2. ERROR PATTERNS  
Across ALL attempts:
- Did any reuse numbers or skip numbers?
- Did any make arithmetic errors?
- What operations were tried (addition-heavy? multiplication-first?)

3. UNEXPLORED TERRITORY
What approaches were NOT tried?
- Different number groupings: (a+b)*(c-d) vs (a*b)+(c*d)
- Different operation sequences: multiply-first vs add-first
- Creating intermediate targets (4,6 or 3,8 or 2,12)

4. SPECIFIC NEXT STEP
Based on the above, give ONE concrete approach to try next.
Not general advice - a specific starting move like "Combine 10 and 6 first to make 16, then..."

Your analysis:'''

reflect_prompt_brief = '''Problem: Use {input} to make 24 (each number exactly once with +, -, *, /)

Failed attempts:
{attempts}

Analyze these failures:
1. Which attempt got closest to 24?
2. What common errors occurred?
3. What specific approach should be tried next?

Your analysis:'''

# Stage 3: Targeted refinement based on reflection
refine_prompt = '''Problem: Use {input} to make 24 (each number exactly once with +, -, *, /)

PREVIOUS ATTEMPTS SUMMARY:
{failed_attempt}

ANALYSIS OF FAILURES:
{reflection}

HISTORY ACROSS ITERATIONS:
{history}

Generate a NEW solution that:
1. Avoids the specific errors identified above
2. Tries the unexplored approach suggested in the analysis
3. Uses a different starting combination than previous attempts

Think step-by-step, but your final response MUST end with:
Answer: [equation] = 24

Example format:
Answer: (10 - 6) * (5 + 1) = 24

Your new solution:'''