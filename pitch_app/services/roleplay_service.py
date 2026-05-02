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

def generate_ai_response(conversation: list[dict]) -> str:
    client: OpenAI = get_openai_client()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content