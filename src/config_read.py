import yaml
from os import path

DEFAULT_CONFIG = {
    "variables": {
        "ainame": "Providence",
        "username": "JoKSo",
        "language": "français"
    },
    "llm": {
        "model": "qwen3-vl:4b-instruct",
        "contextwindow": 256000,
        "vision": True,
        "thinking": False
    },
    "api": {
        "port": 4242
    },
    "tokens": {
        "picovoice": "",
        "google": {
            "api": "",
            "cx": ""
        }
    }
}

if not path.exists("config.yml"):
    with open("config.yml", "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
    print("config.yml créé. Remplis les valeurs avant de relancer.")

#Getting the conf:
with open("config.yml", "r", encoding="utf-8") as file:
    config = data = yaml.safe_load(file)

texthistory = []

AINAME = config["variables"]["ainame"]
USERNAME = config["variables"]["username"]
LANGUAGE = config["variables"]["language"]

MODEL = config["llm"]["model"]
CTXWIN = config["llm"]["contextwindow"]
VISION = config["llm"]["vision"]
THINKING = config["llm"]["thinking"]

PORT = config["api"]["port"]

PICOVOICE_KEY = config["tokens"]["picovoice"]
GOOGLE_API_KEY = config["tokens"]["google"]["api"]
GOOGLE_CX = config["tokens"]["google"]["cx"]