def get_task(name):
    """Factory function to get task instances by name."""
    if name == 'gsm8k':
        from .gsm8k import GSM8KTask
        return GSM8KTask()
    elif name == 'game24':
        from .game24 import Game24Task
        return Game24Task()
    elif name == 'crosswords':
        from .crosswords import MiniCrosswordsTask
        return MiniCrosswordsTask()
    else:
        raise NotImplementedError(f"Task '{name}' not implemented")
    