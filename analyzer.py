"""
analyzer.py — Esquemas de validação e prompts para o Gemini
"""

import json
from pydantic import BaseModel, Field

# Definição da estrutura exata que o Gemini DEVE retornar
class FactCheckSchema(BaseModel):
    verdict: str = Field(description="O veredito da análise. Deve ser obrigatoriamente um destes: VERDADEIRO, FALSO, SUSPEITO ou INCONCLUSIVO")
    confidence: int = Field(description="Número inteiro de 0 a 100 indicando o grau de certeza da análise")
    summary: str = Field(description="Resumo do veredito em exatamente 1 frase clara em português")
    analysis: str = Field(description="Análise detalhada em português abordando o que o conteúdo afirma, evidências, fontes e técnicas de desinformação")


def build_analysis_prompt(
    content: str,
    url: str = "",
    title: str = "VeritaisAI",
    extra_context: str = "",
    factcheck_data: list = None
) -> str:
    """
    Monta o prompt focado no contexto do conteúdo. 
    A formatação do JSON agora é garantida pelo GenerateContentConfig (Structured Outputs).
    """
    factcheck_section = ""
    if factcheck_data:
        factcheck_section = f"\n## Resultados de fact-checkers externos de referência:\n{json.dumps(factcheck_data, ensure_ascii=False, indent=2)}\n"

    url_section = f"URL de origem: {url}" if url else ""
    title_section = f"Título: {title}" if title else ""
    context_section = f"Contexto adicional relevante: {extra_context}" if extra_context else ""

    prompt = f"""Você é um jornalista especialista em verificação de fatos (fact-checking) com amplo conhecimento em identificar desinformação, fake news e conteúdo manipulado.

## Conteúdo que você deve analisar criteriosamente:
{url_section}
{title_section}
{context_section}

---
{content[:4000]}
---
{factcheck_section}

## Sua Tarefa:
Avalie minuciosamente o conteúdo acima estruturando sua resposta de acordo com o esquema de dados fornecido.

Critérios para definição do campo 'verdict':
- VERDADEIRO: Afirmação confirmada por fontes confiáveis, sem distorções.
- FALSO: Afirmação claramente incorreta, que contradiz evidências verificáveis.
- SUSPEITO: Contém elementos verdadeiros misturados com distorções ou que carecem de contexto importante.
- INCONCLUSIVO: Sem informação suficiente para determinar a veracidade de forma justa.
"""
    return prompt