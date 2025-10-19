# Abstraction Limits in Medium Sized Open Source LLMs: Contrasting Deliberate Search and Iterative Refinement

## Overview

This repository documents a comparative study of deliberate search mechanisms, specifically the Tree of Thoughts (ToT) framework, and an adapted Sequential Refinement methodology, applied to modern open-weight language models, including Llama 3.1 8B and Llama 4 Scout. The original ToT framework was introduced to augment models (like GPT-4 in early 2023) that were constrained to token-level, left-to-right decision-making, enabling them to generalize Chain-of-Thought (CoT) prompting by searching over "coherent units of text ('thoughts')". Our research addresses a critical gap: when models already possess some level of internal reasoning, does complex deliberate search provide benefits, or does it introduce constraints that hinder performance?.

Llama 4 Scout demonstrated a strong baseline in mathematical reasoning (33% single-shot success on Game of 24). However, the model completely failed the Tree of Thoughts protocol (0% success) due to instruction-following limitations imposed by rigid formatting. This suggests that for some modern, capable models, iteration with reflection may be more effective than exploration through search.

## Research Questions

This study was designed to investigate the limits and optimal deployment strategies for small to medium sized modern LLMs in problem-solving applications:
1. How do Llama 3.1 8B and Llama 4 Scout compare on mathematical reasoning tasks?
2. Does Tree of Thoughts' deliberate search improve upon Scout's internal reasoning capabilities? 
3. How do key design choices (number of iterations, reflection strategy depth, temperature settings) affect sequential refinement performance?
4. What are the performance-cost tradeoffs between tree search and iterative refinement?
5. What task complexity (abstraction limits) reveals the fundamental constraints of these models?

## Study Design and Methodology

We evaluated methods across three tasks designed to challenge systematic planning or search.

| Task | Domain | Thought Step Decomposition | Baseline Performance Objective | Methods Compared |
| :--- | :--- | :--- | :--- | :--- |
| **GSM8K** (1,319 problems) | Multi-step arithmetic | N/A (Zero-shot) | Establish core reasoning capabilities | Zero-shot IO (Llama 3.1 8B, Llama 4 Scout) |
| **Game of 24** (100 hard problems) | Deductive math, planning | 3 intermediate equations | Test transfer of ToT, evaluate cost/performance | Implicit/Explicit IO, CoT, Sequential Refinement, ToT (BFS) |
| **Mini Crosswords** (20 games) | Lexical reasoning, constraint satisfaction | Words to fill in for clues | Test high-density constraint limits | Implicit IO, Sequential Refinement, ToT (DFS) |


## Key Findings and Analytical Results

### 1. Strong Baseline Reasoning Established

Llama 4 Scout exhibited strong performance on baseline reasoning tasks, justifying the shift in focus from basic reasoning augmentation to efficiency and constraint handling:

* **GSM8K**: Scout achieved 91.10% accuracy (1201/1318) zero-shot, compared to Llama 3.1 8B's 71.09%. The authors of the ToT paper reported 51% and 90% for GPT-4 using zero shot IO and ToT respectively.
* **Game of 24**: Scout’s single-shot Implicit IO success rate was 33%, significantly exceeding GPT-4's 4.0% with CoT prompting, the context for which ToT was initially developed. Scout achieved 82% success with just 10 samples ($n=10$), a level GPT-4 could not match with 100 samples.

### 2. Instruction-Following: The Abstraction Bottleneck

The layered protocols necessary for implementing the classic ToT search algorithm caused complete failure in Llama 4 Scout:

* **ToT Complete Failure**: Tree of Thoughts (BFS, $b=5,3,1$) yielded 0% success on Game of 24 regardless of temperature, beam or sample size variation.
* **Possible Root Cause**: This performance drop (from 33% baseline to 0%) demonstrates that Scout’s limitation lies in its inability to follow fine-tuned multi-turn instructions (e.g., specific proposal formats, scalar value evaluation, state management across steps), rather than a failure of core reasoning.
* **Explicit Constraints Degrade Performance**: Explicit IO prompting (as seen in the ToT paper) achieved only 27% success (n=10), whereas Implicit IO (flexible format) achieved 82% success (n=10). This indicates that constraining Scout's natural problem-solving degrades performance.

