#!/bin/bash
source venv/bin/activate
MODE=${1:-lightweight}
python3 run.py "$MODE"
