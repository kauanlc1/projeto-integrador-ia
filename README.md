# Projeto Integrador IA

> **Este projeto** visa integrar APIs de busca de editais e gerar planos de estudos personalizados para usuários. A aplicação é construída com **Flask** no backend e utiliza o **Heroku** para deploy contínuo. A automação do deploy é feita através de **GitHub Actions**.

## 🛠️ Tecnologias utilizadas

- **Flask**: Framework web para Python.
- **Heroku**: Plataforma para deploy do aplicativo.
- **GitHub Actions**: CI/CD (Integração contínua e deploy contínuo).
- **Python 3.12**: Linguagem de programação usada para a construção do backend.
- **openai**: Integração com a API do OpenAI para gerar planos de estudos e sugerir recursos.
- **python-dotenv**: Para gerenciar variáveis de ambiente.
- **PyMuPDF**: Para leitura de arquivos PDF.

## 🚀 Funcionalidades

1. **Busca de Editais**: O sistema é capaz de buscar editais de concursos e eventos por meio de APIs.
2. **Geração de Plano de Estudos**: Com base no edital e nas preferências do usuário, o sistema sugere um plano de estudos personalizado, usando a **API do OpenAI**.
3. **Integração de APIs**: Integração contínua com APIs de busca de editais e recursos educativos.
4. **Deploy Automático**: A cada novo **push** na branch `master`, o código é automaticamente enviado para o **Heroku** utilizando **GitHub Actions**.

## 📦 Como rodar localmente

1. **Clone o repositório**:

   ```bash
   git clone https://github.com/kauanlc1/projeto-integrador-ia.git
   cd projeto-integrador-ia

2.  **Crie um ambiente virtual** (se ainda não tiver um):
    
    `python -m venv venv` 
    
3.  **Ative o ambiente virtual**:
    
    -   **Windows**:
        
        `.\venv\Scripts\activate` 
        
    -   **Linux/macOS**:
        
        `source venv/bin/activate` 
        
4.  **Instale as dependências**:
    
    `pip install -r requirements.txt` 
    
5.  **Defina suas variáveis de ambiente**:
    
    Crie um arquivo `.env` na raiz do projeto e adicione suas **variáveis de ambiente** (exemplo):
    
    `OPENAI_API_KEY=your_openai_api_key
    HEROKU_API_KEY=your_heroku_api_key
    HEROKU_API_NAME=your_heroku_app_name
    HEROKU_API_EMAIL=your_heroku_email` 
    
6.  **Rodar a aplicação**:
    
    `python app.py` 
    
7.  **Acesse no seu navegador**:
    
    -   Abra `http://127.0.0.1:5000` para interagir com a aplicação localmente.
        

----------

## 📝 Como contribuir

1.  **Faça o fork** do repositório.
    
2.  Crie uma **branch** para suas mudanças:
    
    `git checkout -b minha-feature` 
    
3.  **Faça o commit** das suas alterações:
    
    `git commit -m "Minha feature"` 
    
4.  **Envie para o repositório remoto**:
    
    `git push origin minha-feature` 
    
5.  **Abra um pull request** para a branch `master`.
    

----------

## 🚀 Deploy no Heroku

O deploy é feito automaticamente sempre que houver um **push na branch `master`**. O **GitHub Actions** está configurado para **realizar o deploy no Heroku** automaticamente, com as seguintes etapas:

1.  **Instalar dependências** do `requirements.txt`.
    
2.  **Rodar testes automatizados** com `pytest` (caso configurado).
    
3.  **Fazer deploy para o Heroku** usando a **Heroku API Key** configurada como variável de ambiente.
    

### 🔑 Configuração do Heroku no GitHub

Para que o deploy funcione, você precisa configurar as **variáveis de ambiente** no **GitHub** com suas **chaves da API do Heroku**:

1.  **Heroku API Key**: Gere sua chave da API no painel do Heroku.
    
2.  **Heroku App Name**: O nome do seu app no Heroku.
    
3.  **Heroku Email**: O e-mail associado à sua conta do Heroku.
    

No **GitHub**:

1.  Vá em **Settings** → **Secrets**.
    
2.  Crie os **secrets** com os nomes `HEROKU_API_KEY`, `HEROKU_API_NAME` e `HEROKU_API_EMAIL`.
    

No **arquivo `deploy.yml`**, essas variáveis são usadas para o deploy automático no Heroku.

----------

## 📂 Estrutura do projeto

```
├── app.py                  # Arquivo principal da aplicação Flask
├── requirements.txt        # Dependências do projeto
├── .github/
│   └── workflows/
│       └── deploy.yml      # Arquivo de configuração do GitHub Actions
├── .env                    # Variáveis de ambiente
├── services.py             # Lógica de serviços (API do OpenAI, PDF, etc.)
├── routes.py               # Definição das rotas da aplicação
├── models/
│   └── history.py          # Modelo de dados do histórico de editais
└── README.md               # Este arquivo
```
