import os

# Adjust this path based on where you put your data
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data')

class Task:
    """Base class for all tasks."""
    
    def __init__(self):
        pass

    def __len__(self) -> int:
        """Return the number of problems in the dataset."""
        raise NotImplementedError

    def get_input(self, idx: int) -> str:
        """Get the input for problem at index idx."""
        raise NotImplementedError

    def test_output(self, idx: int, output: str) -> dict:
        """
        Test if the output is correct for problem at index idx.
        Returns dict with 'r' key (0 or 1).
        """
        raise NotImplementedError