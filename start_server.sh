#!/bin/bash
pkill -f "python app.py"
nohup python app.py > flask.log 2>&1 &
ngrok http 5000

