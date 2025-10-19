import os
import backoff
from groq import Groq
from typing import List, Dict, Optional

# Global token tracking
completion_tokens = 0
prompt_tokens = 0

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY", "")
if api_key != "":
    client = Groq(api_key=api_key)
else:
    print("Warning: GROQ_API_KEY is not set")
    client = None


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def completions_with_backoff(**kwargs) -> object:
    """
    Make API call with exponential backoff retry logic.
    
    Args:
        **kwargs: Arguments to pass to Groq chat completion API
        
    Returns:
        Groq chat completion response object
        
    Raises:
        Exception: If all retry attempts fail
    """
    if client is None:
        raise ValueError("Groq client not initialized. Set GROQ_API_KEY environment variable.")
    return client.chat.completions.create(**kwargs)


def llama(prompt: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct", temperature: float = 0.7, max_tokens: int = 1000, n: int = 1, stop: Optional[List[str]] = None) -> List[str]:
    """
    Generate completions using Llama 4 Maverick via Groq.
    
    Args:
        prompt: The input prompt text
        model: Model name (default: "meta-llama/llama-4-scout-17b-16e-instruct")
        temperature: Sampling temperature between 0 and 2 (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 1000)
        n: Number of completions to generate (default: 1)
        stop: Optional list of stop sequences
    
    Returns:
        List of generated text completions
        
    Example:
        >>> responses = llama("What is 2+2?", n=3)
        >>> print(responses[0])
    """
    messages = [{"role": "user", "content": prompt}]
    return chat_llama(messages, model=model, temperature=temperature, max_tokens=max_tokens, n_args=n, stop=stop)


def chat_llama(
    messages: List[Dict[str, str]], 
    model: str = "llama-3.1-8b-instant", 
    temperature: float = 0.7, 
    max_tokens: int = 1000, 
    n_args: int = 1, 
    stop: Optional[List[str]] = None
) -> List[str]:
    """
    Generate chat completions using Llama 4 Maverick via Groq.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
                 Example: [{"role": "user", "content": "Hello"}]
        model: Model name (default: "meta-llama/llama-4-scout-17b-16e-instruct")
        temperature: Sampling temperature between 0 and 2 (default: 0.7)
        max_tokens: Maximum tokens to generate (default: 1000)
        n: Number of completions to generate (default: 1)
        stop: Optional list of stop sequences
    
    Returns:
        List of generated text completions
        
    Note:
        - Groq API requires n=1 per call, so this function makes n sequential calls
        - Global token counters (completion_tokens, prompt_tokens) are updated
        - Exponential backoff retry is applied automatically
        
    Example:
        >>> messages = [{"role": "user", "content": "Solve: 2+2=?"}]
        >>> responses = chat_llama(messages, n=5)
        >>> print(len(responses))  # 5
    """
    global completion_tokens, prompt_tokens
    outputs = []
    
    for _ in range(n_args):
        res = completions_with_backoff(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            stop=stop
        )
        outputs.extend([choice.message.content for choice in res.choices])
        
        # Update global token tracking
        if res.usage:
            completion_tokens += res.usage.completion_tokens
            prompt_tokens += res.usage.prompt_tokens
            
    return outputs


def llama_usage(backend: str = "llama-3.1-8b-instant") -> Dict[str, float]:
    """
    Calculate token usage and estimated cost for Llama 3.1 8B via Groq.
    
    Args:
        backend: Model name for cost calculation (default: "llama-3.1-8b-instant")
    
    Returns:
        Dictionary with:
            - 'completion_tokens': Total completion tokens used
            - 'prompt_tokens': Total prompt tokens used  
            - 'cost': Estimated cost in USD
            
    Cost Structure for Llama 3.1 8B Instant:
        - Input: $0.05 per 1M tokens
        - Output: $0.08 per 1M tokens
        
    Example:
        >>> usage = llama_usage()
        >>> print(f"Cost so far: ${usage['cost']:.4f}")
        >>> print(f"Tokens used: {usage['prompt_tokens']} input, {usage['completion_tokens']} output")
    """
    global completion_tokens, prompt_tokens
    
    # Groq pricing for Llama 3.1 8B Instant (per 1M tokens)
    input_price_per_1m = 0.11
    output_price_per_1m = 0.34
    
    # Calculate cost (tokens / 1M * price per 1M)
    cost = (
        (completion_tokens / 1000000) * output_price_per_1m +
        (prompt_tokens / 1000000) * input_price_per_1m
    )
    
    return {
        "completion_tokens": completion_tokens,
        "prompt_tokens": prompt_tokens,
        "cost": cost
    }


def reset_usage() -> None:
    """
    Reset global token counters to zero.
    
    Useful for:
        - Starting fresh tracking for a new experiment
        - Measuring cost for specific task subsets
        - Debugging token consumption
        
    Example:
        >>> reset_usage()
        >>> # Run experiment on 100 problems
        >>> usage = llama_usage()
        >>> print(f"This experiment cost: ${usage['cost']:.4f}")
    """
    global completion_tokens, prompt_tokens
    completion_tokens = 0
    prompt_tokens = 0