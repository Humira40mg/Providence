#!/bin/bash

# Activation of the conda virtual environement
source ~/miniconda3/etc/profile.d/conda.sh
conda activate providence

# app launch
python3 src/main.py &

conda deactivate


sleep 15s

if [ "$(cat /sys/class/power_supply/ADP1/online)" = "1" ]; then
    curl -X POST http://localhost:5000/launch
fi