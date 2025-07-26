import json
from fuzzywuzzy import fuzz
from os import path, makedirs

makedirs("data", exist_ok=True)

if not path.exists("data/memory.json"):
    with open("data/memory.json", 'w') as f:
        f.write("{}") 

with open("data/memory.json", "r", encoding="utf-8") as f:
    memory = json.load(f)

def addToMemory(data):
    memory[len(memory.keys())] = data
    write()

def removeFromMemory(data):
    supposition = ""
    for char in data:
        if char.isdigit():
            supposition += char

    for key, value in memory.items():

        if int(supposition) == int(key):
            del memory[key]
            write()

def write():
    with open("data/memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)