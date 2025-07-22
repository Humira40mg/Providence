from PIL import Image
from flask import Flask, request
from pytesseract import image_to_string
from llmaccess import OllamaAccess, threading, config
from time import sleep
import pyautogui 
from datetime import datetime
import os
from infogetter import getWindowsTitles
from logger import logger
from parser import parseResponse, notify, run
import signal

logger.info("Initialisation of Providence's Server")
providence = OllamaAccess.getInstance()
os.makedirs("temp", exist_ok=True)
api = Flask(__name__)

def eye_in_the_sky(stop_event):

    hello = providence.generate(f"{config['username']} just arrived. Say hello !")
    if not "[INTERVENTION]" in hello:
        notify(hello)
    else:
        parseResponse(hello)
    logger.info(f"AI : {hello}")

    sleep(90)

    while not stop_event.is_set() :

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(f"temp/screenshot_{timestamp}.png")

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
capture_thread.daemon = True

def run_flask():
    api.run(port=config["apiport"])

@api.route("/eyelaunch", methods=['POST'])
def launchEvent():
    if capture_thread.is_alive():
        return "Providence's eyes are already open.\n"
    stop_event.clear()
    capture_thread.start()
    logger.info("Providence's eyes open.")
    return "Providence's eyes opened\n"

@api.route("/eyestop", methods=['POST'])
def stopEvent():
    if stop_event.is_set():
        return "Providence's eyes are already closed.\n"
    stop_event.set()
    capture_thread.join()
    logger.info("Providence's eyes closed\n")
    return "Providence's eyes closed\n"

@api.route('/shutdown', methods=['POST'])
def shutdown():
    stop_event.set()
    run(["kill", str(os.getpid())])
    return 'Server shutting down...\n'


if __name__ == "__main__":
    run_flask()