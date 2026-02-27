import Tools
from subprocess import run
from os import path

icon = path.abspath("resources/providence.png")

def notify(msg):
    run([
            "notify-send",
            "-i", icon,
            "Providence",
            msg
        ])

def parseEyeResponse(response: dict):
    """exemple: 'tool_calls': [{'function': {'name': 'AddToMemory', 'arguments': {'aichoice': '03 en août et 18:12'}}}]"""
    if not response.get('tool_calls') : return []

    recursiveprompt = []
    
    for d in response['tool_calls']:
        tool = getattr(Tools, d['function']['name'])
        args = d['function'].get('arguments')
        arg = None
        if args :
            arg = args.get('aichoice')
        result = tool().activate(arg)
        if result: recursiveprompt.append(result)
    
    return recursiveprompt
