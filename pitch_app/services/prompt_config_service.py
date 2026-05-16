from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class PromptDefinition:
    key: str
    title: str
    module: str
    description: str
    default_prompt: str


DEFAULT_PROMPTS: dict[str, PromptDefinition] = {
    "study_chat.system": PromptDefinition(
        key="study_chat.system",
        title="Chat Inteligente - Prompt do sistema",
        module="Chat Inteligente",
        description="Define como a IA responde perguntas sobre materiais selecionados.",
        default_prompt="""
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
""".strip(),
    ),
    "roleplay.system": PromptDefinition(
        key="roleplay.system",
        title="Simulação - Prompt do mentor",
        module="Simulação",
        description="Define o comportamento da IA nas simulações de instrução e catecismo interativo.",
        default_prompt="""
Você é um mentor maçônico em uma simulação de instrução.

Seu comportamento:
- Seja respeitoso, exigente e fraterno.
- Faça perguntas sobre símbolos, rito, grau, história, filosofia e aplicação prática.
- Peça clareza, fundamentação e coerência com os materiais selecionados.
- Faça perguntas de catecismo interativo quando o material permitir.
- NÃO revele nem invente conteúdo ritualístico sigiloso.
- NÃO substitua instrutor, Vigilante ou Venerável Mestre.

Objetivo:
Treinar instrução, argumentação, didática, profundidade e condução ritualística responsável.
""".strip(),
    ),
    "roleplay.evaluation": PromptDefinition(
        key="roleplay.evaluation",
        title="Simulação - Prompt de avaliação",
        module="Simulação",
        description="Define como a IA avalia o desempenho do usuário na simulação.",
        default_prompt="""
Você é um especialista em avaliação de mentoria e instrução maçônica.

Analise o desempenho do irmão na simulação e retorne:

- score geral (0 a 100)
- clareza
- profundidade simbólica
- domínio do material
- coerência ritualística
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
""".strip(),
    ),
    "ritual_evaluation.developer": PromptDefinition(
        key="ritual_evaluation.developer",
        title="Avaliação Ritualística - Prompt do avaliador",
        module="Ritualística",
        description="Define as regras de avaliação de leitura, instrução oral ou apresentação.",
        default_prompt="""
Você é um avaliador sênior de estudos, instrução e mentoria maçônica.

Sua tarefa é avaliar uma leitura ritualística, instrução oral ou apresentação de estudo comparando:
1. a transcrição do irmão avaliado
2. os materiais de apoio selecionados e autorizados para o grau

Regras:
- Seja rigoroso, objetivo, respeitoso e acionável.
- Não invente fatos.
- Só considere como coberto aquilo que estiver claramente presente na transcrição.
- Quando algo estiver ausente, diga explicitamente que não foi encontrado.
- Use notas de 0 a 5.
- Sempre traga evidências curtas, literais ou parafraseadas, retiradas da transcrição.
- Diferencie bem:
  a) qualidade geral da leitura ou apresentação
  b) aderência aos materiais
  c) critérios avançados de fidelidade ritualística, simbolismo, didática, clareza, cadência e segurança
- Não revele, complete nem invente conteúdo ritualístico sigiloso.
- Se o material de referência não trouxer base suficiente, diga que é necessário validar com o instrutor, Vigilante ou Venerável Mestre.

Importante:
- A resposta deve refletir profundidade analítica.
- Evite respostas genéricas.
- As justificativas devem explicar o porquê da nota.
- As evidências devem ser curtas, objetivas e rastreáveis à transcrição.
""".strip(),
    ),
    "board.system": PromptDefinition(
        key="board.system",
        title="Pranchas - Prompt do avaliador",
        module="Pranchas",
        description="Define a postura e os limites da IA na avaliação de pranchas.",
        default_prompt="""
Você é um avaliador de pranchas maçônicas, com postura fraterna, criteriosa e prudente.

Regras de governança:
- Use apenas a prancha enviada e os materiais autorizados no contexto.
- Não invente rituais, landmarks, palavras, sinais, procedimentos ou decisões ritualísticas.
- Não substitua a avaliação de instrutores, Vigilantes, Venerável Mestre, Loja ou Potência.
- Se faltar base documental, diga que o ponto deve ser validado por autoridade competente.
- Avalie com notas de 0 a 100 no resultado final e 0 a 10 por critério.
""".strip(),
    ),
}


def iter_prompt_definitions() -> Iterable[PromptDefinition]:
    return DEFAULT_PROMPTS.values()


def ensure_ai_prompts_table(db: Session) -> None:
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS ai_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_key VARCHAR(120) NOT NULL UNIQUE,
            title VARCHAR(180) NOT NULL,
            module VARCHAR(80) NOT NULL,
            description TEXT,
            prompt_text TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    for item in iter_prompt_definitions():
        db.execute(text("""
            INSERT OR IGNORE INTO ai_prompts
            (prompt_key, title, module, description, prompt_text, active)
            VALUES (:key, :title, :module, :description, :prompt_text, 1)
        """), {
            "key": item.key,
            "title": item.title,
            "module": item.module,
            "description": item.description,
            "prompt_text": item.default_prompt,
        })


def get_ai_prompt(db: Session, prompt_key: str) -> str:
    default = DEFAULT_PROMPTS[prompt_key].default_prompt
    row = db.execute(text("""
        SELECT prompt_text, active
        FROM ai_prompts
        WHERE prompt_key = :key
    """), {"key": prompt_key}).fetchone()

    if not row or not row.active:
        return default

    text_value = (row.prompt_text or "").strip()
    return text_value or default


def get_ai_prompt_runtime(prompt_key: str) -> str:
    from pitch_app.db import SessionLocal

    db = SessionLocal()
    try:
        ensure_ai_prompts_table(db)
        prompt = get_ai_prompt(db, prompt_key)
        db.commit()
        return prompt
    finally:
        db.close()


def list_ai_prompts(db: Session) -> list[dict]:
    ensure_ai_prompts_table(db)
    rows = db.execute(text("""
        SELECT prompt_key, title, module, description, prompt_text, active, updated_at
        FROM ai_prompts
        ORDER BY module, title
    """)).fetchall()

    return [
        {
            "key": row.prompt_key,
            "title": row.title,
            "module": row.module,
            "description": row.description,
            "prompt_text": row.prompt_text,
            "active": bool(row.active),
            "updated_at": row.updated_at,
            "default_prompt": DEFAULT_PROMPTS[row.prompt_key].default_prompt
            if row.prompt_key in DEFAULT_PROMPTS else "",
        }
        for row in rows
    ]


def update_ai_prompt(db: Session, prompt_key: str, prompt_text: str, active: bool = True) -> None:
    if prompt_key not in DEFAULT_PROMPTS:
        raise ValueError("Prompt desconhecido")

    ensure_ai_prompts_table(db)
    db.execute(text("""
        UPDATE ai_prompts
        SET prompt_text = :prompt_text,
            active = :active,
            updated_at = CURRENT_TIMESTAMP
        WHERE prompt_key = :key
    """), {
        "key": prompt_key,
        "prompt_text": (prompt_text or "").strip() or DEFAULT_PROMPTS[prompt_key].default_prompt,
        "active": 1 if active else 0,
    })


def reset_ai_prompt(db: Session, prompt_key: str) -> None:
    if prompt_key not in DEFAULT_PROMPTS:
        raise ValueError("Prompt desconhecido")
    update_ai_prompt(db, prompt_key, DEFAULT_PROMPTS[prompt_key].default_prompt, True)
