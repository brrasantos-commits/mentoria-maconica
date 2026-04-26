from typing import Any

from pitch_app.services.config import MAX_TEXT_CHARS_PER_MATERIAL

SCORE_ITEM = {
    "type": "object",
    "properties": {
        "score": {"type": "number"},
        "justification": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["score", "justification", "evidence"],
    "additionalProperties": False,
}

DEVELOPER_PROMPT = """
Você é um avaliador sênior de treinamento comercial.

Sua tarefa é avaliar um pitch de vendas comparando:
1. a transcrição do vendedor
2. os materiais de apoio selecionados

Regras:
- Seja rigoroso, objetivo e acionável.
- Não invente fatos.
- Só considere como coberto aquilo que estiver claramente presente na transcrição.
- Quando algo estiver ausente, diga explicitamente que não foi encontrado.
- Use notas de 0 a 5.
- Sempre traga evidências curtas, literais ou parafraseadas, retiradas da transcrição.
- Diferencie bem:
  a) qualidade geral do pitch
  b) aderência aos materiais
  c) critérios avançados de storytelling, indústria, proposta de valor e posicionamento

Importante:
- A resposta deve refletir profundidade analítica.
- Evite respostas genéricas.
- As justificativas devem explicar o porquê da nota.
- As evidências devem ser curtas, objetivas e rastreáveis ao pitch.
""".strip()


def build_materials_text(materials: dict[str, str]) -> str:
    blocks: list[str] = []
    for key, value in materials.items():
        blocks.append(f"## MATERIAL: {key.upper()}\n{value[:MAX_TEXT_CHARS_PER_MATERIAL]}")
    return "\n\n".join(blocks)


def build_prompts(materials_text: str, transcript_text: str) -> tuple[str, str]:
    user_prompt = f"""
# MATERIAIS DE REFERÊNCIA
{materials_text}

# PITCH TRANSCRITO
{transcript_text}

# CRITÉRIOS PRINCIPAIS
1. clareza da proposta de valor
2. estrutura
3. argumentação comercial
4. conexão com o cliente
5. call to action
6. fluidez

# CRITÉRIOS AVANÇADOS
7. Elevator Pitch focado em missão crítica e baseado em storytelling estratégico
8. Principais dores da indústria consideradas
9. Proposta de valor, resolutividade técnica e diferenciais da solução abordados
10. Features principais da solução demonstradas
11. Serviços Tecnocomp abordados
    (Assessment, Configuração, Instalação, Segurança, Monitoramento NOC/SOC 24x7,
     Suporte N1/N2/N3 e observabilidade)
12. Referências e cases apresentados
13. Porque Tecnocomp
    (42 anos de experiência, presença em mais de 880 cidades,
     excelência comprovada – certificações ISO 9001, 20000, 27001,
     referência nacional em gestão de serviços de TI,
     monitoramento contínuo via command center 24x7,
     especialistas dedicados à continuidade do negócio)
14. Próximos passos / call to action
15. Frases de fechamento impactantes

# INSTRUÇÕES DE SAÍDA
- Avalie cada critério com profundidade.
- Analise separadamente a aderência a cada material.
- Em "summary", faça um resumo executivo consistente.
- Em "improved_pitch", gere uma versão melhorada e mais forte do pitch.
- Em "strengths", liste pontos fortes reais observados.
- Em "improvements", liste melhorias práticas e acionáveis.
- Em "must_fix_first", liste os pontos prioritários.
""".strip()
    return DEVELOPER_PROMPT, user_prompt


def build_material_schema(material_names: list[str]) -> dict[str, Any]:
    material_props: dict[str, Any] = {}
    for name in material_names:
        material_props[name] = {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "covered_points": {"type": "array", "items": {"type": "string"}},
                "missing_points": {"type": "array", "items": {"type": "string"}},
                "critical_gaps": {"type": "array", "items": {"type": "string"}},
                "evidence_from_pitch": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "score",
                "covered_points",
                "missing_points",
                "critical_gaps",
                "evidence_from_pitch",
            ],
            "additionalProperties": False,
        }
    return material_props


def build_advanced_criteria_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "elevator_pitch_missao_critica": SCORE_ITEM,
            "dores_da_industria": SCORE_ITEM,
            "proposta_valor_diferenciais": SCORE_ITEM,
            "features_principais": SCORE_ITEM,
            "servicos_tecnocomp": SCORE_ITEM,
            "referencias_cases": SCORE_ITEM,
            "porque_tecnocomp": SCORE_ITEM,
            "proximos_passos": SCORE_ITEM,
            "frases_fechamento": SCORE_ITEM,
        },
        "required": [
            "elevator_pitch_missao_critica",
            "dores_da_industria",
            "proposta_valor_diferenciais",
            "features_principais",
            "servicos_tecnocomp",
            "referencias_cases",
            "porque_tecnocomp",
            "proximos_passos",
            "frases_fechamento",
        ],
        "additionalProperties": False,
    }


def build_evaluation_schema(material_names: list[str]) -> dict[str, Any]:
    material_props = build_material_schema(material_names)

    return {
        "name": "pitch_multi_material_evaluation",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "object",
                    "properties": {
                        "clareza": SCORE_ITEM,
                        "estrutura": SCORE_ITEM,
                        "argumentacao": SCORE_ITEM,
                        "conexao": SCORE_ITEM,
                        "cta": SCORE_ITEM,
                        "fluidez": SCORE_ITEM,
                    },
                    "required": [
                        "clareza",
                        "estrutura",
                        "argumentacao",
                        "conexao",
                        "cta",
                        "fluidez",
                    ],
                    "additionalProperties": False,
                },
                "advanced_criteria": build_advanced_criteria_schema(),
                "material_adherence": {
                    "type": "object",
                    "properties": material_props,
                    "required": material_names,
                    "additionalProperties": False,
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
                "improvements": {"type": "array", "items": {"type": "string"}},
                "must_fix_first": {"type": "array", "items": {"type": "string"}},
                "improved_pitch": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": [
                "scores",
                "advanced_criteria",
                "material_adherence",
                "strengths",
                "improvements",
                "must_fix_first",
                "improved_pitch",
                "summary",
            ],
            "additionalProperties": False,
        },
    }