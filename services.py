import openai
import fitz


# === Função genérica para conversar com GPT ===
def call_gpt(prompt, max_tokens=1000):
    response = openai.Completion.create(
        model="gpt-5.0",
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].text.strip()


# === 1️⃣ Extrair dados do edital ===
def extract_notice_data(notice_text):
    prompt = f"""
    Leia o edital abaixo e extraia:
    - Título do edital
    - Breve descrição
    - Lista de vagas (nome e breve descrição)
    
    Retorne em JSON no formato:
    {{
        "Notice": "...",
        "NoticeTitle": "...",
        "NoticeDescription": "...",
        "JobRoles": [{{"Name": "...", "Description": "..."}}]
    }}

    Edital:
    {notice_text}
    """

    gpt_response = call_gpt(prompt)
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
    gpt_response = call_gpt(gpt_prompt)
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
    gpt_response = call_gpt(prompt, max_tokens=1500)
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

    gpt_response = call_gpt(prompt, max_tokens=1200)
    return {"Questions": gpt_response}


# === Utilitário para ler PDFs ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text
