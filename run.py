import os
from dotenv import load_dotenv
from app.app import create_app

load_dotenv()

config=os.getenv('FLASK_ENV') or 'development'

app = create_app(config)

if __name__ == "__main__":
     # Configuração para ambientes de desenvolvimento e produção
    host = "0.0.0.0"  # Garante que o servidor escute conexões de qualquer IP
    port = 5000       # Porta padrão para o backend
    debug = config == 'development'

    app.run(host=host, port=port, debug=debug)
