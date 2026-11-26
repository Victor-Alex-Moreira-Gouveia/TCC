FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código (incluindo o main.py e o start.sh)
COPY . .

# CORREÇÃO: Remove os caracteres ocultos do Windows (\r) do script
RUN sed -i 's/\r$//' ./start.sh

# Dá permissão de execução para o script de inicialização
RUN chmod +x ./start.sh

# Execute com usuário sem privilégios administrativos no contêiner.
RUN groupadd --system --gid 10001 tccapp \
    && useradd --system --uid 10001 --gid tccapp --home-dir /app --no-create-home tccapp \
    && chown -R tccapp:tccapp /app

USER tccapp

EXPOSE 8080

# Executa o script que criamos
CMD ["./start.sh"]