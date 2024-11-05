import sys
import math
import json
from vllm import LLM, SamplingParams

with open("typst_test.json") as f:
    typst_test = json.load(f)

texts = [sample["content"].strip() for sample in typst_test]

sampling_params = SamplingParams(temperature=0, top_p=1, max_tokens=1, prompt_logprobs=True)
llm = LLM(model=sys.argv[1], gpu_memory_utilization=0.95, max_model_len=100000, enforce_eager=True, trust_remote_code=True, tensor_parallel_size=1)
outputs = llm.generate(texts, sampling_params)

def calculate_logprob(output):
    logprob_sum = sum(
        logprob[prompt_token_id].logprob
        for prompt_token_id, logprob in zip(output.prompt_token_ids[1:], output.prompt_logprobs[1:])
    )
    avg_logprob = logprob_sum / len(output.prompt_token_ids[1:])
    return -avg_logprob

logprobs = [calculate_logprob(output) for output in outputs]
ppl = sum([math.exp(logprob) for logprob in logprobs]) / len(logprobs)
print("Perplexity (PPL):", ppl)
