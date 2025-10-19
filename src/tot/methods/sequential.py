import re
import numpy as np
from functools import partial
from src.tot.models import llama


def extract_equation(attempt: str) -> str:
    """
    Extract clean equation from attempt response.
    
    Args:
        attempt: Raw model output
        
    Returns:
        Extracted equation string, or empty string if not found
    """
    if 'answer:' in attempt.lower():
        parts = attempt.lower().split('answer:')
        if len(parts) > 1:
            candidate = parts[-1].strip()
            candidate = re.sub(r'\s*=\s*24\s*$', '', candidate)
            if re.search(r'[+\-*/]', candidate):
                return candidate
    
    match = re.search(r'([0-9+\-*/().\s]+)\s*=\s*24', attempt)
    if match:
        return match.group(1).strip()
    
    lines = attempt.split('\n')
    for line in reversed(lines):
        line = line.strip()
        if re.search(r'\d', line) and re.search(r'[+\-*/]', line):
            line = re.sub(r'\s*=\s*24\s*$', '', line)
            return line
    
    return ""


def get_attempt_value(task, idx: int, attempt: str) -> int:
    """
    Evaluate how close an attempt is to success.
    
    Args:
        task: Task instance with test_output method
        idx: Problem index
        attempt: Solution attempt string
        
    Returns:
        Score: 100 if correct, distance from 24 if close, 0 if invalid
    """
    result = task.test_output(idx, attempt)
    if result['r'] == 1:
        return 100
    
    equation = extract_equation(attempt)
    if not equation:
        return 0
    
    try:
        import sympy
        value = float(sympy.simplify(equation))
        distance = abs(24 - value)
        return max(0, 50 - distance)
    except:
        return 0


def format_attempt_summary(attempts: list, task, idx: int) -> str:
    """
    Create detailed summary of attempts for reflection.
    
    Args:
        attempts: List of attempt strings
        task: Task instance
        idx: Problem index
        
    Returns:
        Formatted summary showing equations and their results
    """
    summary_lines = []
    for i, attempt in enumerate(attempts, 1):
        equation = extract_equation(attempt)
        if equation:
            try:
                import sympy
                result = sympy.simplify(equation)
                summary_lines.append(f"{i}. {equation} = {result}")
            except:
                summary_lines.append(f"{i}. {equation} (invalid arithmetic)")
        else:
            preview = attempt.strip()[:100]
            summary_lines.append(f"{i}. {preview}... (no valid equation found)")
    
    return '\n'.join(summary_lines)


def select_best_failed_attempt(attempts: list, task, idx: int) -> str:
    """
    Select the most promising failed attempt for refinement.
    
    Args:
        attempts: List of failed attempt strings
        task: Task instance
        idx: Problem index
        
    Returns:
        Best attempt string to use for refinement
    """
    if not attempts:
        return ""
    
    scores = [get_attempt_value(task, idx, att) for att in attempts]
    best_idx = np.argmax(scores)
    return attempts[best_idx]


def solve_sequential(args, task, idx, to_print=False):
    """
    Sequential refinement solver: generate → validate → reflect → refine.
    
    Args:
        args: Arguments with backend, temperature, n_generate_sample, max_iterations
        task: Task instance
        idx: Problem index
        to_print: Whether to print debug info
        
    Returns:
        Tuple of (attempts, info_dict)
    """
    global llama
    llama = partial(llama, model=args.backend, temperature=args.temperature)
    
    x = task.get_input(idx)
    max_iterations = args.max_iterations if hasattr(args, 'max_iterations') else 5
    n_samples = args.n_generate_sample
    
    all_attempts = []
    iteration_summaries = []
    infos = []
    
    for iteration in range(max_iterations):
        if iteration == 0:
            prompt = task.natural_prompt_wrap(x)
            attempts = llama(prompt, n=n_samples, stop=None, max_tokens=400)
        else:
            history = '\n'.join([
                f"Iteration {i}: {summary}" 
                for i, summary in enumerate(iteration_summaries)
            ])
            
            last_iteration_attempts = all_attempts[-n_samples:]
            best_failed = select_best_failed_attempt(last_iteration_attempts, task, idx)
            
            prompt = task.refine_prompt_wrap(x, best_failed, reflection, history)
            attempts = llama(prompt, n=n_samples, stop=None, max_tokens=400)
        
        all_attempts.extend(attempts)
        
        results = [task.test_output(idx, attempt) for attempt in attempts]
        successes = [i for i, r in enumerate(results) if r['r'] == 1]
        
        summary = format_attempt_summary(attempts, task, idx)
        iteration_summaries.append(
            f"Tried {len(attempts)} attempts. "
            f"{'SUCCESS!' if successes else 'All failed.'}"
        )
        
        infos.append({
            'iteration': iteration,
            'attempts': attempts,
            'results': results,
            'num_successes': len(successes),
            'summary': summary
        })
        
        if successes:
            successful_attempt = attempts[successes[0]]
            return [successful_attempt], {
                'iterations': iteration + 1,
                'total_attempts': len(all_attempts),
                'success': True,
                'infos': infos
            }
        
        if iteration < max_iterations - 1:
            attempts_str = format_attempt_summary(attempts, task, idx)
            reflection_prompt = task.reflect_prompt_wrap(x, attempts_str)
            reflection = llama(reflection_prompt, n=1, stop=None, max_tokens=300)[0]
    
    best_attempt = select_best_failed_attempt(all_attempts, task, idx)
    
    return [best_attempt], {
        'iterations': max_iterations,
        'total_attempts': len(all_attempts),
        'success': False,
        'infos': infos
    }