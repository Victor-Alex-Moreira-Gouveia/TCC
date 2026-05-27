FROM python:3.11-slim

WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código (incluindo o main.py e o start.sh)
COPY . .

# Dá permissão de execução para o script de inicialização
RUN chmod +x start.sh

EXPOSE 8080

# Executa o script que criamos
CMD ["./start.sh"]