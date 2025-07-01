# Imagem base
FROM python:3.12

# Define o diretório de trabalho
WORKDIR /app



# Copiar e instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos para dentro do container
COPY . .

# Expondo a porta padrão do Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["fdr_db:5432", "python", "run.py"]
