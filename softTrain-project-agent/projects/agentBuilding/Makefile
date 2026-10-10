PYTHON = /opt/venvs/pyDS/bin/python

.PHONY: help agentAPI ollama_backend anthropic_backend test

help:
	@echo "====help===="
	@echo "make ollama_backend"
	@echo "make anthropic_backend"
	@echo "make test"
	@echo "make agentAPI"	
	@echo "============"

agentAPI:
	$(PYTHON) -m agentAPI

chat_ollama:
	$(PYTHON) -m agentAPI -b "ollama"

chat_anthropic:
	$(PYTHON) -m agentAPI -b "anthropic"

test:
	$(PYTHON) -m pytest -v