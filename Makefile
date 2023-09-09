VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip

debug_run: $(VENV)/Scripts/activate
	$(PYTHON) src/main.py

run: $(VENV)/Scripts/activate
	$(PYTHON) -O src/main.py

$(VENV)/Scripts/activate: requirements.txt
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -rf src/__pycache__
	rm -rf $(VENV)
