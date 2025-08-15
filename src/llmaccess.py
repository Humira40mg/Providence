from generationlock import generationLock
import json
import requests
from math import floor
from memoriser import memory, addToMemory, removeFromMemory
from logger import logger
import Tools
from parser import parseEyeResponse

#Getting the conf:
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open(f"ressources/systemprompt.txt", "r", encoding="utf-8") as file:
    sys_prompt = file.read().replace("$ainame", config["ainame"]).replace("$username", config["username"]).replace("$language", config['language'])

toolList = {"Eyes": [], "N/A": []}
for toolname in Tools.__all__ :
    tool = getattr(Tools, toolname)
    tool = tool()
    toolList["N/A"].append(tool.ollamaFormat())
    if tool.hidden == "Eyes" : continue
    toolList["Eyes"].append(tool.ollamaFormat())

sys_prompt += f"\n[AVAILABLE_TOOLS]{str(toolList)}[/AVAILABLE_TOOLS]"

class OllamaAccess :
    """ The Object that treat interaction with the LLM. 
    Singleton, so if i extend the project to a voice assistant i don't overload my GPU """
    __instance = None

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
        with generationLock:
            if not OllamaAccess.__instance :
                OllamaAccess()
        return OllamaAccess.__instance


    def chat(self, prompt: str, useTools: bool = True, selfprompt: bool= False, hiddenTools: str = "N/A", think = False) -> str:
        """ Ask AI with the prompt given. Return the response """
        generationLock.acquire()
        
        systemPrompt = self.updateSystemPrompt(sys_prompt)

        # Construire le prompt complet
        self.history.append({"role": "user", "content": prompt})

        if len(f"{systemPrompt} {str(self.history)}".split()) > (int(config['contextwindow']) // 2):
            self.tronkHistory()

        logger.info({"role": "user", "content": prompt})
        
        payload = {
                "model": self.model,
                "messages": [{"role": "system", "content": systemPrompt}] + self.history,
                "think": think,
                "stream": False
            }
        
        if useTools:
            payload["tools"] = toolList[hiddenTools]
            payload["tool_choice"] = "auto"
        
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        if response.ok:
            try:
                data = response.json()
                text = data["message"]
                logger.info(data["message"])
                
                # update history
                self.history.append(data["message"])

                recursiveanswer = parseEyeResponse(text)

                if generationLock.locked() :
                    generationLock.release()

                if not selfprompt or not recursiveanswer or (recursiveanswer and len(recursiveanswer) < 20) : return
                
                self.chat(f"Voici les réponses données par les outils appelés :\n {recursiveanswer}. Tu peux maintenant répondre avec en utilisant la fonction d'intervention pour répondre à la question original {prompt}.")

            except ValueError:
                logger.error("Error : non JSON response")
                logger.warn("Content :", response.text)
        else:
            logger.error(f"Error Ollama API: {response.text}")
        
        #security unlock in case of anything going wrong
        if generationLock.locked() :
            generationLock.release()
            
    def tronkHistory(self):
        """ Make the AI forgot the oldest half of the dialogue History """
        self.history = self.history[floor(len(self.history)/2):]
        logger.info("History tronked.")

    def updateSystemPrompt(self, sysprompt: str) -> str:
        """ Update the system prompt with the current memory """
        #restructuration of memory in a string
        return f"{sysprompt} Informations saved in your long term memory are : [{str(self.memory)}]"
    