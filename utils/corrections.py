import json
import re


def text_to_unique_json(text, output_filename="output.json"):
    words = text.replace("\n", " ").split()
    words = [re.sub(r"[.,;!?(){}\[\]]$", "", word) for word in words]
    words = [word.lower() for word in words]
    unique_words = sorted(set(words), key=words.index)
    json_output = json.dumps(unique_words, ensure_ascii=False)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(json_output)

    return json_output
