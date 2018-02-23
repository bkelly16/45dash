#!/bin/bash

ps -ef | grep app.py | grep -v grep | awk '{print $2}' | xargs kill

python /opt/45dash/app.py
