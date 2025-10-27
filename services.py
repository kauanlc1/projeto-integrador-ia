import openai
import fitz


def call_gpt(prompt):
    response = openai.Completion.create(
        model="gpt-5.0",  # Model da API (use o nome correto do modelo GPT-5)
        prompt=prompt,
        max_tokens=100,  # Limite de tokens
        temperature=0.7  # Nível de criatividade na resposta
    )
    return response.choices[0].text.strip()


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)  # Abrir o arquivo PDF
    text = ""
    for page_num in range(doc.page_count):  # Iterar por todas as páginas do PDF
        page = doc.load_page(page_num)  # Carregar a página
        text += page.get_text("text")  # Extrair texto da página
    return text


def upload_file(pdf_path):
    with open(pdf_path, 'rb') as file:
        response = openai.File.create(
            file=file,
            purpose="answers"  # Ou use "fine-tune" para treinamentos personalizados
        )
    return response['id']  # Retorna o ID do arquivo carregado


def process_notice(notice_text):
    # Aqui, chamamos o GPT-5 para processar o texto do edital e extrair as informações
    prompt = f"Extrair o título, descrição e lista de vagas do seguinte edital: {notice_text}"
    gpt_response = call_gpt(prompt)

    # Suponha que a resposta do GPT-5 seja o formato desejado
    result = {
        "Notice": notice_text,
        "NoticeTitle": gpt_response.get('title', 'Título não encontrado'),
        "NoticeDescription": gpt_response.get('description', 'Descrição não encontrada'),
        "JobRoles": gpt_response.get('job_roles', [])
    }
    return result


def search_notice(prompt):
    # Simular a busca por um edital
    result = {
        "Notice": "Edital encontrado com base no prompt",
        "NoticeTitle": "Título do Edital",
        "NoticeDescription": "Descrição breve do edital",
        "JobRoles": [
            {"Name": "Vaga encontrada", "Description": "Descrição da vaga encontrada"}
        ]
    }
    return result


def extract_roadmap(selected_job_role, notice_text):
    # Extrair o roadmap para a vaga selecionada
    result = {
        "Title": f"Roadmap para {selected_job_role}",
        "Description": "Descrição do roadmap",
        "Modules": [
            {"Title": "Módulo 1", "Description": "Descrição do módulo 1", "Order": 1, "Lessons": []},
            {"Title": "Módulo 2", "Description": "Descrição do módulo 2", "Order": 2, "Lessons": []}
        ]
    }
    return result


def generate_questions(subject, quantity):
    # Gerar questões com base no tipo de avaliação
    questions = []
    for i in range(quantity):
        questions.append({
            "Question": f"Questão {i + 1}",
            "OptionA": "Opção A",
            "OptionB": "Opção B",
            "OptionC": "Opção C",
            "OptionD": "Opção D",
            "CorrectOption": "A",
            "Order": i + 1,
            "Origin": "Assessment"
        })
    return questions
