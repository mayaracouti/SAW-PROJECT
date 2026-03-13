# Variáveis
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

all: install

# Cria o venv e instala as dependências
install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "✅ Ambiente configurado!"
	@echo "Para ativar manualmente, use: source $(VENV)/bin/activate"

# Comando para rodar o projeto já usando o Python do ambiente virtual
run:
	$(BIN)/python src/main.py

# Comando caso você queira apenas ativar e ficar no terminal (informativo)
activate:
	@echo "Copie e cole no seu terminal: source $(VENV)/bin/activate"

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Limpeza concluída!"