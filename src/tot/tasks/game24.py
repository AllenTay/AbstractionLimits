"""
Game of 24 Task Implementation

Task: Use 4 numbers with basic arithmetic (+, -, *, /) to make 24.
Each number must be used exactly once.

Example:
    Input: "4 9 10 13"
    Output: "(13-9)*(10-4)=24"
    
Evaluation: Validates equation uses all numbers once and equals 24.
"""

import re
import os
import sympy
import pandas as pd
from src.tot.tasks.base import Task, DATA_PATH
from src.tot.prompts.game24.game24 import * 
from src.tot.prompts.game24.game24_sequential import (
    natural_prompt,
    reflect_prompt,
    reflect_prompt_brief, 
    refine_prompt
)

def get_current_numbers(y: str) -> str:
    """Extract remaining numbers from last line of thought chain."""
    last_line = y.strip().split('\n')[-1]
    if 'left: ' in last_line:
        return last_line.split('left: ')[-1].split(')')[0]
    return y.strip()


class Game24Task(Task):
    """
    Game of 24 mathematical reasoning task.
    
    Dataset: 1,362 games from 4nums.com, sorted by difficulty.
    Test set: Problems 901-1000 (harder problems).
    
    Attributes:
        data: List of 4-number puzzles
        value_cache: Cached LM evaluations for efficiency
        steps: Number of intermediate equations (always 3)
        stops: Stop tokens for each step
    """
    
    def __init__(self, file='24.csv'):
        super().__init__()
        path = os.path.join(DATA_PATH, 'game24', file)
        self.data = list(pd.read_csv(path)['Puzzles'])
        self.value_cache = {}
        self.steps = 4
        self.stops = ['\n'] * 4

    def __len__(self) -> int:
        return len(self.data)
    
    def get_input(self, idx: int) -> str:
        return self.data[idx]
    
    def test_output(self, idx: int, output: str):
        """
        Validate solution correctness.
        
        Checks:
        1. Extracts equation from various output formats
        2. Verifies all input numbers used exactly once
        3. Confirms equation evaluates to 24
        
        Returns:
            dict: {'r': 1} if correct, {'r': 0} otherwise
        """
        original_output = output
        output = output.strip()
        
        # Extract equation - try multiple patterns
        expression = None
        
        # Pattern 1: \boxed{equation}
        if '\\boxed{' in output:
            match = re.search(r'\\boxed\{([^}]+)\}', output)
            if match:
                expression = match.group(1)
        
        # Pattern 2: Answer: equation
        if not expression and 'answer:' in output.lower():
            for line in reversed(output.split('\n')):
                if 'answer:' in line.lower():
                    expression = line.split(':', 1)[1].strip()
                    break
        
        # Pattern 3: equation = 24
        if not expression:
            match = re.search(r'([0-9+\-*/().\s]+)\s*=\s*24', output)
            if match:
                expression = match.group(1).strip()
        
        # Pattern 4: Last line with numbers and operators
        if not expression:
            lines = output.split('\n')
            for line in reversed(lines):
                line = line.strip()
                if re.search(r'\d', line) and re.search(r'[+\-*/]', line):
                    expression = re.sub(r'\s*=\s*24\s*$', '', line)
                    break
        
        if not expression:
            return {'r': 0}
        
        # Clean expression
        expression = re.sub(r'\s*=\s*24\s*$', '', expression)
        expression = expression.strip()
        expression = re.sub(r'^[^0-9()]*', '', expression)
        expression = re.sub(r'[^0-9()]*$', '', expression)
        
        # Verify correct numbers used
        numbers = re.findall(r'\d+', expression)
        problem_numbers = re.findall(r'\d+', self.data[idx])
        
        if sorted(numbers) != sorted(problem_numbers):
            return {'r': 0}
        
        # Verify equals 24
        try:
            result = sympy.simplify(expression)
            is_correct = int(result == 24)
            return {'r': is_correct}
        except Exception as e:
            return {'r': 0}
                
    @staticmethod
    def standard_prompt_wrap(x: str, y: str = '') -> str:
        """Standard IO prompting with few-shot examples."""
        return standard_prompt.format(input=x) + y

    @staticmethod
    def propose_prompt_wrap(x: str, y: str = '') -> str:
        """Generate next step proposals for ToT."""
        current_numbers = get_current_numbers(y if y else x)
        if current_numbers == '24':
            return y
        else:
            prompt = propose_prompt.format(input=current_numbers)
        return prompt
    
    @staticmethod
    def value_prompt_wrap(x: str, y: str) -> str:
        """Evaluate intermediate step or final solution."""
        last_line = y.strip().split('\n')[-1]
        
        # Check if complete solution (no numbers left)
        if '(left:' in last_line:
            parts = last_line.split('(left:')
            operation = parts[0].strip()
            remaining_part = parts[1].strip().rstrip(')')
            
            # Extract numbers only
            if '|' in remaining_part:
                remaining = remaining_part.split('|')[0].strip()
            else:
                remaining = remaining_part.strip()
            
            # No numbers remain -> final solution
            if not remaining or remaining == '':
                return value_last_step_prompt.format(input=x, answer=operation)
        
        # Alternative format (no "left:" marker)
        if 'left: ' not in last_line:
            ans = last_line.lower().replace('answer: ', '').strip()
            return value_last_step_prompt.format(input=x, answer=ans)
        
        # Regular intermediate step
        parts = last_line.split('(left:')
        operation = parts[0].strip()
        remaining_part = parts[1].strip().rstrip(')')
        
        if '|' in remaining_part:
            remaining = remaining_part.split('|')[0].strip()
        else:
            remaining = remaining_part.strip()
        
        return value_prompt.format(input=x, operation=operation, remaining=remaining)
    
    @staticmethod
    def value_outputs_unwrap(x: str, y: str, value_outputs: list) -> float:
        """Parse LM evaluation scores (1-10 scale)."""
        scores = []
        
        for output in value_outputs:
            # Primary pattern: "Score: N"
            match = re.search(r'score[:\s]+(\d+)', output.lower())
            if match:
                score = int(match.group(1))
                if 1 <= score <= 10:
                    scores.append(score)
                continue
            
            # Fallback: look for standalone number
            lines = output.strip().split('\n')
            for line in reversed(lines):
                nums = re.findall(r'\b([1-9]|10)\b', line)
                if nums:
                    scores.append(int(nums[-1]))
                    break
        
        if not scores:
            print(f"WARNING: Could not parse scores from outputs: {value_outputs}")
            return 1.0
        
        avg_score = sum(scores) / len(scores)
        return avg_score
    
    
    @staticmethod
    def natural_prompt_wrap(x: str) -> str:
        """Natural problem-solving prompt for sequential refinement."""
        return natural_prompt.format(input=x)

    @staticmethod
    def reflect_prompt_wrap(x: str, attempts: str) -> str:
        """Analyze failure patterns for sequential refinement."""
        return reflect_prompt_brief.format(input=x, attempts=attempts)

    @staticmethod
    def refine_prompt_wrap(x: str, failed_attempt: str, reflection: str, history: str = '') -> str:
        """Generate improved solution based on reflection."""
        return refine_prompt.format(
            input=x,
            failed_attempt=failed_attempt,
            reflection=reflection,
            history=history if history else "First iteration"
        )