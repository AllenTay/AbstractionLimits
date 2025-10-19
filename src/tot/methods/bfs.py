import itertools
import numpy as np
from functools import partial
from src.tot.models import llama


def get_value(task, x, y, n_evaluate_sample, cache_value=True):
    """Get value for a single thought."""
    value_prompt = task.value_prompt_wrap(x, y)
    if cache_value and value_prompt in task.value_cache:
        return task.value_cache[value_prompt]
    
    value_outputs = llama(value_prompt, n=n_evaluate_sample, stop=None, max_tokens=200)
    value = task.value_outputs_unwrap(x, y, value_outputs)
    
    if cache_value:
        task.value_cache[value_prompt] = value
    return value


def get_values(task, x, ys, n_evaluate_sample, cache_value=True):
    """Get values for multiple thoughts, with deduplication."""
    values = []
    local_value_cache = {}
    
    for y in ys:
        # Skip exact duplicates within this batch
        if y in local_value_cache:
            values.append(local_value_cache[y])
        else:    
            value = get_value(task, x, y, n_evaluate_sample, cache_value=cache_value)
            local_value_cache[y] = value
            values.append(value)
    
    return values


def get_votes(task, x, ys, n_evaluate_sample):
    """Get votes across multiple thoughts."""
    vote_prompt = task.vote_prompt_wrap(x, ys)
    vote_outputs = llama(vote_prompt, n=n_evaluate_sample, stop=None)
    values = task.vote_outputs_unwrap(vote_outputs, len(ys))
    return values


def get_proposals(task, x, y, n_generate_sample=1): 
    """Generate proposal thoughts from current state."""
    propose_prompt = task.propose_prompt_wrap(x, y)
    raw = llama(propose_prompt, n=n_generate_sample, stop=None, max_tokens=400)[0]
    
    proposals = []
    for line in raw.split('\n'):
        line = line.strip()
        # Valid proposal must have: operation (=), left parenthesis, and at least one operator
        if '=' in line and '(left:' in line and any(op in line for op in ['+', '-', '*', '/']):
            # Clean up the line and append with newline
            proposals.append(y + line + '\n')
    
    # If no valid proposals found, return current state
    return proposals if proposals else [y]


def get_samples(task, x, y, n_generate_sample, prompt_sample, stop):
    """Generate sample continuations from current state."""
    if prompt_sample == 'standard':
        prompt = task.standard_prompt_wrap(x, y)
    else:
        raise ValueError(f'prompt_sample {prompt_sample} not recognized')
    
    samples = llama(prompt, n=n_generate_sample, stop=stop)
    return [y + _ for _ in samples]


def solve(args, task, idx, to_print=False):
    """Main BFS solver for Tree of Thoughts."""
    global llama
    llama = partial(llama, model=args.backend, temperature=args.temperature)
    
    x = task.get_input(idx)
    ys = ['']  # Start with empty thought
    infos = []
    
    for step in range(task.steps):
        # Generate new thoughts
        if args.method_generate == 'sample':
            new_ys = [get_samples(task, x, y, args.n_generate_sample, 
                                 prompt_sample=args.prompt_sample, 
                                 stop=task.stops[step]) for y in ys]
        elif args.method_generate == 'propose':
            new_ys = [get_proposals(task, x, y, args.n_generate_sample) for y in ys]
        
        new_ys = list(itertools.chain(*new_ys))
        ids = list(range(len(new_ys)))
        
        # Evaluate thoughts
        if args.method_evaluate == 'vote':
            values = get_votes(task, x, new_ys, args.n_evaluate_sample)
        elif args.method_evaluate == 'value':
            values = get_values(task, x, new_ys, args.n_evaluate_sample)
        
        # Select best thoughts
        if args.method_select == 'sample':
            ps = np.array(values) / sum(values)
            select_ids = np.random.choice(ids, size=args.n_select_sample, p=ps).tolist()
        elif args.method_select == 'greedy':
            select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:args.n_select_sample]
        
        select_new_ys = [new_ys[select_id] for select_id in select_ids]
        
        # Debug printing
        if to_print: 
            sorted_new_ys, sorted_values = zip(*sorted(zip(new_ys, values), 
                                                       key=lambda x: x[1], 
                                                       reverse=True))
            print(f'-- Step {step} --')
            print(f'New thoughts: {len(new_ys)}')
            print(f'Top 5 values: {sorted_values[:5]}')
            print(f'Selected: {select_new_ys}\n')
        
        infos.append({
            'step': step, 
            'x': x, 
            'ys': ys, 
            'new_ys': new_ys, 
            'values': values, 
            'select_new_ys': select_new_ys
        })
        
        ys = select_new_ys
    
    if to_print: 
        print('Final thoughts:', ys)
    
    return ys, {'steps': infos}


def naive_solve(args, task, idx, to_print=False):
    """Baseline solver without tree search."""
    global llama
    llama = partial(llama, model=args.backend, temperature=args.temperature)
    
    x = task.get_input(idx)
    ys = get_samples(task, x, '', args.n_generate_sample, args.prompt_sample, stop=None)
    
    return ys, {}