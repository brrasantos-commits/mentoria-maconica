
import os
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

from openai import OpenAI
from pitch_app.services.config import OPENAI_MODEL
from pitch_app.services.openai_service import get_openai_client

SYSTEM_PROMPT = """
Você é um cliente em uma simulação de vendas.

Seu comportamento:
- Seja realista e desafiador
- Faça perguntas difíceis
- Use objeções comuns:
  - preço
  - concorrência
  - falta de tempo
  - falta de prioridade
- NÃO ajude o vendedor
- NÃO dê respostas fáceis

Objetivo:
Simular uma conversa real de venda.
"""

def generate_ai_response(conversation: list[dict], material_texts: dict[str, str] | None = None) -> str:
    client: OpenAI = get_openai_client()

    material_context = ""

    if material_texts:
        material_context = "\n\nMateriais de estudo selecionados:\n"

        for filename, text in material_texts.items():
            material_context += f"\n### {filename}\n{text[:3000]}\n"

    system_prompt = SYSTEM_PROMPT + material_context

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation)

    try:

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=1200,
        )

        return response.choices[0].message.content

    except Exception as e:

        print("ERRO OPENAI:", str(e))

        return (
            "A IA está temporariamente indisponível. "
            "Verifique créditos, billing ou configuração da OpenAI."
        )

def evaluate_roleplay(conversation: list[dict]) -> dict:
    client: OpenAI = get_openai_client()

    transcript = ""
    for msg in conversation:
        role = "Vendedor" if msg["role"] == "user" else "Cliente"
        transcript += f"{role}: {msg['content']}\n"

    system_prompt = """
Você é um especialista em avaliação de vendas.

Analise o desempenho do vendedor no roleplay e retorne:

- score geral (0 a 100)
- clareza
- proposta de valor
- domínio do material
- tratamento de objeções
- fechamento

Também forneça:
- pontos fortes
- pontos de melhoria

Responda em JSON no formato:
{
  "score": 0,
  "clarity": 0,
  "value": 0,
  "knowledge": 0,
  "objections": 0,
  "closing": 0,
  "strengths": [],
  "improvements": []
}
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ],
        temperature=0,
    )

    import json
    return json.loads(response.choices[0].message.content)

from openai import RateLimitError