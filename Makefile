VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip

run: $(VENV)/Scripts/activate
	$(PYTHON) -O src/main.py

debug_run: $(VENV)/Scripts/activate
	$(PYTHON) src/main.py

lint: $(VENV)/Scripts/activate
	pylint src/

$(VENV)/Scripts/activate: requirements.txt
	python -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -rf src/__pycache__
	rm -rf $(VENV)