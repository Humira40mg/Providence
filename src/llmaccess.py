import threading
import json
import requests
from tokenizers import Tokenizer
from math import floor
from memoriser import memory, addToMemory, removeFromMemory
from logger import logger

#Getting the conf:
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open(f"ressources/systemprompt.txt", "r", encoding="utf-8") as file:
    sys_prompt = file.read().replace("$ainame", config["ainame"]).replace("$username", config["username"]).replace("$language", config['language'])

tokenizer = Tokenizer.from_file(f"./ressources/{config['model'].split(':')[0]}-tokenizer.json")

class OllamaAccess :
    """ The Object that treat interaction with the LLM. 
    Singleton, so if i extend the project to a voice assistant i don't overload my GPU """
    __instance = None
    __lock = threading.Lock()

    def __init__(self, base_url="http://localhost:11434", model=config["model"]):
        """ Constructor """
        if OllamaAccess.__instance is not None:
            raise Exception("Use get_instance() to get the OllamaClient object.")
        
        self.base_url = base_url
        self.model = model
        self.memory = memory
        self.history = []
        OllamaAccess.__instance = self

    @staticmethod
    def getInstance():
        """to get the singleton"""
        with OllamaAccess.__lock:
            if not OllamaAccess.__instance :
                OllamaAccess()
        return OllamaAccess.__instance


    def generate(self, prompt: str, images: list = None, systemPrompt: str = None) -> str:
        """ Ask AI with the prompt given. Return the response """
        if not systemPrompt:
            systemPrompt = sys_prompt

        with OllamaAccess.__lock:
        
            systemPrompt = self.updateSystemPrompt(systemPrompt)

            # Construire le prompt complet
            conversation = "\n".join(self.history + [f"{config['username']}: {prompt}"])
            
            if len(tokenizer.encode(f"{systemPrompt} {conversation}")) > int(config['contextwindow']) :
                conversation = self.tronkHistory(prompt)

            payload = {
                "model": self.model,
                "system": systemPrompt,
                "prompt": conversation,
                "images": images,
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            if response.ok:
                text = response.json()["response"].strip()
                
                # update history
                self.history.append(f"HISTORY {self.model.upper()}: {text}")
                return text
            else:
                raise Exception(f"Error Ollama API: {response.text}")

    def tronkHistory(self, prompt: str) -> str:
        """ Make the AI forgot the oldest half of the dialogue History """
        self.history = self.history[floor(len(self.history)):]
        logger.info("History tronked.")
        return "\n".join(self.history + [f"{config['username']}: {prompt}"])

    def updateSystemPrompt(self, sysprompt: str) -> str:
        """ Update the system prompt with the current memory """

        #restructuration de la memoire en un str
        data : str = ""
        """ MEMORY IS DISABLE FOR THE MOMENT
        for value in self.memory.values() :
            data += value + " "
        """

        return f"{sysprompt} {data}"
    