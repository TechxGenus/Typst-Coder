# Typst-Coder

<p align="center">
<a href="https://huggingface.co/TechxGenus/Typst-Coder-1.5B">[🤖Models]</a> |
<a href="https://github.com/TechxGenus/Typst-Coder">[🛠️Code]</a> |
<a href="https://huggingface.co/datasets/TechxGenus/Typst-Train">[📊Data]</a> |
</p>

<hr>

- [Typst-Coder](#typst-coder)
  - [Introduction](#introduction)
  - [Environment](#environment)
  - [Usage](#usage)
  - [Models](#models)
  - [Acknowledgements](#acknowledgements)
  - [Contribution](#contribution)

<hr>

## Introduction

While working with Typst documents, we noticed that AI programming assistants often generate poor results. I understand that these assistants may perform better in languages like Python and JavaScript, which benefit from more extensive datasets and feedback signals from executable code, unlike HTML or Markdown. However, current LLMs even frequently struggle to produce accurate Typst syntax, including models like GPT-4o and Claude-3.5-Sonnet.

Upon further investigation, we found that because Typst is a relatively new language, training data for it is scarce. GitHub's search tool doesn't categorize it as a language for code yet, and The Stack v1/v2 don’t include Typst. No open code LLMs currently list it as a supported language, either. To address this, we developed this project aimed at collecting relevant data and training models to improve Typst support in AI programming tools.

## Environment

Please ensure all dependencies are installed using the following command:

```bash
pip install -r requirements.txt
```

We also use [flash-attention](https://github.com/Dao-AILab/flash-attention) for efficient training and [flashinfer](https://github.com/flashinfer-ai/flashinfer) to accelerate inference. See the documents for them to learn how to install.

## Usage

1. Collect repository information
Run `python repos.py` to collect repositories using Typst.

2. Collect corresponding licenses
Run `python licenses.py` to collect corresponding licenses.

3. Collect relevant files
Run `python files.py` to collect corresponding files.

4. Data preprocessing
Run `python preprocess.py` to remove non-permissive licenses and filter according to the method in [Starcoder2]([https](https://arxiv.org/abs/2402.19173)).

5. MinHash deduplication
Run `python minhash_deduplication.py --dataset preprocess.json --output dedup.json` for data deduplication.

6. PII detection
Run `python pii_inference/ner_inference.py --dataset=dedup.json --model_name bigcode/starpii --process_batch_size=100000 --out_path=pii_inference_data` for PII detection.

7. PII redaction
Run `python pii_redaction/main_redact.py --dataset_name pii_inference_data --save_path_disk typst --save_mode local --save_mode_checks local` for PII redaction.

8. Data splitting
Run `python split.py` to split the data into training and testing sets.

Finally, we obtained `typst_train.json`, which includes:

- 18.6K Typst texts
- 2.5K Markdown texts containing Typst-related content

## Models

Our models have been open-sourced on Hugging Face. You can access our models here: [Typst-Coder](https://huggingface.co/TechxGenus/Typst-Coder-1.5B).

We conducted our training based on [Yi-Coder-Chat](https://github.com/01-ai/Yi-Coder), integrating a mix of instruction data to ensure generality and instruction-following capabilities. We did not use [Qwen2.5-Coder series](https://github.com/QwenLM/Qwen2.5-Coder) due to its high initial PPL.

An example script is shown below:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("TechxGenus/Typst-Coder-1.5B")
model = AutoModelForCausalLM.from_pretrained(
    "TechxGenus/Typst-Coder-1.5B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

messages = [
    {"role": "user", "content": "Hi!"},
]
prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

inputs = tokenizer.encode(prompt, return_tensors="pt")
outputs = model.generate(input_ids=inputs.to(model.device), max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
```

## Acknowledgements

The open-source community has been of great help to us, and we reference numerous projects and applications. They include but are not limited to:

[Yi-Coder](https://github.com/01-ai/Yi-Coder), [Bigcode-Project](https://github.com/bigcode-project), ...

## Contribution

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.
