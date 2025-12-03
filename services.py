import os
import re

import fitz
import json
import traceback
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

        print(response)

        # Extrair somente o JSON retornado
        raw_content = response.choices[0].message.content

        # Transformar string JSON → dict
        parsed_json = json.loads(raw_content)

        return parsed_json
    except Exception as e:
        import traceback
        print("Erro ao chamar a API:")
        print(traceback.format_exc())
        return {"error": str(e)}


# === 1️⃣ Extrair dados do edital ===
def extract_notice_data(notice_text):
    prompt = f"""
    Leia o edital abaixo e extraia as informações:
    - Título do edital
    - Breve descrição
    - Lista de vagas (nome e breve descrição)
    
    Atenção:
    - Não leve em consideração os vazamentos de linha identificados por '/n'
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


# === 2️⃣ Procurar edital (Está com problema) ===
def search_notice(prompt):
    gpt_prompt = f"""
    Nome do concurso: {prompt}
    
    Você deve retornar APENAS O EDITAL MAIS RELEVANTE encontrado com base no nome do concurso fornecido.
    
    Busque informações reais pesquisando na WEB, completas e bem estruturadas sobre esse edital, incluindo:
    
    - Título completo
    - Ano do edital
    - Descrição breve do edital
    - Lista de vagas com (nome + breve descrição)
    
    Para garantir que você está trazendo um pdf real, solicitei no campo 'link' um link real do PDF pois vou verificar.
    
    IMPORTANTE:
    ❌ Não gere 10 editais
    ❌ Não preencha placeholders como "outros editais"
    ❌ Não invente dados irreais sem contexto
    ❌ Não deixe campos vazios
    
    ✔ Retorne apenas o MELHOR e mais representativo edital disponível.
    """

    instruction = f"""
    Retorne os resultados de editais encontrados na web, no seguinte formato JSON:
    {{
        "Notices": [
            {{
                "Notice": "Texto completo do edital",
                "NoticeTitle": "Título do edital",
                "NoticeDescription": "Descrição breve do edital",
                "Link": "Link na web do edital",
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
def extract_roadmap(selected_job_role, notice_text, auxiliar_prompt):
    prompt = f"""
    {auxiliar_prompt}.
    
    O roadmap deve sempre:
    
    - Ser dividido em MÓDULOS temáticos
    - No mínimo 7 MÓDULOS COMPLETOS
    - Cada módulo deve conter entre 4 e 7 LIÇÕES
    - As lições devem ser objetivas, claras e progressivas
    - A ordem importa (começo → intermediário → avançado)
    - Deve cobrir TODO o conteúdo técnico listado no edital, sem inventar
    - Não incluir nada que não apareça no edital
    
    Aqui está o edital para análise:
    
    {notice_text}
    """

    instruction = """
    Você deve retornar um JSON seguindo ESTRITAMENTE o schema fornecido.
    
    REGRAS IMPORTANTES:
    
    1. NÃO criar chaves vazias como "", " ", ".", ",", etc.
    2. Mantém apenas os campos permitidos pelo schema:
       - Title
       - Description
       - Modules
       - Lessons
       - Order
    
    3. Cada Módulo DEVE conter:
       - Title
       - Description
       - Order
       - Lessons (array)
    
    4. Cada Lesson DEVE conter:
       - Title
       - Description
       - Order
    
    5. Estrutura mínima obrigatória:
       - Entre 3 e 7 módulos
       - Cada módulo com 3 a 7 lições
       - Descrições devem ser detalhadas (mínimo 2 frases)
    
    6. Não inventar conteúdo fora do edital.
    
    7. O título dos módulos deve sempre refletir um tópico real do edital.
    
    Formato JSON de exemplo:
    
    {
      "Title": "Roadmap de Estudos para [Vaga]",
      "Description": "Descrição geral...",
      "Modules": [
        {
          "Title": "Nome do módulo",
          "Description": "Descrição detalhada...",
          "Order": 1,
          "Lessons": [
            {
              "Title": "Nome da lição",
              "Description": "Descrição detalhada...",
              "Order": 1
            }
          ]
        }
      ]
    }
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


def extract_programmatic_contents(text):
    patterns = [
        r"CONTEÚDOS PROGRAMÁTICOS(.*)",
        r"PROGRAMA DA PROVA(.*)",
        r"CONHECIMENTOS ESPECÍFICOS(.*)",
        r"CONHECIMENTOS BÁSICOS(.*)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()

    return None


def clean_pdf_text(text):
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    text = text.lstrip()
    text = text.replace("\t", " ").replace("\r", " ")

    return text.strip()


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text") + "\n"

    doc.close()
    return text


def generate_test_response(prompt):
    gpt_response = generate_completion(prompt, '', '')

    if gpt_response:
        return gpt_response
    else:
        return "Erro ao gerar resposta. Verifique a saída do modelo."


# === Utilitário para ler PDFs (Somente para testes locais, é responsabilidade do backend)===
def extract_data_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text
