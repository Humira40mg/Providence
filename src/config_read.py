import yaml

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