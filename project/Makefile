PYTHON = venv/bin/python
PIP = venv/bin/pip
STREAMLIT = venv/bin/streamlit
PYINSTALLER = venv/bin/pyinstaller

install:
	$(PIP) install --upgrade pip
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