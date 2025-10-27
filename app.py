import os
import openai
from dotenv import load_dotenv
from flask import Flask
from routes import api_routes

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Cria a instância da aplicação Flask
app = Flask(__name__)

# Registra as rotas (endpoints) definidos em outro arquivo
app.register_blueprint(api_routes)

# Configura a chave da API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Inicia o servidor local (localhost:5000 por padrão)
if __name__ == "__main__":
    app.run(debug=True)
