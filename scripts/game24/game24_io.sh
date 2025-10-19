#!/bin/bash
################################################################################
# Game of 24 Baseline Evaluation (Input-Output Prompting)
#
# Task: Use 4 numbers with +,-,*,/ to make 24 (each number exactly once)
# Method: Direct IO prompting with few-shot examples
# Problems: 900-999 (100 hard problems from 4nums.com)
# Samples: 10 generations per problem (configurable via --n_generate_sample)
#
# Usage:
#   ./game24_io.sh
#   ./game24_io.sh --backend llama-3.1-8b-instant
#   ./game24_io.sh --n_generate_sample 1
#
# Output: logs/game24/[backend]_[temp]_naive_standard_sample_[n]_start900_end1000.json
################################################################################

python run.py \
    --task game24 \
    --task_start_index 900 \
    --task_end_index 1000 \
    --naive_run \
    --prompt_sample standard \
    --n_generate_sample 10 \
    ${@}