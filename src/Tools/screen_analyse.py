from .tool import Tool
import pyautogui
from datetime import datetime
from os import path, remove
from PIL import Image
from pytesseract import image_to_string
from generationlock import generationLock
import base64
import requests
from config_read import VISION

desc = "Call this to get an OCR extraction of what the user is seeing."
if VISION :
    desc = "Call this to get a screenshot of what the user is seeing."

def analyse_factory():

    if VISION:
        
        def vision(filename):
            with open(path.abspath(filename), "rb") as f:
                img = [base64.b64encode(f.read()).decode("utf-8")]
            remove(filename)
            return {"role":"tool", "content":"", "images":img, "tool_name":"ScreenAnalyse"}
            
        return vision

    def ocr(filename):
        img = Image.open(filename)
        content = f"OCR Extraction of the screen : {image_to_string(img)}"
        remove(filename)
        return {"role":"tool", "content":content, "images": None, "tool_name":"ScreenAnalyse"}

    return ocr
        
analyse = analyse_factory()   


class ScreenAnalyse(Tool):

    name = "ScreenAnalyse"
    description = desc
    hidden = "Eyes"

    def activate(self, *args) -> dict:
       
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = path.join(f"temp/screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        return analyse(filename)
        

    def ollamaFormat(self):
        return {
            "type": "function", 
            "function": {
                "name":self.name,
                "description": self.description
                }
            }