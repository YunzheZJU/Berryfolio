@echo off
cd ..
pip install --editable .
set FLASK_APP=berryfolio
start flask run --host=0.0.0.0 --port=8080