import json
from typing import Any, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from pitch_app.services.config import OPENAI_API_KEY, OPENAI_MODEL
from pitch_app.services.exceptions import AppError
from pitch_app.services.prompt_service import build_evaluation_schema, build_materials_text, build_prompts


def get_openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise AppError('Defina OPENAI_API_KEY no ambiente da aplicação.', status_code=500)
    return OpenAI(api_key=OPENAI_API_KEY)


def evaluate_pitch(
    client: OpenAI,
    transcript_text: str,
    material_texts: dict[str, str],
    material_names: list[str],
    db: Optional[Session] = None,
    user_id: Optional[int] = None
) -> dict[str, Any]:
    materials_text = build_materials_text(material_texts)
    developer_prompt, user_prompt = build_prompts(materials_text, transcript_text)
    evaluation_schema = build_evaluation_schema(material_names)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {'role': 'developer', 'content': developer_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        response_format={'type': 'json_schema', 'json_schema': evaluation_schema},
        temperature=0.1,
        max_tokens=4000,
    )
    
    # Log usage
    content = response.choices[0].message.content

    print("=== RETORNO IA AVALIAÇÃO ===")
    print(content)
    print("=== FIM RETORNO IA ===")

    if not content:
        raise AppError(
            'O modelo não retornou uma avaliação válida.',
            status_code=500
        )

    try:

        return json.loads(content)

    except Exception as e:

        print("ERRO JSON OPENAI:", str(e))

        return {
            "final_score": 0,
            "status": "Erro",
            "analysis_confidence": 0,
            "evaluation": {
                "strengths": [
                    "Não foi possível processar a avaliação."
                ],
                "improvements": [
                    "A IA retornou um JSON inválido."
                ]
            }
        }