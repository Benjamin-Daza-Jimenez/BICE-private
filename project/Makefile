PYTHON = venv/bin/python
PIP = venv/bin/pip
STREAMLIT = venv/bin/streamlit

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

freeze:
	$(PIP) freeze > requirements.txt

run:
	$(STREAMLIT) run app.py

test:
	$(PYTHON) -m unittest discover tests

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf func/__pycache__