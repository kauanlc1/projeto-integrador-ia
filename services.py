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
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response_schema",
                    "schema": schema
                }
            }
        )

        print(response)

        raw_content = response.choices[0].message.content.replace("'", "\"")
        parsed_json = json.loads(raw_content)
        cleaned_json = clean_empty_keys(parsed_json)

        return cleaned_json
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
def extract_roadmap(notice_text, auxiliar_prompt, selected_job_role):
    cleaned_notice = preprocess_notice(notice_text, selected_job_role)

    prompt = f"""
    O MAIS IMPORTANTE E ANTES DE TUDO, ME DÊ RESPOSTA RÁPIDA E ASSERTIVA, RÁPIDA MESMO.
    
    Abaixo estão as informações extraídas do edital para a vaga de {selected_job_role}:

    {cleaned_notice}
    
    O roadmap deve sempre:
    
    - Ser dividido em MÓDULOS temáticos
    - As lições devem ser objetivas, claras e progressivas
    - A ordem importa (começo → intermediário → avançado)
    - Deve cobrir TODO o conteúdo técnico listado nas informações extraídas.
    - Se houver POUCO conteúdo técnico nas informações extraídas ou NÃO HOUVER, crie informações baseadas em conteúdos técnicos reais vinculados a vaga.
    - Não incluir nada que não apareça nas informações extraídas
    """

    instruction = f"""
    Você deve gerar um roadmap detalhado para a vaga de {selected_job_role} e retornar um JSON com a estrutura que segue abaixo:
    
    1. **Títulos dos módulos e lições** devem ser claros e refletir o conteúdo do edital.
    2. **Descrições** devem ser completas e específicas, com pelo menos duas frases explicativas.
    3. **Estrutura** deve ser bem organizada, com **módulos e lições** progressivas e sem repetições.
    4. Não deixe nenhum campo vazio (sem valores), nem chaves adicionais.
    5. Retornar APENAS 3 MÓDULOS, IMPLEMENTAR OS MAIS CONEXOS À VAGA EM QUESTÃO.
    
    1. Não use aspas extras, quebras de linha desnecessárias, ou caracteres especiais como '\\'.
    2. Mantenha as chaves do JSON corretamente formatadas, sem erros ou espaços adicionais.
    3. Não use as palavras 'Descrição' com caracteres extras ou inválidos.
    4. CRUCIAL que não retorne módulos ou lições vazias. 
    5. Se alguma lição ou módulo não for encontrado ou estiver incompleto, ignore ou retorne um aviso claro.
    6. A chave 'Lessons' de cada módulo deve ter entre 3 a 7 lições, se houver mais, ajuste a estrutura de acordo.
    7. A chave 'Order' de cada módulo e lição deve ser numérica e crescente.
    
    Aqui está o edital para análise:
    {notice_text}
    """

    # Adicionando o formato final esperado com JSON bem estruturado
    instruction += """
    Formato esperado:
    
    {
      "Title": "Roadmap de Estudos para [Vaga]",
      "Description": "Descrição geral do roadmap...",
      "Modules": [
        {
          "Title": "Nome do módulo",
          "Description": "Descrição detalhada do módulo...",
          "Order": 1,
          "Lessons": [
            {
              "Title": "Nome da lição",
              "Description": "Descrição da lição...",
              "Order": 1
            }
          ]
        }
      ]
    }
    """

    # Gerar a resposta da API
    gpt_response = generate_completion(prompt, instruction, 'roadmap_data_schema')

    # Verificar se a resposta é um dicionário válido
    if isinstance(gpt_response, dict):
        return {"RoadmapDataView": gpt_response}
    else:
        return {"error": "A resposta da API não está no formato esperado."}


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


