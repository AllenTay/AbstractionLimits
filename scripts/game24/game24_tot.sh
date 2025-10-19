#!/bin/bash
################################################################################
# Game of 24 Tree of Thoughts (BFS) Evaluation
#
# Method: Breadth-first search over thought trees
# - Propose: Generate candidate next steps (intermediate equations)
# - Evaluate: Score each step 1-10 based on progress toward 24
# - Select: Keep top b most promising states per depth
#
# Tree structure: 3 steps (each step combines 2 numbers)
#   Depth 0: 4 numbers
#   Depth 1: 3 numbers (after combining 2)
#   Depth 2: 2 numbers
#   Depth 3: 1 number (should be 24)
#
# Config:
#   - Breadth limit: n (keep top n states per step)
#   - Proposal samples: 5 per state
#   - Value samples: n evaluations per thought
#
# Usage:
#   ./game24_tot.sh
#   ./game24_tot.sh --n_select_sample 3
#
# Output: logs/game24/[backend]_[temp]_propose5_value3_greedy5_start900_end920.json
################################################################################

python run.py \
    --task game24 \
    --task_start_index 900 \
    --task_end_index 920 \
    --method_generate propose \
    --method_evaluate value \
    --method_select greedy \
    --n_evaluate_sample 3 \
    --n_select_sample 5