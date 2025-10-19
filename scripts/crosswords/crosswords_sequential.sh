#!/bin/bash
################################################################################
# Mini Crosswords Sequential Refinement Evaluation
#
# Method: Iterative generate → validate → reflect → refine loop
# - Generate: Natural problem-solving with explicit format requirements
# - Validate: Check word-level and letter-level correctness
# - Reflect: Analyze constraint conflicts and word intersections
# - Refine: Generate improved solutions based on reflection
#
# Config:
#   - Max iterations: 10 (stop early if solution found)
#   - Samples per iteration: 3
#   - Temperature: 0.3
#   - Problems: 0-19 (test games at indices 0, 5, 10, ..., 95)
#
# Usage:
#   ./crosswords_sequential.sh
#   ./crosswords_sequential.sh --max_iterations 5
#   ./crosswords_sequential.sh --temperature 0.7
#
# Output: logs/crosswords/[backend]_[temp]_sequential_sample3_iter10_start0_end20.json
################################################################################

python run.py \
    --task crosswords \
    --task_start_index 0 \
    --task_end_index 2 \
    --method sequential \
    --n_generate_sample 3 \
    --max_iterations 10 \
    --backend meta-llama/llama-4-maverick-17b-128e-instruct \
    --temperature 0.7