"""
Veritais - Backend de Verificação de Fake News
FastAPI + Novo SDK Google GenAI + Google Fact Check API + GOOGLE SEARCH
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup  # Para limpeza do HTML
from dotenv import load_dotenv # Para gerenciamento de ambiente

# Importação do NOVO SDK moderno e oficial do Google Gemini
from google import genai
from google.genai import types

# Importações internas
from models import SessionLocal, Verification, init_db
from factcheck import check_google_factcheck
from analyzer import build_analysis_prompt, FactCheckSchema

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações de chaves obtidas de forma segura
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TARGET_MODEL = "gemini-2.0-flash"

if not GEMINI_KEY:
    raise RuntimeError("A variável de ambiente GEMINI_API_KEY não foi configurada no arquivo .env")

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Veritais API",
    description="API de verificação de fake news com IA conectada à Internet em tempo real",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa banco de dados SQLite automaticamente
init_db()

def get_temporal_context():
    """Retorna a data atual para injeção de contexto no Gemini."""
    return f"Hoje é dia {datetime.now().strftime('%d/%m/%Y')}."

# ─── Schemas ──────────────────────────────────────────────────────────────────

class URLRequest(BaseModel):
    url: str
    context: Optional[str] = ""

class TextRequest(BaseModel):
    text: str
    title: Optional[str] = ""

class VerificationResponse(BaseModel):
    id: int
    verdict: str                  # "VERDADEIRO" | "FALSO" | "SUSPEITO" | "INCONCLUSIVO"
    confidence: int               # 0–100
    summary: str
    analysis: str                 # Texto limpo para renderização no front
    sources_found: list
    checked_at: str

# ─── Rotas ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Veritais API (Connected to Google Search)",
        "status": "online",
        "endpoints": ["/verify/url", "/verify/text", "/verify/image", "/history"]
    }

@app.post("/verify/url", response_model=VerificationResponse)
async def verify_url(req: URLRequest):
    """Verifica uma notícia a partir de uma URL extraindo seu conteúdo de texto limpo."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as http:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Veritais/1.0)"}
            page = await http.get(req.url, headers=headers)
            
            # Limpa o HTML extraindo apenas o texto visível real
            soup = BeautifulSoup(page.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Não foi possível acessar ou ler a URL: {str(e)}")

    factcheck_results = await check_google_factcheck(page_text[:500])

    prompt = build_analysis_prompt(
        content=f"{get_temporal_context()} {page_text}",
        url=req.url,
        extra_context=req.context,
        factcheck_data=factcheck_results
    )

    try:
        client_secure = genai.Client(api_key=GEMINI_KEY)
        
        # Etapa 1: Ativa o Google Search (Sem forçar Mime Type JSON) para fazer a checagem
        config_busca = types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
        response_busca = client_secure.models.generate_content(
            model=TARGET_MODEL,
            contents=prompt,
            config=config_busca
        )
        analise_bruta = response_busca.text

        # Etapa 2: Pega o resultado estruturado na Etapa 1 e formata no Pydantic Schema esperado
        config_json = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FactCheckSchema
        )
        response_estruturada = client_secure.models.generate_content(
            model=TARGET_MODEL,
            contents=f"Formate a seguinte análise de fatos estritamente de acordo com o esquema solicitado:\n\n{analise_bruta}",
            config=config_json
        )
        
        verdict_data = json.loads(response_estruturada.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na API do Gemini: {str(e)}")

    db = SessionLocal()
    try:
        verification = Verification(
            input_type="url",
            input_value=req.url,
            verdict=verdict_data.get("verdict", "INCONCLUSIVO"),
            confidence=verdict_data.get("confidence", 0),
            summary=verdict_data.get("summary", ""),
            analysis=verdict_data.get("analysis", ""),
            sources_found=json.dumps(factcheck_results),
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        record_id = verification.id
        created_at = verification.created_at
    finally:
        db.close()

    return VerificationResponse(
        id=record_id,
        verdict=verification.verdict,
        confidence=verification.confidence,
        summary=verification.summary,
        analysis=verification.analysis,
        sources_found=factcheck_results,
        checked_at=created_at.isoformat()
    )


@app.post("/verify/text", response_model=VerificationResponse)
async def verify_text(req: TextRequest):
    """Verifica um texto ou afirmação diretamente via Gemini com acesso ao Google."""
    factcheck_results = await check_google_factcheck(req.text[:500])

    prompt = build_analysis_prompt(
        content=f"{get_temporal_context()} Analise a seguinte afirmação: {req.text}",
        title=req.title,
        factcheck_data=factcheck_results
    )

    try:
        client_secure = genai.Client(api_key=GEMINI_KEY)
        
        # Etapa 1: Ativa o Google Search (Sem forçar Mime Type JSON) para fazer a checagem
        config_busca = types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
        response_busca = client_secure.models.generate_content(
            model=TARGET_MODEL,
            contents=prompt,
            config=config_busca
        )
        analise_bruta = response_busca.text

        # Etapa 2: Pega o resultado estruturado na Etapa 1 e formata no Pydantic Schema esperado
        config_json = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=FactCheckSchema
        )
        response_estruturada = client_secure.models.generate_content(
            model=TARGET_MODEL,
            contents=f"Formate a seguinte análise de fatos estritamente de acordo com o esquema solicitado:\n\n{analise_bruta}",
            config=config_json
        )
        
        verdict_data = json.loads(response_estruturada.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na API do Gemini: {str(e)}")

    db = SessionLocal()
    try:
        verification = Verification(
            input_type="text",
            input_value=req.text[:500],
            verdict=verdict_data.get("verdict", "INCONCLUSIVO"),
            confidence=verdict_data.get("confidence", 0),
            summary=verdict_data.get("summary", ""),
            analysis=verdict_data.get("analysis", ""),
            sources_found=json.dumps(factcheck_results),
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        record_id = verification.id
        created_at = verification.created_at
    finally:
        db.close()

    return VerificationResponse(
        id=record_id,
        verdict=verification.verdict,
        confidence=verification.confidence,
        summary=verification.summary,
        analysis=verification.analysis,
        sources_found=factcheck_results,
        checked_at=created_at.isoformat()
    )


@app.post("/verify/image", response_model=VerificationResponse)
async def verify_image(file: UploadFile = File(...)):
    """Analisa uma imagem em busca de desinformação mapeando a resposta de forma limpa."""
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")

    image_bytes = await file.read()

    instructions = f"""{get_temporal_context()} Você é um especialista em verificação de fatos e análise de mídia visual.
                    
Analise minuciosamente os elements textuais e o contexto gráfico contidos nesta imagem para preencher a estrutura de dados solicitada.
Verifique se há manipulações digitais óbvias, citações descontextualizadas ou elementos falsos."""

    try:
        client_secure = genai.Client(api_key=GEMINI_KEY)
        response = client_secure.models.generate_content(
            model=TARGET_MODEL,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=file.content_type,
                ),
                instructions
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FactCheckSchema  # Mantém consistência total
            )
        )
        verdict_data = json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na API multimodal do Gemini: {str(e)}")

    db = SessionLocal()
    try:
        verification = Verification(
            input_type="image",
            input_value=file.filename or "imagem_enviada",
            verdict=verdict_data.get("verdict", "INCONCLUSIVO"),
            confidence=verdict_data.get("confidence", 0),
            summary=verdict_data.get("summary", ""),
            analysis=verdict_data.get("analysis", ""),
            sources_found=json.dumps([]),
        )
        db.add(verification)
        db.commit()
        db.refresh(verification)
        record_id = verification.id
        created_at = verification.created_at
    finally:
        db.close()

    return VerificationResponse(
        id=record_id,
        verdict=verification.verdict,
        confidence=verification.confidence,
        summary=verification.summary,
        analysis=verification.analysis,
        sources_found=[],
        checked_at=created_at.isoformat()
    )


@app.get("/history")
def get_history(limit: int = 20, skip: int = 0):
    db = SessionLocal()
    try:
        verifications = db.query(Verification).order_by(Verification.created_at.desc()).offset(skip).limit(limit).all()
        return [
            {
                "id": v.id,
                "input_type": v.input_type,
                "input_value": v.input_value[:100],
                "verdict": v.verdict,
                "confidence": v.confidence,
                "summary": v.summary,
                "checked_at": v.created_at.isoformat()
            } for v in verifications
        ]
    finally:
        db.close()

@app.get("/history/{verification_id}")
def get_verification(verification_id: int):
    db = SessionLocal()
    try:
        v = db.query(Verification).filter(Verification.id == verification_id).first()
        if not v:
            raise HTTPException(status_code=404, detail="Verificação não encontrada.")
        return {
            "id": v.id,
            "input_type": v.input_type,
            "input_value": v.input_value,
            "verdict": v.verdict,
            "confidence": v.confidence,
            "summary": v.summary,
            "analysis": v.analysis,
            "sources_found": json.loads(v.sources_found or "[]"),
            "checked_at": v.created_at.isoformat()
        }
    finally:
        db.close()

@app.delete("/history/{verification_id}")
def delete_verification(verification_id: int):
    db = SessionLocal()
    try:
        v = db.query(Verification).filter(Verification.id == verification_id).first()
        if not v:
            raise HTTPException(status_code=404, detail="Verificação não encontrada.")
        db.delete(v)
        db.commit()
        return {"message": "Verificação removida com sucesso."}
    finally:
        db.close()