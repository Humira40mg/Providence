import subprocess
from .tool import Tool
from os import kill
from time import sleep

subprocess.run(["tmux", "new-session", "-d", "-s", "iasession"])
subprocess.run(["tmux", "send-keys", "-t", "iasession", "cd ~", "C-m"])
actual_pid = None

def is_running(pid):
    try:
        kill(pid, 0)
        return True
    except OSError:
        return False

class Terminal(Tool):

    name = "Terminal"
    description = "Call this to run an Arch Linux command in an open terminal."
    parameterDescription: str = "The command to run. If you launch an application like spotify or firefox, use & to launch it in background."
    hidden = "Eyes"

    def activate(self, aichoice: str) -> dict:
        global actual_pid

        if not actual_pid or not is_running(actual_pid) :
            proc = subprocess.Popen(["alacritty", "-e", "tmux", "attach", "-t", "iasession"])
            actual_pid = proc.pid

        subprocess.run(["tmux", "send-keys", "-t", "iasession", aichoice, "C-m"])

        sleep(0.2)

        result = subprocess.run(
            ["tmux", "capture-pane", "-t", "iasession", "-p"],
            capture_output=True,
            text=True
        )
        return {"role":"tool", "content":str(result.stdout), "tool_name":"Terminal"}
