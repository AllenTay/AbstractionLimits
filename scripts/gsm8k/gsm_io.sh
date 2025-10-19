#!/bin/bash
################################################################################
# GSM8K Implicit Reasoning Evaluation Script
#
# Purpose:
#   Evaluate language model performance on GSM8K math word problems using
#   standard input-output (IO) prompting without chain-of-thought scaffolding.
#
#
# Usage:
#   ./gsm_io.sh [additional_args]
#
# Example:
#   ./gsm_io.sh --backend llama-3.1-8b-instant
#   ./gsm_io.sh --backend meta-llama/llama-4-scout-17b-16e-instruct
#
# Configuration:
#   - Task: gsm8k (Grade School Math 8K problems)
#   - Problems: 0-1318 (full test set of 1,319 problems)
#   - Method: naive_run (direct IO prompting, no search)
#   - Prompt: standard (minimal instruction overhead)
#   - Samples: 1 per problem (single generation, no self-consistency)
#
#
# Output:
#   Results logged to: ./logs/gsm8k/[backend]_[temp]_naive_standard_sample_1_start0_end1318.json
################################################################################

python run.py \
    --task gsm8k \
    --task_start_index 0 \
    --task_end_index 1318 \
    --naive_run \
    --prompt_sample standard \
    --n_generate_sample 1 \
    ${@}