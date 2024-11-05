import re
import json

with open("files.json", "r") as f:
    files = json.load(f)

non_permissive_licenses = [
    "European Union Public License 1.0",
    "European Union Public License 1.1",
    "European Union Public License 1.2",
    "GNU General Public License v1.0",
    "GNU General Public License v2.0",
    "GNU General Public License v3.0",
    "Mozilla Public License 1.0",
    "Mozilla Public License 1.1",
    "Mozilla Public License 2.0",
    "GNU Lesser General Public License v2.1",
    "GNU Lesser General Public License v3.0",
    "GNU Affero General Public License v3.0",
    "EUPL-1.0",
    "EUPL-1.1",
    "EUPL-1.2",
    "GPL-1.0",
    "GPL-2.0",
    "GPL-3.0",
    "MPL-1.0",
    "MPL-1.1",
    "MPL-2.0",
]

def is_permissive_license(f, non_permissive_licenses):
    return f["license"] not in non_permissive_licenses and not any([l in f["content"] for l in non_permissive_licenses])

def is_typst_or_contains_code(f):
    return f["language"] == "typst" or "typst" in f["content"].lower() or "```typ" in f["content"].lower()

def is_within_length_limits(f):
    lines = f["content"].split("\n")
    return len(f["content"]) >= 25 and len(lines) <= 100000 and all(len(line) <= 100000 for line in lines)

def has_sufficient_alphabetic_content(f):
    alphabetic_count = sum(c.isalpha() for c in f["content"])
    return alphabetic_count / len(f["content"]) >= 0.25 if len(f["content"]) > 0 else False

def exclude_auto_generated_files(f):
    auto_generated_phrases = [
        "auto-generated",
        "autogenerated",
        "automatically generated",
        "generated automatically",
        "this file is generated"
    ]
    first_five_lines = "\n".join(f["content"].split("\n")[:5]).lower()
    return not any(phrase in first_five_lines for phrase in auto_generated_phrases)

def exclude_encoded_data(f):
    base64_pattern = re.compile(r'[a-zA-Z0-9+/\n=]{64,}')
    hex_pattern = re.compile(r'(?:\b(?:0x|\\x)?[0-9a-fA-F]{2}(?:,|\b\s*)){8,}')
    unicode_pattern = re.compile(r'(?:\\u[0-9a-fA-F]{4}){8,}')

    base64_matches = base64_pattern.findall(f["content"])
    hex_matches = hex_pattern.findall(f["content"])
    unicode_matches = unicode_pattern.findall(f["content"])

    if any(len(match) > 1024 for match in base64_matches + hex_matches + unicode_matches):
        return False

    if sum(len(match) for match in base64_matches + hex_matches + unicode_matches) / len(f["content"]) > 0.5:
        return False

    return True

def print_filter_stats(stage, files, filtered_files):
    print(f"Stage: {stage}")
    print(f"Before: {len(files)}")
    print(f"After: {len(filtered_files)}")
    print(f"Filtered out: {len(files) - len(filtered_files)}\n")

def apply_filter(files, filter_func, stage_name):
    filtered_files = [f for f in files if filter_func(f)]
    print_filter_stats(stage_name, files, filtered_files)
    return filtered_files

filters = [
    (lambda f: is_permissive_license(f, non_permissive_licenses), "Permissive License"),
    (is_typst_or_contains_code, "Typst or Contains Typst Code"),
    (is_within_length_limits, "Length Limits"),
    (has_sufficient_alphabetic_content, "Sufficient Alphabetic Content"),
    (exclude_auto_generated_files, "Exclude Auto-Generated Files"),
    (exclude_encoded_data, "Exclude Encoded Data")
]

for filter_func, stage_name in filters:
    files = apply_filter(files, filter_func, stage_name)

with open("preprocess.json", "w") as f:
    json.dump(files, f, indent=4)
