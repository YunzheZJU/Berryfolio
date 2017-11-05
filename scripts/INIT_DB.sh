#!/bin/bash
cd ..
pip install --editable .
export FLASK_APP=berryfolio
flask initdb
