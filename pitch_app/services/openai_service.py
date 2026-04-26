import json
from typing import Any

from openai import OpenAI

from pitch_app.services.config import OPENAI_API_KEY, OPENAI_MODEL
from pitch_app.services.exceptions import AppError
from pitch_app.services.prompt_service import build_evaluation_schema, build_materials_text, build_prompts


def get_openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise AppError('Defina OPENAI_API_KEY no ambiente da aplicação.', status_code=500)
    return OpenAI(api_key=OPENAI_API_KEY)


def evaluate_pitch(client: OpenAI, transcript_text: str, material_texts: dict[str, str], material_names: list[str]) -> dict[str, Any]:
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
        temperature=0,
    )
    content = response.choices[0].message.content
    if not content:
        raise AppError('O modelo não retornou uma avaliação válida.', status_code=500)
    return json.loads(content)