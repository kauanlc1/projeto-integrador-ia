from flask import Blueprint, request, jsonify
from services import call_gpt

api_routes = Blueprint('api', __name__)


@api_routes.route('/gpt5', methods=['POST'])
def gpt_endpoint():
    content = request.get_json()
    prompt = content.get('prompt')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    # Chama a função que faz a requisição para a OpenAI
    result = call_gpt(prompt)
    return jsonify({"response": result})
