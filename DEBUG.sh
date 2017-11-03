#!/bin/bash
pip install --editable .
export FLASK_APP=berryfolio
export FLASK_DEBUG=true
flask run --host=0.0.0.0 --port=8080
