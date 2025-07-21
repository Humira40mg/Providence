from PIL import Image
from pytesseract import image_to_string
from llmaccess import OllamaAccess, threading
from time import sleep
import pyautogui 
from datetime import datetime
import os
from infogetter import getWindowsTitles
from logger import logger
from parser import parseResponse

logger.info("Initialisation of Providence")
providence = OllamaAccess.getInstance()
output_dir = "temp"
os.makedirs(output_dir, exist_ok=True)

def eye_in_the_sky(stop_event):
    sleep(90)
    while not stop_event.is_set() :

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(output_dir, f"screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        img = Image.open(filename)
        textlu = image_to_string(img)
        os.remove(filename)
        
        prompt = f"Applications ouvertes : {getWindowsTitles()} | Phrases et mots lus à l'écran : ```{textlu}```"

        response = providence.generate(prompt)
        parseResponse(response)
        
        logger.info(f"USER : {prompt}\n\nAI : {response}")

        sleep(90)

stop_event = threading.Event()
capture_thread = threading.Thread(target=eye_in_the_sky, args=(stop_event,))
capture_thread.start()