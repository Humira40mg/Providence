import threading
import json
import requests
from tokenizers import Tokenizer
from math import floor
from memoriser import memory, addToMemory, removeFromMemory

tokenizer = Tokenizer.from_file("./ressources/tokenizer.json")

#Getting the conf:
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open(config["systempromptPath"], "r", encoding="utf-8") as file:
    sys_prompt = file.read().replace("$ainame", config["ainame"]).replace("$username", config["username"])

class OllamaAccess :

    __instance = None
    __lock = threading.Lock()

    def __init__(self, base_url="http://localhost:11434", model="mistral"):
        if OllamaAccess.__instance is not None:
            raise Exception("Use get_instance() to get the OllamaClient object.")
        
        self.base_url = base_url
        self.model = model
        self.memory = memory
        self.history = []
        OllamaAccess.__instance = self


    #Pour recupérer le singleton
    @staticmethod
    def getInstance() :

        with OllamaAccess.__lock:
            if not OllamaAccess.__instance :
                OllamaAccess()
        return OllamaAccess.__instance


    def generate(self, prompt, systemPrompt = None):

        if not systemPrompt:
            systemPrompt = sys_prompt

        with OllamaAccess.__lock:

            systemPrompt = self.updateSystemPrompt(systemPrompt)

            # Construire le prompt complet
            conversation = "\n".join(self.history + [f"{config["username"]}: {prompt}"])
            
            if len(tokenizer.encode(f"{systemPrompt} {conversation}")) > 4096 :
                conversation = self.tronkHistory(prompt)

            payload = {
                "model": self.model,
                "system": systemPrompt,
                "prompt": conversation,
                "stream": False
            }
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            if response.ok:
                text = response.json()["response"].strip()
                # Mettre à jour l’historique
                self.history.append(f"HISTORY USER: {prompt}")
                self.history.append(f"HISTORY {self.model.upper()}: {text}")
                return text
            else:
                raise Exception(f"Error Ollama API: {response.text}")


    def tronkHistory(self, prompt) :
        self.history = self.history[floor(len(self.history)):]
        logger.info("History tronked.")
        return "\n".join(self.history + [f"{config["username"]}: {prompt}"])

    def updateSystemPrompt(self, sysprompt):
        #restructuration de la memoire en un str
        data : str = ""
        for value in self.memory.values() :
            data += value + " "

        return f"{sysprompt} {data}"
    