### 3. Iterative Refinement Outperforms Deliberate Search

Since complex search protocols failed, Sequential Refinement, which uses flexible prompting, automatic validation, and focused reflection, was developed as an alternative:

* **Performance**: The best Sequential Refinement configuration (k=5, n=5) achieved 85% success. The highly efficient configuration (k=5, n=3, brief reflection) achieved 84% success. This performance exceeds the original GPT-4+ToT score of 74%.
* **Design Insight**: Brief reflection (3 questions) beat detailed reflection (4 steps): 84% vs 71%. This suggests the model requires focused, actionable error identification, not verbose analysis, for effective self-correction.
* **Llama 3.1 8B**: Sequential refinement provided no benefit to the smaller Llama 3.1 8B (14% success vs 15% baseline), indicating that a sufficient base reasoning capability is prerequisite for iterative refinement to be effective.

### 4. Task Abstraction Limits in Crosswords

Mini Crosswords, a task requiring simultaneous satisfaction of 10 interdependent word and letter constraints, revealed a fundamental abstraction capacity limit:

* Regardless of the method used (Implicit IO or Sequential Refinement), performance remained near 0% word-level success.
* This suggests that prompting methods cannot overcome task complexity limits when the abstraction required (e.g., managing high-density, interdependent constraints) is beyond the model's inherent capability.

## Practical Implications and Recommendations

The issue with applying complex search methods to models like Llama 4 Scout is rooted in instruction-following rigidity, not capacity for reasoning. The central finding is that for models possessing strong inherent reasoning, allowing flexibility through iteration (generating multiple answers or refinement) is superior to forcing compliance with complex, explicit search frameworks.

The original Tree of Thoughts (ToT) framework significantly improved models like GPT-4 on Game of 24, increasing success from 4.0% (Chain-of-Thought) to 74%. However, the less monolithic, yet still capable, Llama 4 Scout (which has a 33% single-shot Implicit Input/Output baseline) failed completely (0% success) when attempting the ToT search protocol. This failure occurred because the model could not adhere to the rigid, fine-tuned, multi-turn instructions necessary for state evaluation and proposal formatting required by the deliberate search abstraction.

In contrast, Sequential Refinement, which utilizes flexible prompting for iterative correction and focused reflection, achieved up to 85% success for Llama 4 Scout. This supports the conclusion that when a model has sufficient internal reasoning, allowing it to generate answers multiple times or iteratively refine them proves more effective than constraining its natural problem-solving process with complex search instructions.

Practical Implications: Search vs. Iteration
The following table summarizes the performance-cost trade-offs, demonstrating that flexible, iterative methods offer superior efficiency compared to complex search mechanisms for models with strong internal reasoning, like Llama 4 Scout. Tree of Thoughts is not recommended for models exhibiting strong internal reasoning but rigid instruction-following limits.

| Priority | Method | Success@1 (Game of 24) | Calls/Solution | Efficiency (Success% / Calls) | Why Recommended |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cost** | Implicit IO (n=10) | 82% | 12.2 | 6.72 | Highest efficiency; relies on natural reasoning, avoids instruction limits. |
| **Balance** | Sequential (k=5, n=3, brief) | 84% | 17.9 | 4.69 | Near-optimal performance; marginal gain justifies cost. |
| **Performance** | Sequential (k=5, n=5) | 85% | 29.4 | 2.89 | Highest success, but marginal gain is achieved at significant cost increase. |

**Recommendation for Deployment**: Use Implicit IO ($n=10$) for cost-sensitive applications. If marginal improvement is required, switch to Sequential Refinement (k=5, n=3, brief). Tree of Thoughts is not recommended for models exhibiting strong internal reasoning but rigid instruction-following limits.

## Resources and Citation

The research documented here is built upon and compares against the Tree of Thoughts framework.

**Codebase**: The original Tree of Thoughts implementation, on which this research built, is available: https://github.com/princeton-nlp/tree-of-thought-llm
**Models**: Experiments utilized the Groq API for Llama 3.1 8B and Llama 4 Scout models.

**Citation**: The original framework is: Yao, S., et al. (2023). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. Advances in Neural Information Processing Systems (NeurIPS 2023).