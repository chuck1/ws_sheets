
virtualenv venv

source venv/bin/activate

pip3 install -U .

python3 -m unittest ws_sheets.tests -v



