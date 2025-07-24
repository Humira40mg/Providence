# Providence – Local AI Contextual Assistant (Linux Only)

**Providence** is a privacy-respecting AI assistant that runs entirely **locally** on your Linux machine.
It observes your screen in real time and sends intelligent contextual notifications based on what you’re doing.

> No cloud. No tracking. Just local intelligence.

---

## Features

* Real-time screen monitoring
* Context-aware smart reactions using local LLMs
* OCR via Tesseract for screen text analysis
* Native Linux notifications via `notify-send`
* Flask API server with control endpoints

---

## Platform Support

Currently supported on **Linux only** due to reliance on `notify-send`, and `wmctrl`.

---

## Installation

First, clone the repository and run the install script:

```bash
git clone https://github.com/yourname/providence.git
cd providence
./install.sh
```
Make sure to also install the Linux System Dependencies (see at the end of this readme).

This will install the necessary dependencies and tools.

---

## Running the Assistant

Use the provided script to launch the Flask server and the assistant:

```bash
./run.sh
```

---

## Available Endpoints (Flask Server)

| Endpoint          | Description                     |
| ----------------- | ------------------------------- |
| `POST /eyelaunch` | Start screen monitoring         |
| `POST /eyestop`   | Stop screen monitoring          |
| `POST /shutdown`  | Gracefully shut down the server |

---

## Model Support

Providence supports both **vision** and **text** models locally through [Ollama](https://ollama.com/).
You can use any model available in your Ollama setup, such as:

* `gemma:3b` (default)
* `mistral:7b`
* `llava` (vision + text)

> **Tokenizer Notice**
> If you use a custom model, make sure to place the corresponding tokenizer file in `./resources/` with the following format:
> `MODELNAME-tokenizer.json`
> *(e.g., `gemma3-tokenizer.json`, `mistral-tokenizer.json`)*
> And change the context window size in config to what your model can support.

---

## Tech Stack

* **Python 3.13+**
* **Flask** – lightweight API layer
* **Ollama** – LLM and VLM backends
* **PyTesseract** – OCR from screenshots
* **Pillow** – image processing
* **pyautogui** – screen capture and input hooks
* **notify-send** – native Linux notifications

---

## Linux System Dependencies

Install system packages manually or through the `install.sh` script.

### Debian/Ubuntu

```bash
sudo apt install tesseract-ocr libnotify-bin wmctrl
```

### Arch Linux

```bash
sudo pacman -S tesseract libnotify wmctrl
```

---

## Example Use Case

You're working on a coding project and Providence detects you're stuck on an error message.
It captures the screen, extracts the relevant code using OCR, and suggests a potential fix — all locally.

---

## Privacy First

Providence **never** sends data to the cloud.
All OCR, AI reasoning, and decision logic happen on your machine.

---

## Roadmap Ideas

* Audio context capture (e.g., hotword triggers or keyboard profiling)
* a POST request to open a chat window to interact with providence.

---

## Contributing

Feel free to open issues or PRs for bugs, feature suggestions, or model support.

---

## License

MIT — Use freely, fork with respect.