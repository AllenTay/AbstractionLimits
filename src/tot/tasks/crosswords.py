"""
Mini Crosswords Task Implementation

Task: Solve 5x5 mini crosswords given 10 clues (5 horizontal, 5 vertical).
Each answer is exactly 5 letters.

Example:
    Input: "h1. A lunar valley\nh2. A fatty oil\n..."
    Output: "R I L L E\nO L E I N\n..."
    
Evaluation: Letter-level, word-level, and game-level accuracy.
"""

import re
import os
import json
from src.tot.tasks.base import Task, DATA_PATH
from src.tot.prompts.crosswords.crosswords import standard_prompt
from src.tot.prompts.crosswords.crosswords_sequential import (
    natural_prompt,
    reflect_prompt_brief,
    refine_prompt
)


class MiniCrosswordsTask(Task):
    """
    5x5 mini crosswords solving task.
    
    Dataset: 156 games from GooBix, using every 5th game for testing.
    Test set: Games at indices 0, 5, 10, ... (mapped via idx * 5).
    
    Attributes:
        all_data: List of (clues, board) tuples
        n_games: Total number of games in dataset
    """
    
    def __init__(self, file='mini0505.json'):
        super().__init__()
        path = os.path.join(DATA_PATH, 'crosswords', file)
        
        with open(path, 'r') as f:
            self.all_data = json.load(f)
        
        self.n_games = len(self.all_data)
    
    def __len__(self) -> int:
        return self.n_games
    
    def get_input(self, idx: int) -> str:
        """
        Get clues for crossword puzzle.
        
        Maps idx to every 5th game: idx 0→game 0, idx 1→game 5, etc.
        
        Args:
            idx: Problem index (0 to len(self)//5 - 1)
            
        Returns:
            Formatted clues string (h1-h5, then v1-v5)
        """
        actual_idx = idx * 5
        clues, _ = self.all_data[actual_idx]
        lines = []
        for i in range(5):
            lines.append(f'h{i+1}. {clues[i]}')
        for i in range(5, 10):
            lines.append(f'v{i-4}. {clues[i]}')
        return '\n'.join(lines)
    
    def test_output(self, idx: int, output: str) -> dict:
        """
        Validate solution correctness at three granularities.
        
        Extracts 5x5 letter grid from output and compares to ground truth.
        Maps idx to every 5th game: idx 0→game 0, idx 1→game 5, etc.
        
        Args:
            idx: Problem index
            output: Generated solution (should contain 5 rows of 5 letters)
            
        Returns:
            dict: {'r_letter': float, 'r_word': float, 'r_game': int, 'r': float}
                - r_letter: Proportion of correct letters (0-1)
                - r_word: Proportion of correct words (0-1)  
                - r_game: Binary game success (0 or 1)
                - r: Primary metric (same as r_word)
        """
        actual_idx = idx * 5
        _, board_gt = self.all_data[actual_idx]
        
        lines = output.strip().split('\n')
        board_pred = []
        
        for line in lines:
            # Try word boundary pattern first
            letters = re.findall(r'\b[A-Za-z]\b', line)
            
            # If that fails, try finding sequences of capital letters
            if len(letters) != 5 and re.search(r'[A-Z].*[A-Z].*[A-Z].*[A-Z].*[A-Z]', line):
                letters = re.findall(r'[A-Z]', line)[:5]
            
            if len(letters) == 5:
                board_pred.extend([letter.upper() for letter in letters])
            if len(board_pred) >= 25:
                break
        
        # Pad incomplete boards
        while len(board_pred) < 25:
            board_pred.append('_')
        
        board_pred = board_pred[:25]
        
        # Flatten ground truth
        board_gt_flat = []
        for row in board_gt:
            board_gt_flat.extend(list(row.upper()))
        
        # Letter-level accuracy
        correct_letters = sum(1 for p, g in zip(board_pred, board_gt_flat) if p == g)
        r_letter = correct_letters / 25
        
        # Word-level accuracy (5 horizontal + 5 vertical)
        def get_words(board):
            words = []
            for i in range(5):
                words.append(''.join(board[i*5:(i+1)*5]))
            for i in range(5):
                words.append(''.join(board[i::5]))
            return words
        
        words_pred = get_words(board_pred)
        words_gt = get_words(board_gt_flat)
        
        correct_words = sum(1 for p, g in zip(words_pred, words_gt) if p == g)
        r_word = correct_words / 10
        
        # Game-level accuracy
        r_game = 1 if board_pred == board_gt_flat else 0
        
        return {
            'r_letter': r_letter,
            'r_word': r_word, 
            'r_game': r_game,
            'r': r_word
        }
    
    @staticmethod
    def standard_prompt_wrap(x: str, y: str = '') -> str:
        """Standard IO prompting with few-shot examples."""
        return standard_prompt.format(input=x) + y
    
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