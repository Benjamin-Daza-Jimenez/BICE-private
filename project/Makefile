PYTHON = venv/bin/python
PIP = venv/bin/pip
STREAMLIT = venv/bin/streamlit

.PHONY: venv install freeze run run-desktop test

venv:
	test -d venv || python3 -m venv venv
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt
	$(PIP) install pywebview pyinstaller

freeze:
	$(PIP) freeze > requirements.txt

run:
	$(STREAMLIT) run app.py

run-desktop:
	$(PYTHON) desktop.py

test:
	$(PYTHON) -m unittest discover tests