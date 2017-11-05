@echo off
cd ..
pip install --editable .
set FLASK_APP=berryfolio
flask initdb