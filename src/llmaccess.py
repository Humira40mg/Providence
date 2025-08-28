from generationlock import generationLock
import json
import requests
from math import floor
from memoriser import memory, addToMemory, removeFromMemory
from logger import logger
import Tools
from parser import parseEyeResponse
from config_read import config, texthistory

with open(f"ressources/systemprompt.txt", "r", encoding="utf-8") as file:
    sys_prompt = file.read().replace("$ainame", config["ainame"]).replace("$username", config["username"]).replace("$language", config['language'])

toolList = {"Eyes": [], "Chat": [], "N/A": []}
for toolname in Tools.__all__ :
    tool = getattr(Tools, toolname)
    tool = tool()
    toolList["N/A"].append(tool.ollamaFormat())

    if tool.hidden != "Eyes" :
        toolList["Eyes"].append(tool.ollamaFormat())
    
    if tool.hidden != "Chat" :
        toolList["Chat"].append(tool.ollamaFormat())

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


    def chat(self, prompt: str, useTools: bool = True, selfprompt: bool= False, hiddenTools: str = "N/A", think = False, toolresponse = None, images: list = None, notextlog: bool = False) -> str:
        """ Ask AI with the prompt given. Return the response """
        generationLock.acquire()
        
        systemPrompt = self.updateSystemPrompt(sys_prompt)
        
        if not toolresponse :
            # Construire le prompt complet
            self.history.append({"role": "user", "content": prompt})
            if not notextlog:
                texthistory.append({"role": "user", "content": prompt})
            logger.info({"role": "user", "content": prompt})

        elif len(toolresponse) > 0:
            for response in toolresponse:
                self.history.append(response)
                logger.info(response)

        if len(f"{systemPrompt} {str(self.history)}".split()) > (int(config['contextwindow']) // 2):
            self.tronkHistory()
        
        payload = {
                "model": self.model,
                "messages": [{"role": "system", "content": systemPrompt}] + self.history,
                "think": think,
                "images": images,
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

                if not selfprompt or len(recursiveanswer) == 0 : return
                
                self.chat("", toolresponse=recursiveanswer)

            except ValueError:
                logger.error("Error : non JSON response")
                logger.warn("Content :", response.text)
        else:
            logger.error(f"Error Ollama API: {response.text}")
        
        #security unlock in case of anything going wrong
        if generationLock.locked() :
            generationLock.release()

    def textchat(
        self, 
        prompt: str, 
        selfprompt: bool = False, 
        hiddenTools: str = "Chat", 
        think: bool = False, 
        toolresponse: list = None, 
        images: list = None
        ):
        """
        Ask AI with the prompt given. Always streaming. 
        Handles tools, self-prompt recursion, and history.
        Returns a generator for streaming.
        """

        generationLock.acquire()  # Bloque pour éviter génération simultanée

        try:
            systemPrompt = self.updateSystemPrompt(sys_prompt)

            # Construction de l'historique
            if not toolresponse:
                self.history.append({"role": "user", "content": prompt})
                texthistory.append({"role": "user", "content": prompt})
                logger.info({"role": "user", "content": prompt})
            else:
                for resp in toolresponse:
                    self.history.append(resp)
                    logger.info(resp)

            # Tronque l'historique si trop long
            if len(f"{systemPrompt} {str(self.history)}".split()) > (int(config['contextwindow']) // 2):
                self.tronkHistory()

            # Prépare le payload pour Ollama
            payload = {
                "model": self.model,
                "messages": [{"role": "system", "content": systemPrompt}] + self.history,
                "think": think,
                "images": images,
                "tools": toolList.get(hiddenTools, []),
                "tool_choice": "auto",
                "stream": True
            }
            # Envoie la requête
            response = requests.post(f"{self.base_url}/api/chat", json=payload, stream=True)

            def generate():
                full_text = ""
                toolcalls = []  
                try:
                    # Streamer la réponse
                    for line in response.iter_lines(decode_unicode=True):
                        if line:
                            text = line.decode("utf-8") if isinstance(line, bytes) else line
                            yield text      # envoi immédiat au front-end

                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                full_text += content
                                if data.get("message", {}).get("tool_calls") :
                                    toolcalls += data.get("message", {}).get("tool_calls") 
                            except json.JSONDecodeError:
                                # parfois le chunk n'est pas complet, ignore
                                continue

                    # Libérer le lock
                    if generationLock.locked():
                        generationLock.release()

                    # Traiter la réponse complète après streaming
                    #try:
                    dico = {"role":"assistant", "content":full_text, "tool_calls": toolcalls}
                    logger.info(dico)

                    # Mettre à jour l'historique
                    self.history.append(dico)
                    texthistory.append(dico)

                    # Analyse pour selfprompt
                    recursiveanswer = parseEyeResponse(dico)

                    # Déclenche récursion uniquement si selfprompt ET tools utilisés
                    if selfprompt and len(recursiveanswer) > 0:
                        yield from self.textchat("", toolresponse=recursiveanswer)()

                    #except Exception as e:
                        #logger.warn(f"Impossible d’analyser la réponse finale : {e}")

                finally:
                    # Sécurité : déverrouiller le lock si jamais
                    if generationLock.locked():
                        generationLock.release()

            return generate

        except Exception as e:
            # Sécurité : libération lock en cas d'erreur
            if generationLock.locked():
                generationLock.release()
            logger.error("Erreur textchat:", e)
            raise

            
    def tronkHistory(self):
        """ Make the AI forgot the oldest half of the dialogue History """
        self.history = self.history[floor(len(self.history)/2):]
        logger.info("History tronked.")

    def updateSystemPrompt(self, sysprompt: str) -> str:
        """ Update the system prompt with the current memory """
        #restructuration of memory in a string
        return f"{sysprompt} Informations saved in your long term memory are : [{str(self.memory)}]"
    