#!/bin/bash
. venv/Scripts/activate
pip install --editable .
export FLASK_APP=berryfolio
flask run --host=0.0.0.0 --port=8080
