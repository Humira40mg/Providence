#!/bin/bash

# path to the .venv
VENV_DIR=".venv"

# Activation of the virtual environement
source "$VENV_DIR/bin/activate"

# app launch
python3 src/main.py &

sleep 3s

curl -X POST http://localhost:5000/eyelaunch