def preprocess_notice(notice_text, selected_job_role):
    """
    Função para limpar e extrair o conteúdo relevante do edital com base na vaga.
    """
    # Usar expressões regulares para procurar e extrair conteúdo técnico relacionado à vaga
    # Exemplo de padrões comuns em editais, ajustáveis conforme a estrutura do edital
    relevant_sections = []

    # Buscando tópicos relacionados à vaga selecionada
    patterns = [
        rf"(?<=\bCONTEÚDOS PROGRAMÁTICOS\b)(.*?)(?=\b(PROGRAMA DA PROVA|CONHECIMENTOS BÁSICOS|CONHECIMENTOS ESPECÍFICOS)\b)",  # Extrair a parte técnica do edital
        rf"(?<=\b{re.escape(selected_job_role)}\b)(.*?)(?=\n|$)",  # Buscar detalhes específicos relacionados à vaga
        r"\n\s*\n",  # Remover quebras de linha excessivas
        r"\t",  # Remover tabulações
    ]

    for pattern in patterns:
        matches = re.findall(pattern, notice_text, re.DOTALL)
        relevant_sections.extend(matches)

    # Limpeza do texto removendo espaços extras ou outras formatações desnecessárias
    cleaned_notice = ' '.join(relevant_sections).strip()

    return cleaned_notice


def clean_empty_keys(response_data):
    if isinstance(response_data, dict):
        return {key: clean_empty_keys(value) for key, value in response_data.items() if value not in [None, "", {}, []]}
    elif isinstance(response_data, list):
        return [clean_empty_keys(item) for item in response_data if item not in [None, "", {}, []]]
    else:
        return response_data


def generate_roadmap_based_on_content(selected_job_role, extracted_content):
    prompt = f"""
    Com base nos seguintes tópicos técnicos extraídos do edital para a vaga de {selected_job_role}:

    {extracted_content}

    Gere um roadmap de estudos completo, com módulos temáticos, lições detalhadas e com foco nos tópicos extraídos.
    O roadmap deve ser progressivo e cobrir completamente os tópicos mencionados.
    """

    instruction = """
    Retorne um JSON estruturado com os seguintes campos obrigatórios:

    - Title (Título do roadmap)
    - Description (Descrição geral do roadmap)
    - Modules (Lista de módulos, no mínimo 3 e no máximo 7)
    - Lessons (Cada módulo deve ter entre 3 e 7 lições)

    Lembre-se de incluir as lições com base nos tópicos extraídos, sem inventar conteúdo.
    """

    return extract_roadmap(extracted_content, prompt, instruction)


def generate_questions_based_on_role(selected_job_role):
    prompt = f"""
    Gere um conjunto de 10 questões de múltipla escolha sobre a vaga de {selected_job_role}, abordando tópicos
    técnicos frequentemente exigidos em concursos para essa função. As questões devem cobrir as áreas mais comuns e essenciais,
    como fundamentos de TI, segurança, redes, desenvolvimento, e bancos de dados.

    Para cada questão, forneça 4 alternativas e uma resposta correta.
    """

    instruction = """
    Retorne um JSON com a seguinte estrutura para cada questão gerada:

    - Question: A questão
    - OptionA, OptionB, OptionC, OptionD: As alternativas
    - CorrectOption: A alternativa correta (ex: "A")
    - Order: A ordem da questão (1, 2, 3, ...)
    """

    return generate_questions(selected_job_role, 10)


def extract_job_related_content(notice_text, selected_job_role):
    prompt = f"""
    Leia o edital abaixo e extraia SOMENTE as partes relacionadas aos conteúdos técnicos necessários
    para a vaga de "{selected_job_role}". Se houver uma seção de "Conteúdos Programáticos", extraia essa parte.
    Caso contrário, gere um resumo com os tópicos técnicos mais comuns para essa vaga.

    Edital:
    {notice_text}
    """

    instruction = """
    Retorne somente os tópicos técnicos relacionados à vaga, no seguinte formato:

    - Tópico 1
    - Tópico 2
    - Tópico 3

    Se não encontrar nada explícito, gere uma lista de tópicos comuns para a vaga de "{selected_job_role}",
    baseado nas características gerais dos concursos dessa área.
    """

    gpt_response = generate_completion(prompt, instruction, 'exam_data_schema')

    # Extração do conteúdo relevante
    if gpt_response:
        return gpt_response
    else:
        return "Conteúdo técnico não encontrado no edital."


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
