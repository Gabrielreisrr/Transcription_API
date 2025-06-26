# Use uma imagem Python slim para reduzir o tamanho
FROM python:3.10-slim

# Instale dependências do sistema necessárias para whisper e ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Crie o diretório de trabalho
WORKDIR /app

# Copie os arquivos de requirements e instale as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código da API para o container
COPY whisper_api.py .

# Exponha a porta padrão do FastAPI/Uvicorn
EXPOSE 8000

# Comando para rodar a API
CMD ["uvicorn", "whisper_api:app", "--host", "0.0.0.0", "--port", "8000"] 