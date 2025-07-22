import json
from fuzzywuzzy import fuzz
from os import makedirs

makedirs("data", exist_ok=True)

with open("data/memory.json", "r", encoding="utf-8") as f:
    memory = json.load(f)

def addToMemory(data):
    memory[len(memory.keys())] = data
    write()

def removeFromMemory(data):
    for key, value in memory.items():
        ratio = fuzz.ratio(value.strip().lower(), data.strip().lower())
        if ratio >= 75:
            del memory[key]
            write()

def write():
    with open("data/memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)