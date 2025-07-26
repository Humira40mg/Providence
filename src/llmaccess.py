import threading
import json
import requests
from math import floor
from memoriser import memory, addToMemory, removeFromMemory
from logger import logger

#Getting the conf:
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open(f"ressources/systemprompt.txt", "r", encoding="utf-8") as file:
    sys_prompt = file.read().replace("$ainame", config["ainame"]).replace("$username", config["username"]).replace("$language", config['language'])

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
            conversation = "\n".join(["Current History of your messages :\n ["] + self.history + ["]"] + [f"Informations fetched on {config['username']}'s screen and other sources : [{prompt}]"])
            #conversation = "\n".join([f"{config['username']}: {prompt}"]) #history disable if this line is used

            if len(f"{systemPrompt} {conversation}".split()) > (int(config['contextwindow']) // 2):
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
                self.history.append(f"HISTORY {config['ainame'].upper()}: {text}")
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

        #restructuration of memory in a string
        data : str = ""
        
        for key, value in self.memory.items() :
            data += f"[{key} : {value}], "

        return f"{sysprompt} Informations saved in memory are : [{data}]"
    