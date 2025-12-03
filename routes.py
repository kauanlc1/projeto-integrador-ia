import os
import tempfile

import openai
from flask import Blueprint, request, jsonify
from services import (
    extract_notice_data,
    search_notice,
    extract_roadmap,
    generate_questions,
    generate_test_response, extract_data_from_pdf, clean_pdf_text, extract_programmatic_contents,
    extract_job_related_content,
)

api_routes = Blueprint('api', __name__)


# 1️⃣ Extrair dados do edital
@api_routes.route('/extract_notice_data', methods=['POST'])
def extract_notice_data_route():
    content = request.get_json()
    notice = content.get('notice')
    notice = clean_pdf_text(notice)

    if not notice:
        return jsonify({"error": "Campo 'notice' é obrigatório."}), 400

    result = extract_notice_data(notice)
    result["ExamDataView"]["Notice"] = notice
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
    contents = extract_programmatic_contents(notice)

    if contents:
        roadmap_source = contents
        auxiliar_prompt = f"""
        Você deve gerar um ROADMAP COMPLETO, PROFUNDO e ESTRUTURADO DE ESTUDOS
        para a vaga "{selected_job_role}", utilizando EXCLUSIVAMENTE os conteúdos
        PROGRAMÁTICOS descritos na extração das informações técnicas da vaga descritos abaixo.
        
        {roadmap_source}
        """
    else:
        roadmap_source = "IGNORE O EDITAL — ele não possui conteúdos de prova."
        auxiliar_prompt = f"""
        Você deve gerar um ROADMAP COMPLETO, PROFUNDO e ESTRUTURADO DE ESTUDOS
        para a vaga "{selected_job_role}". Devido ao fato de o edital não possuir contaúdo programáticos dispostos para a vaga,
        gere o roadmap
        com base nas bancas mais comuns (Institutos Federais, concursos federais, nível superior TI).
        
        {roadmap_source}
        """

    if not selected_job_role or not notice:
        return jsonify({"error": "Campos 'selectedJobRole' e 'notice' são obrigatórios."}), 400

    result = extract_roadmap(notice, auxiliar_prompt, selected_job_role)
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


@api_routes.route('/generate_roadmap_or_questions', methods=['POST'])
def generate_roadmap_or_questions_route():
    content = request.get_json()
    selected_job_role = content.get('selectedJobRole')
    notice = content.get('notice')

    # Extrair conteúdo técnico do edital
    extracted_content = extract_job_related_content(notice, selected_job_role)

    # Verifique se conseguimos extrair conteúdo específico da vaga
    if "Conteúdo técnico não encontrado" in extracted_content:
        # Caso não tenha informações específicas, gerar perguntas
        return generate_questions_based_on_role(selected_job_role)
    else:
        # Caso contrário, geramos o roadmap com base no conteúdo extraído
        return generate_roadmap_based_on_content(selected_job_role, extracted_content)


@api_routes.route('/upload_notice_pdf', methods=['POST'])
def upload_notice_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado. Use o campo 'file'"}), 400

    pdf_file = request.files['file']

    if pdf_file.filename == "":
        return jsonify({"error": "Nome de arquivo inválido."}), 400

    # Diretório temporário compatível com Windows, Linux e Heroku
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, pdf_file.filename)

    pdf_file.save(temp_path)

    try:
        raw_text = extract_data_from_pdf(temp_path)
        text = clean_pdf_text(raw_text)
        return jsonify({
            "message": "PDF processado com sucesso",
            "text": text
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
