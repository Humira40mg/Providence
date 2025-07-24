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
import base64

logger.info("Initialisation of Providence's Server")
providence = OllamaAccess.getInstance()
os.makedirs("temp", exist_ok=True)
api = Flask(__name__)

def cooldown(time, stop_event):
    for i in range(time):
        if stop_event.is_set():
            return True
        sleep(1)
    return False

def eye_in_the_sky(stop_event):

    hello = providence.generate(f"{config['username']} just arrived. Say hello ! It's {datetime.now().strftime('%A we are in %B and the clock is currently %H:%M:%S')}")
    if not "[INTERVENTION]" in hello:
        notify(hello)
    else:
        parseResponse(hello)
    logger.info(f"AI : {hello}")

    if cooldown(90, stop_event):
        return

    while not stop_event.is_set() :

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(f"temp/screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        img = Image.open(filename)
        textlu = f"Information rode on the screen : {image_to_string(img)}" #important for non vision models

        if config['vision']:
            with open(os.path.abspath(filename), "rb") as f:
                img = [base64.b64encode(f.read()).decode("utf-8")]
        else :
            img = None
        
        prompt = f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %A %B')}\nOpened Applications: {getWindowsTitles()} {textlu} | Analyse the image given"

        response = providence.generate(prompt, images=img)
        parseResponse(response)

        os.remove(filename)

        logger.info(f"USER : {prompt}\n\nAI : {response}")

        if cooldown(90, stop_event):
            return

stop_event = threading.Event()
capture_thread = None

def run_flask():
    api.run(port=config["apiport"])

@api.route("/eyelaunch", methods=['POST'])
def launchEvent():
    global capture_thread

    if capture_thread and capture_thread.is_alive():
        return "Providence's eyes are already open.\n"
    stop_event.clear()

    capture_thread = threading.Thread(target=eye_in_the_sky, args=(stop_event,))
    capture_thread.daemon = True

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