import os
import json
import argparse

from src.tot.tasks import get_task
from src.tot.methods.bfs import solve, naive_solve
from src.tot.methods.sequential import solve_sequential
from src.tot.models import llama_usage

def run(args):
    task = get_task(args.task)
    logs, cnt_avg, cnt_any = [], 0, 0
    
    if args.naive_run:
        file = f'./logs/{args.task}/{args.backend.replace("/", "_")}_{args.temperature}_naive_{args.prompt_sample}_sample_{args.n_generate_sample}_start{args.task_start_index}_end{args.task_end_index}.json'
    elif args.method == 'sequential':
        file = f'./logs/{args.task}/{args.backend.replace("/", "_")}_{args.temperature}_sequential_sample{args.n_generate_sample}_iter{args.max_iterations}_start{args.task_start_index}_end{args.task_end_index}.json'
    elif args.method == 'dfs':
        file = f'./logs/{args.task}/{args.backend.replace("/", "_")}_{args.temperature}_dfs_start{args.task_start_index}_end{args.task_end_index}.json'
    else:
        file = f'./logs/{args.task}/{args.backend.replace("/", "_")}_{args.temperature}_{args.method_generate}{args.n_generate_sample}_{args.method_evaluate}{args.n_evaluate_sample}_{args.method_select}{args.n_select_sample}_start{args.task_start_index}_end{args.task_end_index}.json'
    
    os.makedirs(os.path.dirname(file), exist_ok=True)

    for i in range(args.task_start_index, args.task_end_index):
        # solve
        if args.naive_run:
            ys, info = naive_solve(args, task, i) 
        elif args.method == 'sequential':
            ys, info = solve_sequential(args, task, i, to_print=True)
        else:
            ys, info = solve(args, task, i)

        # log
        infos = [task.test_output(i, y) for y in ys]
        info.update({'idx': i, 'ys': ys, 'infos': infos, 'usage_so_far': llama_usage(args.backend)})
        logs.append(info)
        with open(file, 'w') as f:
            json.dump(logs, f, indent=4)
        
        # log main metric
        accs = [info['r'] for info in infos]
        cnt_avg += sum(accs) / len(accs)
        cnt_any += any(accs)
        print(i, 'sum(accs)', sum(accs), 'cnt_avg', cnt_avg, 'cnt_any', cnt_any, '\n')
    
    n = args.task_end_index - args.task_start_index
    print(cnt_avg / n, cnt_any / n)
    print('usage_so_far', llama_usage(args.backend))


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--backend', type=str, choices=['llama-3.1-8b-instant', 'meta-llama/llama-4-scout-17b-16e-instruct','meta-llama/llama-4-maverick-17b-128e-instruct', 'llama-3.3-70b-versatile'], default='meta-llama/llama-4-scout-17b-16e-instruct')
    args.add_argument('--temperature', type=float, default=0.7)

    args.add_argument('--task', type=str, required=True, choices=['gsm8k', 'game24', 'crosswords'])
    args.add_argument('--task_start_index', type=int, default=0)
    args.add_argument('--task_end_index', type=int, default=100)

    args.add_argument('--naive_run', action='store_true')
    args.add_argument('--prompt_sample', type=str, choices=['standard'], default='standard')

    args.add_argument('--method', type=str, choices=['bfs', 'dfs', 'sequential'], default='bfs')
    args.add_argument('--method_generate', type=str, choices=['sample', 'propose'], default='propose')
    args.add_argument('--method_evaluate', type=str, choices=['value'], default='value')
    args.add_argument('--method_select', type=str, choices=['sample', 'greedy'], default='greedy')
    args.add_argument('--n_generate_sample', type=int, default=1)
    args.add_argument('--n_evaluate_sample', type=int, default=1)
    args.add_argument('--n_select_sample', type=int, default=1)
    
    args.add_argument('--value_threshold', type=float, default=0.5)
    
    # Sequential refinement specific
    args.add_argument('--max_iterations', type=int, default=5, help='Max refinement iterations for sequential method')

    args = args.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    print(args)
    run(args)