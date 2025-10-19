# gsm8k.py

"""
GSM8K Task Implementation

This module implements the GSM8K (Grade School Math 8K) task for evaluating
language model mathematical reasoning capabilities. GSM8K consists of grade
school level math word problems requiring multi-step reasoning.

Task Structure:
    Input (x): A math word problem (string)
    Output (y): A numerical answer (string)
    Reward (r): Binary score (0 or 1) for exact match

Example:
    Input: "Natalia sold clips to 48 of her friends in April, and then she 
           sold half as many clips in May. How many clips did Natalia sell 
           altogether in April and May?"
    Output: "72"
    Reward: 1 (if correct), 0 (if incorrect)
"""

import re
import os
import json
from src.tot.tasks.base import Task, DATA_PATH
from src.tot.prompts.gsm8k.gsm8k import standard_prompt


def extract_answer(text: str) -> str:
    """
    Extract numerical answer from model output using multiple patterns.
    
    This function tries various common patterns that language models use to
    present numerical answers, including explicit "Answer:" prefixes, natural
    language phrases like "the answer is", and the GSM8K dataset format (####).
    
    Args:
        text: Raw model output text that may contain the numerical answer
              along with reasoning steps or explanatory text
    
    Returns:
        Extracted numerical answer as a string. Returns the last number found
        in the text if no explicit answer pattern matches. Returns empty string
        if no numbers are found.
    
    Examples:
        >>> extract_answer("The calculation is 5 + 3 = 8. Answer: 8")
        '8'
        >>> extract_answer("After solving, the answer is 42")
        '42'
        >>> extract_answer("Step 1: Add 10 and 5... #### 15")
        '15'
    """
    # Pattern 1: Explicit "Answer:" prefix (case-insensitive)
    # Pattern 2: Natural language "the answer is X"
    # Pattern 3: GSM8K dataset format with ####
    # Pattern 4: Equation ending with = number
    patterns = [
        r'[Aa]nswer:\s*(\d+)',
        r'the answer is\s*(\d+)',
        r'####\s*(\d+)',
        r'=\s*(\d+)\s*$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Fallback: Extract the last number in the text
    numbers = re.findall(r'\d+', text)
    if numbers:
        return numbers[-1]
    
    return ""


class GSM8KTask(Task):
    """
    GSM8K mathematical reasoning task.
    
    This task evaluates language models on grade school math word problems
    that require multi-step arithmetic reasoning. The dataset contains 1,319
    test problems covering topics like addition, subtraction, multiplication,
    division, percentages, and ratios.
    
    Attributes:
        data: List of question strings (math word problems)
        answers: List of ground truth numerical answers (strings)
    
    Methods:
        __len__: Returns number of problems in the dataset
        get_input: Returns the question text for a given problem index
        test_output: Evaluates if a model's output matches the ground truth
        standard_prompt_wrap: Wraps input with standard prompting format
    """
    
    def __init__(self, file: str = 'test.jsonl'):
        """
        Initialize GSM8K task with data from JSONL file.
        
        The JSONL file should contain one problem per line with 'question' and
        'answer' fields. The 'answer' field contains both solution steps and
        the final numerical answer in the format "#### NUMBER".
        
        Args:
            file: Filename of the GSM8K data file in data/gsm8k/ directory.
                  Default is 'test.jsonl' containing 1,319 test problems.
        
        Raises:
            FileNotFoundError: If the specified data file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        super().__init__()
        path = os.path.join(DATA_PATH, 'gsm8k', file)
        self.data = []
        self.answers = []
        
        with open(path, 'r') as f:
            for line in f:
                item = json.loads(line)
                self.data.append(item['question'])
                
                # Extract numerical answer from the "#### NUMBER" format
                answer_text = item['answer']
                answer_match = re.search(r'####\s*(\d+)', answer_text)
                if answer_match:
                    self.answers.append(answer_match.group(1))
                else:
                    self.answers.append("")

    def __len__(self) -> int:
        """
        Return the total number of problems in the dataset.
        
        Returns:
            Integer count of problems (1,319 for test.jsonl)
        """
        return len(self.data)
    
    def get_input(self, idx: int) -> str:
        """
        Get the input question for a specific problem.
        
        Args:
            idx: Zero-based index of the problem (0 to len(self)-1)
        
        Returns:
            The math word problem as a string
        
        Raises:
            IndexError: If idx is out of bounds
        """
        return self.data[idx]

    def test_output(self, idx: int, output: str) -> dict:
        """
        Evaluate if the model's output is correct for the given problem.
        
        This method extracts the numerical answer from the model's output
        (which may include reasoning steps) and compares it to the ground
        truth answer using exact string matching.
        
        Args:
            idx: Problem index to evaluate against
            output: Raw model output text (may include reasoning and answer)
        
        Returns:
            Dictionary with single key 'r':
                - 'r': 1 if predicted answer matches ground truth, 0 otherwise
        
        Example:
            >>> task = GSM8KTask()
            >>> output = "First add 48 + 24 = 72. Answer: 72"
            >>> task.test_output(0, output)
            {'r': 1}  # If ground truth for problem 0 is "72"
        """
        predicted = extract_answer(output)
        correct = self.answers[idx]
        return {'r': int(predicted == correct)}
            
    @staticmethod
    def standard_prompt_wrap(x: str, y: str = '') -> str:
        """
        Wrap input question with standard prompting format.
        
        This static method formats the input question using the standard
        GSM8K prompt template, which includes task instructions and optional
        few-shot examples (defined in src/tot/prompts/gsm8k/gsm8k.py).
        
        Args:
            x: Input question (math word problem)
            y: Optional partial answer or reasoning to continue from.
                Typically empty string for standard zero-shot prompting.
        
        Returns:
            Formatted prompt string ready for language model input
        
        Example:
            >>> prompt = GSM8KTask.standard_prompt_wrap(
            ...     "What is 5 + 3?", 
            ...     ""
            ... )
            >>> # Returns: "Solve the following math word problem.\n\n
            >>> #           Input: What is 5 + 3?\nAnswer: "
        """
        return standard_prompt.format(input=x) + y