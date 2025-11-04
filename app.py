import os
import openai
from dotenv import load_dotenv
from flask import Flask
from routes import api_routes

load_dotenv()

app = Flask(__name__)

app.register_blueprint(api_routes)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Inicia o servidor local (localhost:5000 por padrão)
if __name__ == "__main__":
    app.run(debug=True)
