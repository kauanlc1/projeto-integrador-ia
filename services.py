import os
import fitz
from openai import OpenAI
from dotenv import load_dotenv

from models import schemas_dict

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def generate_completion(prompt, instructions, schema_key):
    client = OpenAI(api_key=api_key)
    schema = schemas_dict[schema_key]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            top_p=0.9,
            frequency_penalty=1,
            presence_penalty=1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response_schema",
                    "schema": schema
                }
            }
        )
        return response.to_dict()
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return None


# === 1️⃣ Extrair dados do edital ===
def extract_notice_data(notice_text):
    prompt = f"""
    Leia o edital abaixo e extraia as informações:
    - Título do edital
    - Breve descrição
    - Lista de vagas (nome e breve descrição)
    """

    instruction = f"""
    Retorne no formato JSON conforme este modelo estruturado:
    {{
        "Notice": "EDITAL",
        "NoticeTitle": "...",
        "NoticeDescription": "...",
        "JobRoles": [
            {{
                "Name": "...",
                "Description": "..."
            }}
        ]
    }}
    
    Edital:
    {notice_text}
    """

    gpt_response = generate_completion(prompt, instruction, 'exam_data_schema')
    return {"ExamDataView": gpt_response}


# === 2️⃣ Procurar edital ===
def search_notice(prompt):
    gpt_prompt = f"""
    Nome do concurso: {prompt}  
    
    Você recebeu o nome de um concurso, e o objetivo é buscar os editais mais semelhantes relacionados a ele. Realize uma busca na web para encontrar os 10 editais mais próximos do título: "{prompt}".
    
    Os editais devem ser ordenados por similaridade de título e trazer as informações mais relevantes, como:

    - O título completo do edital + ' - '+ Ano do edital
    - Uma breve descrição do edital
    - As vagas oferecidas no edital (nome da vaga e descrição breve)

    Apenas traga os 10 primeiros editais mais similares, ordenados da maior para a menor similaridade.

    Caso não encontre resultados suficientes, retorne a mensagem "Nenhum edital encontrado".
    """

    instruction = f"""
    Retorne os resultados de editais encontrados na web, no seguinte formato JSON:
    {{
        "Notices": [
            {{
                "Notice": "Texto completo do edital",
                "NoticeTitle": "Título do edital",
                "NoticeDescription": "Descrição breve do edital",
                "JobRoles": [
                    {{
                        "Name": "Nome da vaga",
                        "Description": "Breve descrição da vaga"
                    }}
                ]
            }},
            ...
        ]
    }}
    Se não houver resultados, retorne "Nenhum edital encontrado".
    """

    gpt_response = generate_completion(gpt_prompt, instruction, 'search_notice_schema')
    return {"ExamDataView": gpt_response}


# === 3️⃣ Extrair roadmap de estudos ===
def extract_roadmap(selected_job_role, notice_text):
    prompt = f"""
    Gere um roadmap completo de estudos para a vaga "{selected_job_role}" com base nos conteúdos vinculados a vaga, descritos no edital abaixo:
    {notice_text}
    """

    instruction = f"""
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

    gpt_response = generate_completion(prompt, instruction, 'roadmap_data_schema')
    return {"RoadmapDataView": gpt_response}


# === 4️⃣ Gerar questões ===
def generate_questions(subject, quantity):
    title = subject.get("Title")
    description = subject.get("Description")
    assessment_type = subject.get("AssessmentType")

    prompt = f"""
    Gere {quantity} questões de múltipla escolha com 4 alternativas (A, B, C, D)
    sobre o tema "{title}" ({assessment_type}).
    """

    instruction = f"""
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

    gpt_response = generate_completion(prompt, instruction, 'questions_schema')
    return {"Questions": gpt_response}


def generate_test_response(prompt):
    gpt_response = generate_completion(prompt, '', '')

    if gpt_response:
        return gpt_response
    else:
        return "Erro ao gerar resposta. Verifique a saída do modelo."


# === Utilitário para ler PDFs ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text
