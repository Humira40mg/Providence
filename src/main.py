from flask import Flask, request, Response, render_template
from flask_cors import CORS
from llmaccess import OllamaAccess, config, texthistory
from time import sleep
from os import makedirs, walk, remove, path, getpid
from infogetter import getWindowsTitles
from logger import logger
from parser import run
from yapper import yap, is_yapping, toggle_yapping
from pygame import mixer
from Tools import ScreenAnalyse
import threading
from voice_assist import wakeOnWord
import requests


logger.info("Initialisation of Providence's Server")
providence = OllamaAccess.getInstance()
makedirs("temp", exist_ok=True)


#flush the temp directory
for root, dirs, files in walk("./temp"):
    for file in files:
        remove(path.join(root, file))

BASE_DIR = path.abspath(path.join(path.dirname(__file__), ".."))
api = Flask(__name__, template_folder=path.join(BASE_DIR, "web-ui"), static_folder=path.join(BASE_DIR, "web-ui/static"))
CORS(api)

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
    providence.chat(f"{config['username']} est là. Présente lui tes salutations en fonction du contexte temporel donné en system prompt. Utilise la fonction d'intervention !", notextlog=True)

    if cooldown(120, stop_event):
        return

    while not stop_event.is_set() :

        output = ScreenAnalyse().activate()
        prompt = f"Voici des informations récoltées sur mon ordinateur, décide toi même si tu dois intervenir pour m'aider ou faire une remarque mais SI ET SEULEMENT SI tu juge ton intervention pertinante. Sinon n'utilise surtout pas le tool 'Intervention'. Ne répond pas de façon systématique et ne te répète jamais.\nOpened Applications: {getWindowsTitles()} {output['content']}"
        providence.chat(prompt, hiddenTools="Eyes", think = config["thinking"], images = output["images"], notextlog=True)

        if cooldown(120, stop_event):
            return


stop_event = threading.Event()
capture_thread = None
vocal_thread = None


def run_flask():
    api.run(port=config["apiport"], debug=True, use_reloader=False)


@api.route("/launch", methods=['POST'])
def launchEvent():
    """initialize the providence spying capabilities"""
    global capture_thread, vocal_thread

    if capture_thread and capture_thread.is_alive():
        return "Providence's eyes are already open.\n"
    stop_event.clear()

    capture_thread = threading.Thread(target=eye_in_the_sky, args=(stop_event,))
    capture_thread.daemon = True

    vocal_thread = threading.Thread(target=wakeOnWord, args=(stop_event, mixer.music))
    vocal_thread.daemon = True

    capture_thread.start()
    logger.info("Providence's eyes open.")

    vocal_thread.start()
    logger.info("Providence's ears open.")

    return "Providence's eyes and ears opened\n"


@api.route("/stop", methods=['POST'])
def stopEvent():
    """safly end providence's eyes and ears thread."""
    if stop_event.is_set():
        return "Providence's eyes are already closed.\n"
    stop_event.set()

    vocal_thread.join()
    logger.info("Providence's ears closed")

    capture_thread.join()
    logger.info("Providence's eyes closed")

    requests.post("http://localhost:11434/api/chat", json={
        "model": config["model"],
        "messages": [],
        "keep_alive": 0
        })
    return "Providence's eyes and ears closed\n"


@api.route("/toggleyapping", methods=['POST'])
def toggleYappingEvent():
    """Toggle speaking capabilities"""
    toggle_yapping()

    if mixer.music.get_busy() :
        mixer.music.stop()
    
    return "Providence's eyes closed\n"


@api.route('/shutdown', methods=['POST'])
def shutdown():
    """Close the pyhton process"""
    try:
        if not stop_event.is_set():
            stop_event.set()
            
            if mixer.music.get_busy() :
                mixer.music.stop()

            capture_thread.join()
            vocal_thread.join()
            logger.info("Providence's eyes closed\n")
        
        requests.post("http://localhost:11434/api/chat", json={
            "model": config["model"],
            "messages": [],
            "keep_alive": 0
            })
    except Exception :
        pass

    finally:
        run(["kill", "-9", str(getpid())])
        return 'Server shutting down...\n'


@api.route("/")
def index():
    return render_template("index.html", messages=texthistory, yapping=is_yapping())


@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    generate = providence.textchat(user_message, selfprompt= True)

    return Response(generate(), mimetype="text/plain")


if __name__ == "__main__":
    run_flask()