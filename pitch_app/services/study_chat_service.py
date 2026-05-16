import os
from typing import Optional

from openai import OpenAI

from pitch_app.services.openai_service import get_openai_client
from pitch_app.services.config import OPENAI_MODEL


SYSTEM_PROMPT = """
Você é o Mentor Maçônico Inteligente da plataforma.

Objetivo:
- Ajudar Aprendizes, Companheiros, Mestres e Instrutores a estudar materiais autorizados.
- Responder dúvidas, explicar conceitos e resumir trechos.
- Apoiar pranchas, instruções, pesquisas, reflexão filosófica e evolução ritualística.

Regras:
- Use APENAS as informações contidas nos materiais fornecidos no contexto.
- Se a resposta não estiver nos materiais, diga claramente que não encontrou e peça mais contexto.
- Quando usar informações de um material, cite o nome do arquivo (ex.: "Fonte: arquivo.pdf").
- Respeite rito, grau, permissões e governança da Loja.
- Não invente rituais, landmarks, catecismos, sinais, palavras, procedimentos ou decisões ritualísticas.
- Não substitua instrutores, Vigilantes ou Venerável Mestre; recomende validação humana quando o tema exigir.
- Seja direto, didático, fraterno e prático.
""".strip()


def _build_material_context(material_texts: Optional[dict[str, str]]) -> str:
    if not material_texts:
        return ""

    # Hard limits to avoid huge prompts.
    per_material_limit = int(os.getenv("STUDY_CHAT_MATERIAL_CHARS_PER_FILE", "6000"))
    total_limit = int(os.getenv("STUDY_CHAT_MATERIAL_TOTAL_CHARS", "20000"))

    parts: list[str] = []
    used = 0

    for filename, text in material_texts.items():
        if used >= total_limit:
            break

        snippet = (text or "")[:per_material_limit]
        block = f"\n### {filename}\n{snippet}\n"

        if used + len(block) > total_limit:
            block = block[: max(0, total_limit - used)]

        parts.append(block)
        used += len(block)

    return "\n\nMateriais selecionados (conteúdo para referência):\n" + "".join(parts)


def generate_study_chat_response(
    conversation: list[dict],
    material_texts: Optional[dict[str, str]] = None,
) -> str:
    client: OpenAI = get_openai_client()

    system_prompt = SYSTEM_PROMPT + _build_material_context(material_texts)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1200,
    )

    return response.choices[0].message.content or "Não consegui gerar uma resposta agora."
