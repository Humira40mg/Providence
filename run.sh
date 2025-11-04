#!/bin/bash

# Activation of the conda virtual environement
source ~/miniconda3/etc/profile.d/conda.sh
conda activate providence

# app launch
if [ "$(cat /sys/class/power_supply/ADP1/online)" = "1" ]; then
    python3 src/main.py &

    conda deactivate

    sleep 15s

    curl -X GET http://localhost:4242/launch
fi