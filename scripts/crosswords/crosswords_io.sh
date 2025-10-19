#!/bin/bash
################################################################################
# Mini Crosswords Baseline Evaluation (Input-Output Prompting)
#
# Task: Solve 5x5 crosswords given 5 horizontal and 5 vertical clues
# Method: Direct IO prompting with 5 few-shot examples
# Problems: 0-1 (first 2 test games: actual indices 0, 5)
# Samples: 10 generations per problem (configurable via --n_generate_sample)
#
# Usage:
#   ./crosswords_io.sh
#   ./crosswords_io.sh --backend llama-3.1-8b-instant
#   ./crosswords_io.sh --n_generate_sample 5
#
# Output: logs/crosswords/[backend]_[temp]_naive_standard_sample_[n]_start0_end2.json
################################################################################

python run.py \
    --task crosswords \
    --task_start_index 0 \
    --task_end_index 2 \
    --naive_run \
    --prompt_sample standard \
    --n_generate_sample 10 \
    ${@}