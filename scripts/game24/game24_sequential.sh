#!/bin/bash
################################################################################
# Game of 24 Sequential Refinement Evaluation
#
# Method: Iterative generate → validate → reflect → refine loop
# - Generate: Create solutions using natural problem-solving prompt
# - Validate: Check if solution is correct
# - Reflect: Analyze failure patterns across attempts
# - Refine: Generate improved solutions based on reflection
#
# Config:
#   - Max iterations: 5 (stop early if solution found)
#   - Samples per iteration: 3
#   - Temperature: 0.7
#
# Usage:
#   ./game24_sequential.sh
#   ./game24_sequential.sh --max_iterations 10
#
# Output: logs/game24/[backend]_[temp]_sequential_sample3_iter5_start900_end1000.json
################################################################################

python run.py \
    --task game24 \
    --task_start_index 900 \
    --task_end_index 1000 \
    --method sequential \
    --n_generate_sample 3 \
    --max_iterations 5 \
    --backend meta-llama/llama-4-scout-17b-16e-instruct \
    --temperature 0.7