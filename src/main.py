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
from yapper import yap
from pygame import mixer

logger.info("Initialisation of Providence's Server")
providence = OllamaAccess.getInstance()
os.makedirs("temp", exist_ok=True)
api = Flask(__name__)

yapping = True
mixer.init()

def cooldown(time, stop_event):
    """cooldown the right amount of time, but check if a stop condition is set every second"""
    for i in range(time):
        if stop_event.is_set():
            return True
        sleep(1)
    return False

def eye_in_the_sky(stop_event):
    """thread handler, fonction that is basicly a spyware but the informations are given to your local ia"""
    hello = providence.generate(f"{config['username']} just arrived. Say hello ! It's {datetime.now().strftime('%A we are the %d in %B and the clock is currently %H:%M')}, if you have a fact about this date you can share it with {config['username']}, don't make up a fact if there is nothing to tell.", systemPrompt=f"Speak only using : {config['language']}.")

    if yapping :
        audio = yap(hello)
        mixer.music.load(audio)
        notify(hello)
        mixer.music.play()
        while mixer.music.get_busy():
            continue
        os.remove(audio)
        os.remove("audio_outputs/tmp.wav")
    else:
        notify(hello)

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
        
        prompt = f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %A %B')}\nOpened Applications: {getWindowsTitles()} {textlu}"

        response = providence.generate(prompt, images=img)
        intervention = parseResponse(response)
        
        if intervention :
            if yapping :
                audio = yap(intervention)
                mixer.music.load(audio)
                notify(intervention)
                mixer.music.play()
                while mixer.music.get_busy():
                    continue
                os.remove(audio)
                os.remove("audio_outputs/tmp.wav")
            else:
                notify(intervention)
            
        os.remove(filename)

        logger.info(f"USER : {prompt}\n\nAI : {response}")

        if cooldown(90, stop_event):
            return

stop_event = threading.Event()
capture_thread = None

def run_flask():
    api.run(port=config["apiport"], debug=True, use_reloader=False)

@api.route("/eyelaunch", methods=['POST'])
def launchEvent():
    """initialize the providence spying capabilities"""
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
    """safly end providence's eyes thread."""
    if stop_event.is_set():
        return "Providence's eyes are already closed.\n"
    stop_event.set()
    capture_thread.join()
    logger.info("Providence's eyes closed\n")
    return "Providence's eyes closed\n"

@api.route("/toggleyapping", methods=['POST'])
def toggleYappingEvent():
    """Toggle speaking capabilities"""
    yapping = not yapping

    if mixer.music.get_busy() :
        mixer.music.stop()
    
    return "Providence's eyes closed\n"


@api.route('/shutdown', methods=['POST'])
def shutdown():
    """Close the pyhton process"""
    if not stop_event.is_set():
        stop_event.set()
        capture_thread.join()
        logger.info("Providence's eyes closed\n")

    run(["kill", "-9", str(os.getpid())])
    return 'Server shutting down...\n'


if __name__ == "__main__":
    run_flask()