import subprocess

def getWindowsTitles():
    result = subprocess.run(['wmctrl', '-l'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.strip().split('\n')
    windows = ""
    for line in lines:
        parts = line.split(None, 3)
        if len(parts) == 4:
            window_id, desktop_id, machine, title = parts
            windows += f"[{title}], "

    return windows