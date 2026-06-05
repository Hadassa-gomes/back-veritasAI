"""
factcheck.py — Integração com APIs externas de fact-checking
- Google Fact Check Tools API (gratuita)
- NewsAPI (100 req/dia grátis)
"""

import httpx
import os
from typing import Optional


# ─── Google Fact Check API ────────────────────────────────────────────────────

async def check_google_factcheck(query: str) -> list:
    """
    Consulta a API do Google Fact Check Tools.
    
    Como obter sua chave:
    1. Acesse https://console.developers.google.com/
    2. Crie um projeto e ative "Fact Check Tools API"
    3. Gere uma API Key e coloque em GOOGLE_FACTCHECK_API_KEY no .env
    
    Sem chave: retorna lista vazia (a verificação ainda funciona via Claude).
    """
    api_key = os.getenv("GOOGLE_FACTCHECK_API_KEY", "")
    if not api_key:
        return []                          # Continua sem a API externa

    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": query,
        "key": api_key,
        "languageCode": "pt",
        "pageSize": 5
    }

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        claims = data.get("claims", [])
        results = []

        for claim in claims:
            review = claim.get("claimReview", [{}])[0]
            results.append({
                "source": "Google Fact Check",
                "claim": claim.get("text", ""),
                "claimant": claim.get("claimant", ""),
                "rating": review.get("textualRating", ""),
                "publisher": review.get("publisher", {}).get("name", ""),
                "url": review.get("url", ""),
                "review_date": review.get("reviewDate", "")
            })

        return results

    except Exception as e:
        # Não quebra o fluxo se a API externa falhar
        print(f"[Fact Check API] Erro: {e}")
        return []


# ─── NewsAPI ──────────────────────────────────────────────────────────────────

async def check_newsapi(query: str) -> list:
    """
    Verifica se a notícia existe em veículos reais via NewsAPI.
    
    Como obter sua chave:
    1. Acesse https://newsapi.org/register
    2. Plano gratuito: 100 requisições/dia
    3. Coloque em NEWS_API_KEY no .env
    """
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key:
        return []

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query[:100],
        "apiKey": api_key,
        "language": "pt",
        "sortBy": "relevancy",
        "pageSize": 5
    }

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        articles = data.get("articles", [])
        results = []

        for article in articles:
            results.append({
                "source": "NewsAPI",
                "title": article.get("title", ""),
                "outlet": article.get("source", {}).get("name", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", "")
            })

        return results

    except Exception as e:
        print(f"[NewsAPI] Erro: {e}")
        return []
