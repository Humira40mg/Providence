from .tool import Tool
import pyautogui
from datetime import datetime
from os import path, remove
from PIL import Image
from pytesseract import image_to_string
from generationlock import generationLock
import base64
import requests

class ScreenAnalyse(Tool):

    name = "ScreenAnalyse"
    description = "Call this to get an OCR extraction of what the user is seeing."
    hidden = "Eyes"

    def activate(self, *args) -> dict:
       
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = path.join(f"temp/screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        #OCR
        img = Image.open(filename)
        ocr = f"OCR Extraction of the screen : {image_to_string(img)}"

        remove(filename)

        return {"role":"tool", "content":ocr, "tool_name":"ScreenAnalyse"}
        
        """
        with open(path.abspath(filename), "rb") as f:
            img = [base64.b64encode(f.read()).decode("utf-8")]

        remove(filename)

        with generationLock :
            payload = {
                "model": "gemma3:4b",
                "prompt": "Décris avec précision la capture d'écran donnée sans halluciner.",
                "images": img,
                "stream": False
            }

            response = requests.post(f"http://localhost:11434/api/generate", json=payload)
            if response.ok:
                text = response.json()["response"].strip()

                return f"Screen Description : [ {text} ]\nOCR Extraction : [ {ocr} ]"
            else:
                raise Exception(f"Error Ollama API: {response.text}")
        """

    def ollamaFormat(self):
        return {
            "type": "function", 
            "function": {
                "name":self.name,
                "description": self.description
                }
            }