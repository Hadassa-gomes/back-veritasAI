import json
import re


def build_analysis_prompt(
    content: str,
    url: str = "",
    title: str = "VeritasAI",
    extra_context: str = "",
    factcheck_data: list = None
) -> str:
    
    factcheck_section = ""
    if factcheck_data:
        factcheck_section = f"""
## Resultados de fact-checkers externos:
{json.dumps(factcheck_data, ensure_ascii=False, indent=2)}
"""

    url_section = f"URL de origem: {url}" if url else ""
    title_section = f"Título: {title}" if title else ""
    context_section = f"Contexto adicional: {extra_context}" if extra_context else ""

    prompt = f"""Você é um jornalista especialista em verificação de fatos (fact-checking) com amplo conhecimento em identificar desinformação, fake news e conteúdo manipulado.

## Conteúdo para análise:
{url_section}
{title_section}
{context_section}

---
{content[:4000]}
---
{factcheck_section}

## Sua tarefa:
Analise criticamente o conteúdo acima e responda APENAS com um JSON válido neste formato exato (sem markdown, sem texto extra):

{{
  "verdict": "VERDADEIRO|FALSO|SUSPEITO|INCONCLUSIVO",
  "confidence": <número inteiro de 0 a 100>,
  "summary": "<resumo do veredito em 1 frase clara em português>",
  "analysis": "<análise detalhada em português com os seguintes pontos:\\n\\n1. O que afirma o conteúdo\\n2. Evidências a favor ou contra\\n3. Fontes confiáveis sobre o tema\\n4. Técnicas de desinformação identificadas (se houver)\\n5. Conclusão final>"
}}

## Critérios de veredito:
- **VERDADEIRO**: Afirmação confirmada por fontes confiáveis, sem distorções
- **FALSO**: Afirmação claramente incorreta, contradiz evidências verificáveis
- **SUSPEITO**: Contém elementos verdadeiros misturados com distorções ou falta contexto importante
- **INCONCLUSIVO**: Sem informação suficiente para determinar a veracidade

## Critérios de confiança (0–100):
- 90–100: Certeza elevada, múltiplas fontes confirmam
- 70–89: Alta confiança, evidências claras
- 50–69: Confiança moderada, algumas evidências
- 30–49: Baixa confiança, poucas evidências
- 0–29: Muito incerto, quase sem evidências

Responda APENAS com o JSON, sem qualquer texto antes ou depois."""

    return prompt


def parse_verdict(raw_text: str) -> dict:
    
    # Estratégia 1: Tenta parsear diretamente
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # Estratégia 2: Extrai JSON entre chaves
    try:
        match = re.search(r'\{[\s\S]*\}', raw_text)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass

    # Estratégia 3: Remove blocos de código markdown
    try:
        cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', raw_text).strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: retorna estrutura padrão com o texto bruto
    return {
        "verdict": "INCONCLUSIVO",
        "confidence": 0,
        "summary": "Não foi possível processar a análise automaticamente.",
        "analysis": raw_text
    }
