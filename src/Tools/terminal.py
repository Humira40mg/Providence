import subprocess
from .tool import Tool
from os import kill

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
    parameterDescription: str = "The command to run. Add '&' if you want to open an executable."
    hidden = "Eyes"

    def activate(self, aichoice: str) -> str:
        global actual_pid

        if not actual_pid or not is_running(actual_pid) :
            proc = subprocess.Popen(["alacritty", "-e", "tmux", "attach", "-t", "iasession"])
            actual_pid = proc.pid

        subprocess.run(["tmux", "send-keys", "-t", "iasession", aichoice, "C-m"])
        return ""
