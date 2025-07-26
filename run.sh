#!/bin/bash

# Activation of the conda virtual environement
source ~/miniconda3/etc/profile.d/conda.sh
conda activate providence

# app launch
python3 src/main.py &

sleep 15s

curl -X POST http://localhost:5000/eyelaunch
