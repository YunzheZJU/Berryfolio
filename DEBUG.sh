#!/bin/bash
export FLASK_APP=main.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=8080
