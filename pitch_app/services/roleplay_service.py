
import os
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

from openai import OpenAI
from pitch_app.services.config import OPENAI_MODEL
from pitch_app.services.openai_service import get_openai_client

SYSTEM_PROMPT = """
Você é um mentor maçônico em uma simulação de instrução.

Seu comportamento:
- Seja respeitoso, sereno e exigente.
- Faça perguntas sobre os materiais selecionados.
- Peça clareza conceitual, contexto histórico, relação simbólica e aplicação prática.
- Não entregue respostas prontas; conduza o mentorado com perguntas e breves provocações.
- Não revele nem invente conteúdo ritualístico sigiloso.

Objetivo:
Simular uma conversa real de mentoria e instrução.
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
        role = "Mentorado" if msg["role"] == "user" else "Mentor"
        transcript += f"{role}: {msg['content']}\n"

    system_prompt = """
Você é um especialista em avaliação de mentoria maçônica.

Analise o desempenho do mentorado na simulação e retorne:

- score geral (0 a 100)
- clareza
- profundidade simbólica e conceitual
- domínio do material
- qualidade do diálogo
- síntese final

Também forneça:
- pontos fortes
- pontos de melhoria

Responda SOMENTE em JSON válido.
Não escreva texto antes ou depois do JSON.
Não use markdown.
Não use ```json.

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
    try:
        content = response.choices[0].message.content

        print("RETORNO IA EVALUATE:", content)

        return json.loads(content)

    except Exception as e:

        print("ERRO JSON ROLEPLAY:", str(e))

        return {
            "score": 0,
            "clarity": 0,
            "value": 0,
            "knowledge": 0,
            "objections": 0,
            "closing": 0,
            "strengths": [
                "Não foi possível processar a avaliação automaticamente."
            ],
            "improvements": [
                "Verifique se a IA retornou um JSON válido."
            ]
        }

from openai import RateLimitError
