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
