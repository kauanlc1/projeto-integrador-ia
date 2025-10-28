import os
import fitz
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def generate_completion(prompt):
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": """
                    Você é um assistente que irá responder com base no edital e gerar roadmaps e questões de estudo de forma clara e detalhada.
                    """
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.5,
            top_p=0.9,
            frequency_penalty=1,
            presence_penalty=1,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return None


# === 1️⃣ Extrair dados do edital ===
def extract_notice_data(notice_text):
    prompt = f"""
    Leia o edital abaixo e extraia:
    - Título do edital
    - Breve descrição
    - Lista de vagas (nome e breve descrição)
    
    Retorne em formato JSON conforme este modelo:
    {{
        "Notice": "{notice_text}",
        "NoticeTitle": "...",
        "NoticeDescription": "...",
        "JobRoles": [{{"Name": "...", "Description": "..."}}]
    }}

    Edital:
    {notice_text}
    """

    gpt_response = generate_completion(prompt)
    return {"ExamDataView": gpt_response}


# === 2️⃣ Procurar edital ===
def search_notice(prompt):
    gpt_prompt = f"""
    Encontre um edital relacionado ao tema:
    "{prompt}"

    Retorne no formato JSON:
    {{
        "Notice": "...",
        "NoticeTitle": "...",
        "NoticeDescription": "...",
        "JobRoles": [{{"Name": "...", "Description": "..."}}]
    }}
    """
    gpt_response = generate_completion(gpt_prompt)
    return {"ExamDataView": gpt_response}


# === 3️⃣ Extrair roadmap de estudos ===
def extract_roadmap(selected_job_role, notice_text):
    prompt = f"""
    Gere um roadmap completo de estudos para a vaga "{selected_job_role}" com base no edital abaixo:
    {notice_text}

    Retorne no formato JSON:
    {{
        "Title": "...",
        "Description": "...",
        "Modules": [
            {{
                "Title": "...",
                "Description": "...",
                "Order": 1,
                "Lessons": [
                    {{
                        "Title": "...",
                        "Description": "...",
                        "Order": 1
                    }}
                ]
            }}
        ]
    }}
    """
    gpt_response = generate_completion(prompt)
    return {"RoadmapDataView": gpt_response}


# === 4️⃣ Gerar questões ===
def generate_questions(subject, quantity):
    title = subject.get("Title")
    description = subject.get("Description")
    assessment_type = subject.get("AssessmentType")

    prompt = f"""
    Gere {quantity} questões de múltipla escolha com 4 alternativas (A, B, C, D)
    sobre o tema "{title}" ({assessment_type}).

    Retorne no formato JSON:
    [
        {{
            "Question": "...",
            "OptionA": "...",
            "OptionB": "...",
            "OptionC": "...",
            "OptionD": "...",
            "CorrectOption": "A",
            "Order": 1,
            "Origin": "{assessment_type}"
        }}
    ]

    Descrição do tema:
    {description}
    """

    gpt_response = generate_completion(prompt)
    return {"Questions": gpt_response}


def generate_test_response(prompt):
    return "Resposta gerada com base no prompt: " + prompt


# === Utilitário para ler PDFs ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text
