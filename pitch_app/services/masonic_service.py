import json
from typing import Any

from openai import OpenAI

from pitch_app.services.config import OPENAI_MODEL, MAX_TEXT_CHARS_PER_MATERIAL
from pitch_app.services.openai_service import get_openai_client


BOARD_SCHEMA = {
    "name": "masonic_board_evaluation",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "final_score": {"type": "number"},
            "summary": {"type": "string"},
            "criteria": {
                "type": "object",
                "properties": {
                    "estrutura": {"type": "number"},
                    "profundidade": {"type": "number"},
                    "simbolismo": {"type": "number"},
                    "clareza": {"type": "number"},
                    "originalidade": {"type": "number"},
                    "aderencia_ritualistica": {"type": "number"},
                },
                "required": [
                    "estrutura",
                    "profundidade",
                    "simbolismo",
                    "clareza",
                    "originalidade",
                    "aderencia_ritualistica",
                ],
                "additionalProperties": False,
            },
            "strengths": {"type": "array", "items": {"type": "string"}},
            "improvements": {"type": "array", "items": {"type": "string"}},
            "references": {"type": "array", "items": {"type": "string"}},
            "recommended_studies": {"type": "array", "items": {"type": "string"}},
            "improved_outline": {"type": "string"},
        },
        "required": [
            "final_score",
            "summary",
            "criteria",
            "strengths",
            "improvements",
            "references",
            "recommended_studies",
            "improved_outline",
        ],
        "additionalProperties": False,
    },
}


def build_materials_context(material_texts: dict[str, str]) -> str:
    blocks: list[str] = []
    for filename, text in material_texts.items():
        blocks.append(
            f"## MATERIAL AUTORIZADO: {filename}\n"
            f"{(text or '')[:MAX_TEXT_CHARS_PER_MATERIAL]}"
        )
    return "\n\n".join(blocks)


def evaluate_board(
    board_text: str,
    material_texts: dict[str, str],
    grade_name: str = "",
    rite: str = "",
) -> dict[str, Any]:
    client: OpenAI = get_openai_client()
    materials_context = build_materials_context(material_texts)

    system_prompt = """
Você é um avaliador de pranchas maçônicas, com postura fraterna, criteriosa e prudente.

Regras de governança:
- Use apenas a prancha enviada e os materiais autorizados no contexto.
- Não invente rituais, landmarks, palavras, sinais, procedimentos ou decisões ritualísticas.
- Não substitua a avaliação de instrutores, Vigilantes, Venerável Mestre, Loja ou Potência.
- Se faltar base documental, diga que o ponto deve ser validado por autoridade competente.
- Avalie com notas de 0 a 100 no resultado final e 0 a 10 por critério.
""".strip()

    user_prompt = f"""
# CONTEXTO DO USUÁRIO
Grau: {grade_name or "não informado"}
Rito: {rite or "não informado"}

# MATERIAIS AUTORIZADOS
{materials_context or "Nenhum material selecionado."}

# PRANCHA PARA AVALIAÇÃO
{board_text}

# CRITÉRIOS
- Estrutura: organização, introdução, desenvolvimento e conclusão.
- Profundidade: nível reflexivo, maturidade e densidade filosófica.
- Simbolismo: coerência simbólica e conexão com os materiais.
- Clareza: comunicação, objetividade e compreensão.
- Originalidade: reflexão própria sem fugir da tradição.
- Aderência ritualística: compatibilidade com rito, grau e conteúdo autorizado.
""".strip()

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_schema", "json_schema": BOARD_SCHEMA},
        temperature=0.1,
        max_tokens=3000,
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("A IA não retornou conteúdo para a avaliação da prancha.")
    return json.loads(content)
