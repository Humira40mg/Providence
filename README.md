# Providence – Local AI Contextual Assistant (Linux Only)

Providence is a privacy-respecting AI assistant that runs entirely **locally** on your Linux machine.  
It observes your environment (only screen at the moment), and sends smart notifications when it decides your context calls for advice, reminders, or reactions.

> No cloud, no tracking — 100% local intelligence.

---

## Platform Support

This project is currently compatible with **Linux only** because it uses `notify-send` for desktop notifications, and `wmctrl -l`.

---

## Features

-  Context detection (based on activity, screenshots)
-  Smart notifications via `notify-send`
-  OCR from screen images using Tesseract

---

## Tech Stack

- Python 3.13+
- Ollama + [Mistral 7B](https://ollama.com/library/mistral)
- Image processing: `Pillow`, `pytesseract`
- Input/screen activity: `pyautogui`
- Notifications: `notify-send` (Linux only at the moment)

---

## Prerequisites

Before running the assistant, install the following system dependencies:

### Linux System Packages

```bash
# Debian/Ubuntu
sudo apt install tesseract-ocr libnotify-bin scrot

# Arch Linux
sudo pacman -S tesseract libnotify scrot
