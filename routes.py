import openai
from flask import Blueprint, request, jsonify
from services import (
    extract_notice_data,
    search_notice,
    extract_roadmap,
    generate_questions,
    generate_test_response,
)

api_routes = Blueprint('api', __name__)


# 1️⃣ Extrair dados do edital
@api_routes.route('/extract_notice_data', methods=['POST'])
def extract_notice_data_route():
    content = request.get_json()
    notice = content.get('notice')

    if not notice:
        return jsonify({"error": "Campo 'notice' é obrigatório."}), 400

    result = extract_notice_data(notice)
    return jsonify(result), 200


# 2️⃣ Procurar edital
@api_routes.route('/search_notice', methods=['POST'])
def search_notice_route():
    content = request.get_json()
    prompt = content.get('prompt')

    if not prompt:
        return jsonify({"error": "Campo 'prompt' é obrigatório."}), 400

    result = search_notice(prompt)
    return jsonify(result), 200


# 3️⃣ Gerar roadmap (dados do edital + vaga)
@api_routes.route('/extract_roadmap', methods=['POST'])
def extract_roadmap_route():
    content = request.get_json()
    selected_job_role = content.get('selectedJobRole')
    notice = content.get('notice')

    if not selected_job_role or not notice:
        return jsonify({"error": "Campos 'selectedJobRole' e 'notice' são obrigatórios."}), 400

    result = extract_roadmap(selected_job_role, notice)
    return jsonify(result), 200


# 4️⃣ Gerar questões
@api_routes.route('/generate_questions', methods=['POST'])
def generate_questions_route():
    content = request.get_json()
    subject = content.get('subject')
    quantity = content.get('quantity', 5)

    if not subject:
        return jsonify({"error": "Campo 'subject' é obrigatório."}), 400

    result = generate_questions(subject, quantity)
    return jsonify(result), 200


# 5️⃣ Teste de rota
@api_routes.route('/test', methods=['POST'])
def test_route():
    content = request.get_json()
    print(f"Content payload: {content}")

    prompt = content.get('prompt')

    # Gerar o resultado com a função
    result = generate_test_response(prompt)

    # Diagnóstico: imprima o tipo do resultado
    print(f"Tipo do resultado: {type(result)}")

    print(f"Resultado: {result}")

    # Caso o resultado seja um dict, retorne como JSON
    if isinstance(result, dict):
        return jsonify(result), 200
    # Caso seja uma string, retorne como JSON
    elif isinstance(result, str):
        return jsonify({"result": result}), 200
    else:
        return jsonify({"error": "Tipo de resultado inválido"}), 400
