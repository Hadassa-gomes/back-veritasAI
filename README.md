# VeritasAI Backend

API responsável pela análise e checagem de fatos da aplicação VeritasAI. Este projeto recebe textos, URLs e imagens, consulta fontes externas quando disponível e usa o Gemini para gerar um veredito estruturado sobre o conteúdo enviado.

Além da análise, o backend salva cada verificação em um banco SQLite local e expõe um histórico de consultas.

## O que a API faz

- Analisa afirmações de texto
- Extrai e analisa o conteúdo de URLs
- Faz análise multimodal de imagens
- Consulta o Google Fact Check Tools quando a chave está configurada
- Usa Google Search via Gemini para enriquecer a checagem
- Persiste o histórico em SQLite

## Tecnologias

- FastAPI
- Uvicorn
- Google GenAI SDK
- HTTPX
- SQLAlchemy
- SQLite
- BeautifulSoup4

## Requisitos

- Python 3.12 ou superior
- Um ambiente virtual recomendado
- Chave `GEMINI_API_KEY`

Chaves opcionais:

- `GOOGLE_FACTCHECK_API_KEY`
- `NEWS_API_KEY`

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com pelo menos:

```env
GEMINI_API_KEY=sua_chave_aqui
```

Opcionalmente:

```env
GOOGLE_FACTCHECK_API_KEY=sua_chave_aqui
NEWS_API_KEY=sua_chave_aqui
```

## Instalação

Ative seu ambiente virtual e instale as dependências:

```bash
pip install -r requirements.txt
```

## Como rodar

Inicie a API com o Uvicorn:

```bash
uvicorn main:app --reload
```

Por padrão, a aplicação sobe em:

```bash
http://127.0.0.1:8000
```

## Endpoints principais

- `GET /`
- `POST /verify/text`
- `POST /verify/url`
- `POST /verify/image`
- `GET /history`
- `GET /history/{verification_id}`
- `DELETE /history/{verification_id}`

## Banco de dados

O backend usa um banco SQLite local chamado `veritais.db`. O arquivo é criado automaticamente na primeira execução, caso ainda não exista.

## Fluxo das análises

1. O conteúdo é recebido pela API.
2. O backend tenta buscar sinais externos com Google Fact Check, quando configurado.
3. O Gemini recebe o conteúdo e gera uma análise estruturada.
4. O resultado é salvo no banco.
5. A resposta final é enviada ao front-end.

## Estrutura principal

- `main.py`: rotas da API e integração com o Gemini
- `analyzer.py`: schema de resposta e construção de prompt
- `factcheck.py`: integrações com Google Fact Check e NewsAPI
- `models.py`: modelos e configuração do SQLite
- `veritais.db`: banco local de histórico

## Observações

- O backend libera CORS para todas as origens.
- A rota de imagem aceita arquivos `jpeg`, `png`, `webp` e `gif`.
- Se a chave `GEMINI_API_KEY` não estiver definida, a aplicação não sobe corretamente.







## VeritasAI Backend
The API responsible for content analysis and fact-checking within the VeritasAI application. This project processes text, URLs, and images, queries external sources when available, and utilizes Gemini to generate a structured verdict on the submitted content.

In addition to the analysis, the backend saves each verification to a local SQLite database and exposes a query history.

## What the API Does
Analyzes text statements.

Extracts and analyzes content from URLs.

Performs multimodal analysis on images.

Queries Google Fact Check Tools (when the API key is configured).

Uses Google Search via Gemini to enrich fact-checking.

Persists verification history in SQLite.

## Technologies
FastAPI

Uvicorn

Google GenAI SDK

HTTPX

SQLAlchemy

SQLite

BeautifulSoup4

## Requirements
Python 3.12 or higher.

A virtual environment is highly recommended.

GEMINI_API_KEY (Required).

## Optional Keys:

GOOGLE_FACTCHECK_API_KEY

NEWS_API_KEY

## Environment Variables
Create a .env file in the root directory of the project containing at least:

Snippet de código


GEMINI_API_KEY=your_key_here
Optionally, you can add:

## Snippet de código


GOOGLE_FACTCHECK_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
Installation
Activate your virtual environment and install the dependencies:

## Bash


pip install -r requirements.txt
How to Run
Start the API using Uvicorn:

## Bash


uvicorn main:app --reload
By default, the application will run at: http://127.0.0.1:8000

Main Endpoints
GET /

POST /verify/text

POST /verify/url

POST /verify/image

GET /history

GET /history/{verification_id}

DELETE /history/{verification_id}

## Database
The backend uses a local SQLite database named veritais.db. This file is automatically created upon the first execution if it does not already exist.

Analysis Workflow
Input: Content is received by the API.

External Search: The backend attempts to fetch external signals using Google Fact Check (if configured).

AI Processing: Gemini receives the content and generates a structured analysis.

Persistence: The result is saved to the database.

Output: The final response is sent back to the frontend.

## Core Structure
main.py: API routes and Gemini integration.

analyzer.py: Response schemas and prompt engineering.

factcheck.py: Integrations with Google Fact Check and NewsAPI.

models.py: Database models and SQLite configuration.

veritais.db: Local database containing the history.

## Notes
⚠️ Important: If the GEMINI_API_KEY is not defined, the application will fail to start.

The backend has CORS enabled for all origins.

The image route accepts jpeg, png, webp, and gif file formats.
