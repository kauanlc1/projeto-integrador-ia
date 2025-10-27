import os
import openai

from flask import Flask
from routes import api_routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Registrando as rotas
app.register_blueprint(api_routes)

# Configurar a chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    app.run(debug=True)
