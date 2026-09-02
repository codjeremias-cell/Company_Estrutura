"""Validador determinístico do Departamento de Conteúdo e Marketing.

Valida pacote, metadata, proveniência, schema, envelopes internos, semântica dos
oito gates e a fronteira DEPARTMENT_RETURN contra o schema do Diretor.
"""

from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-conteudo-marketing.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"
OPERATIONS_ROOT = PACKAGE_ROOT.parent
DIRECTOR_ROOT = OPERATIONS_ROOT.parent
CEO_ROOT = DIRECTOR_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"
# TAREFA 36 — a fonte legada é PINADA, não viva.
#
# Até 2026-08-08 isto apontava para o `Catalogo-Skills-Unificado/skills` VIVO,
# com override por `LEGACY_CATALOG_ROOT`. O efeito: em 2026-08-06 o commit
# `58b202c` ("garimpo mattpocock/skills") melhorou duas skills do Catálogo, e
# este Departamento passou a REPROVAR — `redator-tecnologia-ia/SKILL.md` e
# `referencia/historico.md` com "hash divergente". Ninguém errou nada. O
# Catálogo é um acervo VIVO e evoluir é a função dele; a Estrutura derivou de
# UMA versão e é dessa versão que ela responde.
#
# Diagnosticado por medição em 2026-08-07: dos 11 arquivos declarados de
# `redator-tecnologia-ia`, **9 batiam exatamente** — o caminho, a receita e a
# declaração estavam sãos, e só o conteúdo de 2 havia mudado a montante. Não
# era EOL nem adulteração: era drift real de upstream, e a trava fez o trabalho
# dela ao acusar.
#
# O PINO, provado antes de ser adotado: as **28 de 28** declarações reproduzem
# exatamente no commit `be19002` (= `58b202c~1`, o estado anterior ao garimpo)
# — 9 reproduzem a partir do blob cru do git e 19 a partir do blob convertido
# para CRLF. Zero ausentes, zero que não batem em lugar nenhum. O snapshot em
# `fontes-legadas-pinadas/` carrega esses bytes verbatim, e o `.gitattributes`
# do cofre marca a pasta como `-text` para que nenhuma conversão de fim de
# linha os altere em qualquer checkout — sem isso os arquivos em LF virariam
# CRLF e a conferência quebraria sem um caractere ter mudado.
#
# CUIDADO COM O RÓTULO, e eu já errei este: "reproduz do blob cru" NÃO é o
# mesmo que "o arquivo é LF". Quatro dos 28 blobs do git JÁ carregam CRLF
# dentro, então batem crus e mesmo assim são CRLF em disco. A divisão real do
# snapshot é **5 arquivos puro-LF e 23 contendo CRLF**; publiquei "9 e 19" e
# esse par descreve qual receita reproduz o hash, não o fim de linha. Quem
# conferir a pasta contando terminadores de linha tem de esperar 5/23, não
# 9/19 — e 28/28 hashes conferindo é o que decide, não a contagem de EOL.
#
# O OVERRIDE POR AMBIENTE FOI REMOVIDO de propósito. Numa conferência de
# proveniência, poder apontar a raiz para outro lugar por variável de ambiente
# é bypass: quem não gosta do vermelho muda o alvo em vez do conteúdo.
#
# Consequência deliberada: este validador **não olha mais o Catálogo vivo**.
# Ressincronizar é ato explícito — mover o pino, recongelar o snapshot e
# redeclarar os hashes no mesmo ato —, não algo que acontece por acidente
# quando alguém melhora uma skill do acervo.
PINO_DA_FONTE_LEGADA = "be19002"  # 58b202c~1, anterior ao garimpo de 06/ago
LEGACY_ROOT = (PACKAGE_ROOT / "fontes-legadas-pinadas").resolve()

DEPARTMENT = "departamento-conteudo-marketing"
AGENT_CAPABILITY = {
    "agente-estrategia-conteudo-campanhas": "STRATEGY",
    "agente-narrativa-redacao": "NARRATIVE",
    "agente-direcao-arte-imagem": "VISUAL",
    "agente-roteiro-producao-video": "VIDEO",
    "agente-publicidade-conversao": "ADVERTISING",
    "agente-email-ciclo-de-vida": "EMAIL",
    "agente-inteligencia-relatoria-marketing": "INTELLIGENCE",
    "agente-governanca-marca-conformidade": "COMPLIANCE",
}
AGENT_NAMES = list(AGENT_CAPABILITY)
DISPLAY_NAMES = {
    "agente-estrategia-conteudo-campanhas": "Agente de Estratégia de Conteúdo",
    "agente-narrativa-redacao": "Agente de Narrativa e Redação",
    "agente-direcao-arte-imagem": "Agente de Direção de Arte e Imagem",
    "agente-roteiro-producao-video": "Agente de Roteiro e Produção de Vídeo",
    "agente-publicidade-conversao": "Agente de Publicidade e Conversão",
    "agente-email-ciclo-de-vida": "Agente de E-mail e Ciclo de Vida",
    "agente-inteligencia-relatoria-marketing": "Agente de Inteligência de Marketing",
    "agente-governanca-marca-conformidade": "Agente de Governança e Conformidade",
}
DIMENSIONS = [
    "BUSINESS_ALIGNMENT",
    "CLAIMS_EVIDENCE",
    "BRAND",
    "ACCESSIBILITY",
    "RIGHTS_PROVENANCE",
    "PRIVACY_CONSENT",
    "CHANNEL_POLICY",
    "MEASUREMENT",
]
DIMENSION_OWNER = {
    "BUSINESS_ALIGNMENT": "agente-estrategia-conteudo-campanhas",
    "CLAIMS_EVIDENCE": "agente-governanca-marca-conformidade",
    "BRAND": "agente-governanca-marca-conformidade",
    "ACCESSIBILITY": "agente-governanca-marca-conformidade",
    "RIGHTS_PROVENANCE": "agente-governanca-marca-conformidade",
    "PRIVACY_CONSENT": "agente-governanca-marca-conformidade",
    "CHANNEL_POLICY": "agente-governanca-marca-conformidade",
    "MEASUREMENT": "agente-inteligencia-relatoria-marketing",
}
RULES_LINK_DEPARTMENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md"

SOURCE_HASHES = {
    "redator-tecnologia-ia": {
        "agents/openai.yaml": "cd747d703991451bf5bc0865e1bde1518b857c5d9531c15f2b32de75b5f0df5f",
        "evals/evals.json": "43cafbc5dbce6fb93d3165ac5d6259bbf5c7b07380c4329e7e87a77f13c2b67e",
        "evals/placar-2026-07-20.md": "2e2f1f8a57d91c3a4c4019ffa550dfa0476fe7cf244ea19da84d2a66a98eab98",
        "referencia/auditoria-2026-07-20.md": "ed567442150c00d5cab4e3a1a30f0f072f107a3967d915fd2cfbfc223d1d7cc8",
        "referencia/confiabilidade-e-revisao.md": "71b7277cb7b8f8e54608554952bec809bbfb37b400ddd0585b2819569528be28",
        "referencia/headlines-e-formatos.md": "c35e4ab38111863c1db71bff4d1c162d3baadbf07569b12ccba3bb4169e36eae",
        "referencia/historico.md": "86040bb2b82ea46f89fe5089b9f5926c81f0f5e4d9aa3d1f9be18c1d9e242286",
        "referencia/rascunho-v0-original.md": "d9106a1c5b4832783f5ce12b6e2c98085906ffffd2fea0315616ed8d041bbcf5",
        "referencia/voz-do-autor-corpus.md": "28a34ce1a7bb4a8f8e59df2c6f64b4b68bc2daf14ce0c435ecb96227322acbfb",
        "referencia/voz-e-tiques.md": "c8a7a7a34d0fde69b9acc836b2495c057dca1a3dd0add3ffffb6eb5c06577f72",
        "SKILL.md": "5d31d497753fe126a0dc00e1660eebe0caf36e8f1fdb0404b934c71f71856fcd",
    },
    "email-marketing-html": {
        "agents/openai.yaml": "f7fb4eb352c62b51f6323c67ba770247a756fdb51864475bd5f9b84b00cd1fdd",
        "referencia/auditoria-2026-07-20.md": "a3566a0bb6eb6fee89f0da6f68be24f64f86d674db3099408f81d348926ba3ae",
        "referencia/checklist-compatibilidade.md": "ee7323b83face8914b0b81324dac274ee344fe65ba499c68d607113125b90e6c",
        "referencia/exemplos/assets/beneficio-frete.png": "f5047f83785e833a006137d8baf973486edc04af9cb279d5fb7c01b2c377f92d",
        "referencia/exemplos/assets/beneficio-parcela.png": "845fcc2cd254e9e31c774f88e76e24038188cf4c756fb5dbc4bc02e1be4b6efd",
        "referencia/exemplos/assets/generate_banners.py": "6697856833f07f47bd0ffe1f24477ebb7bdf0d84067302cf47d154945441d02a",
        "referencia/exemplos/assets/hero-banner.png": "a9bf32f6eeca9638783b2b7414a3d10af69db5a585277565bf19803a4507f3d2",
        "referencia/exemplos/assets/urgencia-strip.png": "f9fe1d80ced60aae1ccecc54891ff67ed039baccbce39bb970b3b563307856d5",
        "referencia/exemplos/exemplo-01-briefing.md": "4b1dfbe2058829ae513785b34d72ea69980bb67502514541dd2f991a51474eac",
        "referencia/exemplos/exemplo-01-lancamento-curso.html": "a4944d1436ec38b82f5624d076dbbe0489af15404b1d95c5b3b70f7153377c17",
        "referencia/exemplos/exemplo-02-banner-promocional.html": "3441aa106c51ce1233f6c21954284da3e65518595e627a5feb63fa2fc5cb9896",
        "referencia/exemplos/exemplo-02-briefing.md": "f3ba667dc188f702144c49e30a29ebc269811ef07ca296388b4439a8a6329c07",
        "referencia/historico.md": "0f5725294264112e605b69b1bb080c657894d42d6db37549babb0212c7e3910d",
        "referencia/mjml-guia.md": "cb35fa72dc532b96488a332d626301f3da2eb6e0d2fa1845675d74b4cc450ab5",
        "scripts/lint-email.py": "36fb94a0f70fe55927c4f6fa11ca586e15b3a9e5208fd0ef024517a5adb91687",
        "SKILL.md": "249351c9e4e630536def50818eeab33e31990fcf079a81c8e3de4469d6cddc26",
        "template/template-base.html": "534f0858fb623404bed01da6c30f745aaff31b7bc49dd7945976e2b57a57c841",
    },
}

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_agents_folder,
        validate_frontmatter,
        validate_links,
        validate_openai_yaml,
        validate_required_files,
    )
    from _compartilhado.verificacoes_estrutura import (  # noqa: E402
        recusar_execucao_fora_da_fonte,
        validate_adr_series,
        validate_cobertura_de_validadores,
        validate_contratos_de_gerente,
        validate_fonte_normativa_conferida,
        validate_placar_nao_declara_cadeia,
        achar_corpo_neutralizado,
        achar_pendencia_sem_dono,
        validate_contagem_ligada_ao_instrumento,
        validate_travas_compartilhadas_com_efeito,
        validate_pendencia_tem_dono,
        validate_sem_check_tautologico,
        validate_trava_de_digest,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(f"[FAIL] motor compartilhado ausente em {STRUCTURE_ROOT}: {exc}")
    raise SystemExit(1)
except ImportError as exc:  # pragma: no cover
    # `ModuleNotFoundError` é SUBCLASSE de `ImportError`: o handler acima não
    # captura o pai. Sem este segundo braço, aplicar os validadores sem o
    # `_compartilhado` atualizado mata o processo por traceback, sem sumário e
    # sem dizer qual condição faltou — o modo de falha que este candidato
    # existe para repudiar. Medido na rodada 1: dez validadores assim.
    print(
        "[FAIL] OVERLAY_APLICADO_PELA_METADE: _compartilhado existe mas não "
        f"expõe o que este validador importa ({exc}). Este conjunto é "
        "INDIVISÍVEL: validadores e _compartilhado/ se aplicam no mesmo ato, "
        "ou a fonte normativa fica sem conferência nenhuma."
    )
    raise SystemExit(1)


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "contract_id": "contract-marketing-001",
        "contract_version": 1,
        "contract_digest": digest("0"),
        "department_mission_ref": "department-mission-marketing-001",
        "round": 1,
        "producer": producer,
        "created_at": "2026-07-26T18:00:00-03:00",
    }


def brief(mode: str = "PRODUCTION_ONLY") -> dict[str, Any]:
    return {
        "artifact_type": "CONTENT_MARKETING_BRIEF",
        "brief_id": "brief-marketing-001",
        "causal": causal(),
        "business_context_refs": ["evidence/business-context-v1.json"],
        "objective": "Preparar o lançamento rastreável do produto.",
        "audiences": ["Gestores de pequenas empresas."],
        "value_propositions": ["Reduz retrabalho operacional comprovável."],
        "offers": ["Demonstração sem promessa de resultado."],
        "journey_stages": ["descoberta", "consideracao", "decisao"],
        "channels": ["site", "email", "video", "paid-media"],
        "required_assets": ["narrativa", "imagem", "video", "anuncio", "email", "relatorio"],
        "facts": ["O produto possui demonstração funcional registrada."],
        "hypotheses": ["A demonstração pode aumentar interesse qualificado."],
        "claims_requiring_evidence": ["Reduz retrabalho operacional."],
        "constraints": ["Não prometer venda nem resultado."],
        "measurement_objectives": ["Medir visitas e pedidos de demonstração."],
        "execution_mode": mode,
        "authorization_refs": (
            ["auth/activation-001.json"] if mode == "AUTHORIZED_ACTIVATION" else []
        ),
        "status": "READY",
    }


def assignment(
    agent: str = "agente-narrativa-redacao",
    mode: str = "PRODUCTION_ONLY",
) -> dict[str, Any]:
    return {
        "artifact_type": "MARKETING_ASSIGNMENT",
        "assignment_id": f"assignment-{AGENT_CAPABILITY[agent].lower()}-001",
        "causal": causal(),
        "brief_ref": "brief-marketing-001",
        "agent_id": agent,
        "capability": AGENT_CAPABILITY[agent],
        "objective": "Executar a fronteira contratada sem ampliar escopo.",
        "input_refs": ["briefs/brief-marketing-001.json"],
        "required_output": ["Entregável versionado da capacidade."],
        "required_evidence": ["Artefato real e verificação aplicável."],
        "execution_mode": mode,
        "authorization_refs": (
            ["auth/activation-001.json"] if mode == "AUTHORIZED_ACTIVATION" else []
        ),
        "forbidden_actions": [
            "Não publicar, enviar, gastar ou usar conta sem autorização.",
            "Não assumir capacidade de agente irmão.",
        ],
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T18:05:00-03:00",
    }


def deliverable(agent: str = "agente-narrativa-redacao") -> dict[str, Any]:
    return {
        "artifact_type": "MARKETING_DELIVERABLE",
        "deliverable_id": f"deliverable-{AGENT_CAPABILITY[agent].lower()}-001",
        "causal": causal(agent),
        "assignment_ref": f"assignment-{AGENT_CAPABILITY[agent].lower()}-001",
        "brief_ref": "brief-marketing-001",
        "agent_id": agent,
        "capability": AGENT_CAPABILITY[agent],
        "artifact_refs": [f"artifacts/{AGENT_CAPABILITY[agent].lower()}-v1.md"],
        "evidence_refs": [f"evidence/{AGENT_CAPABILITY[agent].lower()}-check.json"],
        "source_refs": ["sources/official-source.json"],
        "assumptions": [],
        "risks": ["Resultado de campanha não é garantido."],
        "rights_provenance_refs": ["rights/brand-owned.json"],
        "external_action": "NONE",
        "authorization_refs": [],
        "action_receipt_refs": [],
        "status": "COMPLETED",
        "blocked_reason": "",
        "return_to": DEPARTMENT,
        "returned_at": "2026-07-26T18:30:00-03:00",
    }


def manifest() -> dict[str, Any]:
    return {
        "artifact_type": "CAMPAIGN_ASSET_MANIFEST",
        "manifest_id": "manifest-campaign-001",
        "causal": causal(),
        "brief_ref": "brief-marketing-001",
        "deliverable_refs": ["deliverable-narrative-001"],
        "assets": [
            {
                "asset_id": "asset-narrative-001",
                "asset_type": "TEXT",
                "channel": "site",
                "variant": "pt-br-v1",
                "artifact_ref": "artifacts/narrative-v1.md",
                "digest": digest("a"),
                "specification_ref": "https://developers.google.com/search/docs/fundamentals/creating-helpful-content",
                "specification_checked_at": "2026-07-26T18:20:00-03:00",
                "accessibility": {
                    "alt_text": "",
                    "captions_ref": "",
                    "transcript_ref": "",
                    "not_applicable_reason": "Ativo exclusivamente textual.",
                },
                "rights": {
                    "owner": "Organização contratante",
                    "license_ref": "rights/brand-owned.json",
                    "territory": "Brasil",
                    "expires_at": "n/a",
                    "allowed_channels": ["site"],
                },
                "ingredient_refs": ["sources/product-evidence.json"],
                "ai_use": "ASSISTED",
                "content_credentials_ref": "",
                "claim_refs": ["claims/rework-evidence.json"],
                "measurement_tags": ["utm_source=site", "utm_medium=owned"],
            }
        ],
        "candidate_digest": digest("b"),
        "status": "READY",
        "pending_refs": [],
        "assembled_at": "2026-07-26T18:40:00-03:00",
    }


def readiness(
    overrides: dict[str, str] | None = None,
    *,
    gaps: list[str] | None = None,
    pending: list[str] | None = None,
    declared_ready: bool | None = None,
) -> dict[str, Any]:
    states = {dimension: "PASS" for dimension in DIMENSIONS}
    states.update(overrides or {})
    gap_refs = gaps or []
    pending_refs = pending or []
    computed = all(state in {"PASS", "NOT_APPLICABLE"} for state in states.values())
    computed = computed and not gap_refs and not pending_refs
    ready_value = computed if declared_ready is None else declared_ready
    return {
        "artifact_type": "CAMPAIGN_READINESS_RECORD",
        "readiness_id": "readiness-campaign-001",
        "causal": causal(),
        "manifest_ref": "manifest-campaign-001",
        "candidate_digest": digest("b"),
        "dimensions": [
            {
                "dimension": dimension,
                "status": state,
                "reason": (
                    "Evidência verificada no candidato."
                    if state == "PASS"
                    else "Dimensão não aplicável ao ativo exclusivamente textual."
                ),
                "evidence_refs": (
                    [f"evidence/{dimension.lower()}.json"] if state == "PASS" else []
                ),
                "owner": DIMENSION_OWNER[dimension],
            }
            for dimension, state in states.items()
        ],
        "open_gap_refs": gap_refs,
        "blocking_pending_refs": pending_refs,
        "ready": ready_value,
        "generated_at": "2026-07-26T18:45:00-03:00",
    }


def gap() -> dict[str, Any]:
    return {
        "artifact_type": "MARKETING_CAPABILITY_GAP",
        "gap_id": "gap-video-renderer-001",
        "causal": causal(),
        "capability": "VIDEO",
        "expected_agent": "agente-roteiro-producao-video",
        "discovery_evidence": "Runtime não expõe ferramenta de renderização de vídeo.",
        "impact": "O roteiro existe, mas o MP4 não pode ser produzido nem declarado.",
        "status": "OPEN",
        "recovery_owner": "diretor-de-lentes",
        "recovery_condition": "Disponibilizar renderizador autorizado e reemitir a missão.",
        "detected_at": "2026-07-26T18:10:00-03:00",
    }


def director_causal(producer: str, candidate: str) -> dict[str, Any]:
    return {
        "work_item_id": "work-marketing-001",
        "front_id": "front-marketing",
        "handoff_id": "handoff-marketing-001",
        "message_id": "message-marketing-return-001",
        "causation_message_ids": ["message-director-mission-001"],
        "contract_id": "contract-marketing-001",
        "contract_version": 1,
        "contract_digest": digest("0"),
        "candidate_digest": candidate,
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": digest("c"),
        "created_at": "2026-07-26T18:50:00-03:00",
    }


def derive_department_return(record: dict[str, Any]) -> dict[str, Any]:
    statuses = [item["status"] for item in record["dimensions"]]
    passed = sum(status == "PASS" for status in statuses)
    failed = sum(status in {"FAIL", "NOT_PROVEN"} for status in statuses)
    skipped = sum(status == "NOT_APPLICABLE" for status in statuses)
    candidate = record["candidate_digest"]
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-marketing-001",
        "causal": director_causal(DEPARTMENT, candidate),
        "department_mission_ref": "department-mission-marketing-001",
        "returned_by": DEPARTMENT,
        "state": "RETURNED",
        "scope_touched": ["Conteúdo e campanha previstos na missão."],
        "artifact_refs": ["artifacts/manifest-campaign-001.json"],
        "evidence_refs": ["evidence/readiness-campaign-001.json"],
        "candidate_digest": candidate,
        "test_summary": {
            "pass": passed,
            "fail": failed,
            "skip": skipped,
            "skip_reasons": (
                ["Dimensão declarada não aplicável com razão verificável."]
                if skipped
                else []
            ),
            "critical_fail": failed > 0,
        },
        "pending_refs": record["blocking_pending_refs"] + record["open_gap_refs"],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": "2026-07-26T18:50:00-03:00",
    }


def validate_readiness_semantics(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    dimensions = [item["dimension"] for item in record["dimensions"]]
    if len(dimensions) != len(set(dimensions)):
        errors.append("readiness: dimensão duplicada")
    if set(dimensions) != set(DIMENSIONS):
        errors.append("readiness: cobertura das oito dimensões incompleta")
    computed = all(
        item["status"] in {"PASS", "NOT_APPLICABLE"}
        for item in record["dimensions"]
    )
    computed = (
        computed
        and not record["open_gap_refs"]
        and not record["blocking_pending_refs"]
    )
    if record["ready"] != computed:
        errors.append("readiness: booleano declarado diverge do recálculo")
    return errors


def activation_allowed(mode: str, auth_refs: list[str], receipts: list[str]) -> bool:
    return mode == "AUTHORIZED_ACTIVATION" and bool(auth_refs) and bool(receipts)


def validate_structure() -> list[str]:
    required_local = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "evals" / "PLACAR.md",
        PACKAGE_ROOT / "references" / "protocolo-conteudo-marketing.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT / "references" / "fundamentos-pesquisa-2026-07-26.md",
        PACKAGE_ROOT / "references" / "adr-007-departamento-e-time-elastico.md",
        PACKAGE_ROOT / "scripts" / "lint-email.py",
        PACKAGE_ROOT / "templates" / "template-base.html",
    ]
    errors = validate_required_files(required_local, "arquivo local")
    errors.extend(
        validate_required_files(
            [
                DIRECTOR_SCHEMA_PATH,
                RULES_PATH,
                DIRECTOR_ROOT / "SKILL.md",
                DIRECTOR_ROOT / "departamento-juizes" / "SKILL.md",
                STRUCTURE_ROOT / "ORGANOGRAMA.md",
                STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
                STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
            ],
            "vínculo externo",
        )
    )
    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        errors.append("Departamento fora de departamentos-operacionais/")
    errors.extend(validate_agents_folder(AGENTS_ROOT, AGENT_NAMES))
    if len(AGENT_NAMES) < 3:
        errors.append("time executor abaixo do piso de três agentes")
    return errors


def validate_metadata() -> list[str]:
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    errors.extend(
        validate_openai_yaml(
            OPENAI_PATH,
            "Departamento de Conteúdo e Marketing",
            f"${DEPARTMENT}",
        )
    )
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        errors.extend(validate_frontmatter(root / "SKILL.md", name))
        errors.extend(
            validate_openai_yaml(
                root / "agents" / "openai.yaml",
                DISPLAY_NAMES[name],
                f"${name}",
            )
        )
    return errors


def validate_normative_source() -> list[str]:
    errors: list[str] = []
    for path in [SKILL_PATH, CONTRACT_PATH]:
        if RULES_LINK_DEPARTMENT not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.name}: fonte normativa ausente")
    skill = SKILL_PATH.read_text(encoding="utf-8")
    for token in [
        "diretor-de-lentes",
        "departamento-negocios",
        "departamento-juizes",
        "CONTENT_MARKETING_BRIEF",
        "CAMPAIGN_READINESS_RECORD",
        "DEPARTMENT_RETURN",
        "PRODUCTION_ONLY",
        "AUTHORIZED_ACTIVATION",
    ]:
        if token not in skill:
            errors.append(f"SKILL.md sem token contratual: {token}")
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        agent_skill = (root / "SKILL.md").read_text(encoding="utf-8")
        agent_contract = (root / "CONTRATO-DE-COMPROMISSO.md").read_text(
            encoding="utf-8"
        )
        if RULES_LINK_AGENT not in agent_skill:
            errors.append(f"{name}: skill sem fonte normativa")
        if RULES_LINK_AGENT not in agent_contract:
            errors.append(f"{name}: contrato sem fonte normativa")
        if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill:
            errors.append(f"{name}: trava anti-bypass ausente")
        if DEPARTMENT not in agent_skill:
            errors.append(f"{name}: superior ausente")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "contentMarketingBrief",
        "marketingAssignment",
        "marketingDeliverable",
        "campaignAssetManifest",
        "campaignReadinessRecord",
        "marketingCapabilityGap",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    if schema.get("$defs", {}).get("agentId", {}).get("enum") != AGENT_NAMES:
        errors.append("agentId diverge das pastas canônicas")
    if schema.get("$defs", {}).get("readinessDimension", {}).get("enum") != DIMENSIONS:
        errors.append("readinessDimension diverge das oito dimensões")

    refs: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                refs.append(node["$ref"])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(schema)
    for ref in refs:
        try:
            json_pointer(schema, ref)
        except (KeyError, ValueError) as exc:
            errors.append(f"$ref não resolve: {ref}: {exc}")
    return errors


def validate_inherited_authority(director: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    definitions = director.get("$defs", {})
    operational = definitions.get("operationalDepartment", {}).get("enum", [])
    if DEPARTMENT not in operational:
        errors.append("Diretor não reconhece Conteúdo e Marketing")
    if "departamento-registros" not in operational:
        errors.append("Diretor não reconhece a custódia institucional de Registros")
    plan = definitions.get("directorPlan", {})
    matrix = plan.get("properties", {}).get("department_matrix", {})
    if matrix.get("minItems") != 10 or matrix.get("maxItems") != 10:
        errors.append("matriz do Diretor não exige exatamente dez Departamentos")
    department_return = definitions.get("departmentReturn", {})
    if not find_const(department_return, "returned_by", DEPARTMENT):
        errors.append("Diretor não aceita retorno produzido por Conteúdo e Marketing")
    if not find_const(department_return, "returned_to", "diretor-de-lentes"):
        errors.append("retorno departamental não aponta ao Diretor")
    matrix_exchange = definitions.get("matrixExchangeMessage", {})
    for field, value in (
        ("sender", "diretor-de-lentes"),
        ("recipient", "departamento-negocios"),
        ("sender", "departamento-negocios"),
        ("recipient", "diretor-de-lentes"),
    ):
        if not find_const(matrix_exchange, field, value):
            errors.append(f"matriz Diretor/Negócios não prova {field}={value}")
    judgment_request = definitions.get("judgmentRequest", {})
    if not find_const(judgment_request, "producer", "diretor-de-lentes"):
        errors.append("pedido aos Juízes não pertence exclusivamente ao Diretor")
    if not find_const(judgment_request, "return_to", "diretor-de-lentes"):
        errors.append("pedido aos Juízes não retorna exclusivamente ao Diretor")
    judge_report = definitions.get("departmentJudgeReport", {})
    if not find_const(judge_report, "producer", "departamento-juizes"):
        errors.append("parecer independente não pertence aos Juízes")
    boundary_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            PACKAGE_ROOT / "SKILL.md",
            PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md",
            PACKAGE_ROOT / "references" / "protocolo-conteudo-marketing.md",
            PACKAGE_ROOT
            / "agentes"
            / "agente-inteligencia-relatoria-marketing"
            / "SKILL.md",
        )
    ).lower()
    for token in (
        "departamento-negocios",
        "departamento-juizes",
        "departamento-registros",
        "custódia",
        "missão separada",
    ):
        if token not in boundary_text:
            errors.append(f"fronteira externa não declara {token}")
    return errors


def validate_source_integrity() -> list[str]:
    errors: list[str] = []
    for source, files in SOURCE_HASHES.items():
        root = LEGACY_ROOT / source
        actual_files = {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        } if root.is_dir() else set()
        if actual_files != set(files):
            errors.append(
                f"{source}: inventário mudou; esperado {len(files)}, atual {len(actual_files)}"
            )
            continue
        for relative, expected in files.items():
            actual = sha256_file(root / relative)
            if actual != f"sha256:{expected}":
                errors.append(f"{source}/{relative}: hash divergente")
    copied = {
        PACKAGE_ROOT / "scripts" / "lint-email.py":
            SOURCE_HASHES["email-marketing-html"]["scripts/lint-email.py"],
        PACKAGE_ROOT / "templates" / "template-base.html":
            SOURCE_HASHES["email-marketing-html"]["template/template-base.html"],
    }
    for path, expected in copied.items():
        if path.is_file() and sha256_file(path) != f"sha256:{expected}":
            errors.append(f"cópia preservada divergiu: {path.name}")
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if evals.get("skill") != DEPARTMENT:
        errors.append("evals: skill incorreta")
    cases = evals.get("cases", [])
    if len(cases) < 12:
        errors.append("evals: menos de 12 casos")
    if not any(case.get("origem") == "real" for case in cases):
        errors.append("evals: falta caso real")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("evals: id duplicado")
    for case in cases:
        if f"${DEPARTMENT}" in case.get("prompt", ""):
            errors.append(f"evals: {case.get('id')} nomeia a skill")
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case.get('id')} tem menos de 3 assertions")
    return errors


def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))
    cases: list[tuple[str, bool, list[str]]] = []

    cases.extend(
        [
            ("pacote, time elástico e vínculos", True, validate_structure()),
            ("metadata da gerente e dos oito agentes", True, validate_metadata()),
            ("fonte normativa e tokens", True, validate_normative_source()),
            ("links internos resolvem", True, validate_links(PACKAGE_ROOT)),
            ("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)),
            (
                "todo pacote gerente tem validador que roda a trava global",
                True,
                validate_cobertura_de_validadores(STRUCTURE_ROOT),
            ),
            (
                "contratos de gerente na anatomia canônica",
                True,
                validate_contratos_de_gerente(STRUCTURE_ROOT),
            ),
            (
                "anatomia de contrato acusa raiz inexistente",
                False,
                validate_contratos_de_gerente(STRUCTURE_ROOT / "pacote-inexistente-t97"),
            ),
            (
                "a recusa de digest() dispara e ninguém tem cópia privada do motor",
                True,
                validate_trava_de_digest(STRUCTURE_ROOT),
            ),
            (
                "nenhuma asserção é verdadeira por construção sobre valor produzido",
                True,
                validate_sem_check_tautologico(STRUCTURE_ROOT),
            ),
            (
                "nenhum placar de pacote declara total de cadeia como estado corrente",
                True,
                validate_placar_nao_declara_cadeia(STRUCTURE_ROOT),
            ),
            (
                "a contagem publicada aponta para o digest do instrumento vigente",
                True,
                validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT),
            ),
            (
                "as travas do modulo compartilhado nao estao neutralizadas",
                True,
                validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT),
            ),
            (
                "toda pendencia declarada nomeia quem responde por ela",
                True,
                validate_pendencia_tem_dono(STRUCTURE_ROOT),
            ),
            # Par NEGATIVO da trava acima (T71): sem raiz para varrer, ela tem de
            # FALHAR FECHADO. Trava que devolve vazio quando não consegue olhar
            # nada fica verde por ausência, não por conformidade — e o passo 9
            # exige negativos >= positivos, então acrescentar trava sem par
            # desequilibra a suíte.
            (
                "trava do selo falha fechado quando a raiz não existe",
                False,
                validate_contagem_ligada_ao_instrumento(
                    STRUCTURE_ROOT / "raiz-inexistente"
                ),
            ),
            # Par NEGATIVO da trava da T84: planta a forma proibida — trava
            # desligada por `return` precoce, corpo inteiro virando código morto
            # — e exige que ela seja ACUSADA.
            (
                "trava desligada por return precoce é acusada",
                False,
                achar_corpo_neutralizado(
                    "def validate_de_mentira(raiz):\n"
                    "    return []\n"
                    "    if not raiz.is_dir():\n"
                    "        return ['raiz ausente']\n",
                    "fixture",
                ),
            ),
            # Par NEGATIVO da trava do dono (T71): planta a forma proibida —
            # item de pendência sem linha na tabela de donos — e exige que ela
            # seja ACUSADA.
            (
                "pendência sem dono é acusada",
                False,
                achar_pendencia_sem_dono(
                    "# P\n\n## O que ainda não foi provado\n\n"
                    "1. **Um.** texto\n2. **Dois.** texto\n",
                    "fixture",
                ),
            ),
            (
                "a fonte normativa confere com o valor declarado em ORIGEM.md",
                True,
                validate_fonte_normativa_conferida(STRUCTURE_ROOT),
            ),
            ("schema e refs locais", True, validate_schema_shape(schema)),
            (
                "autoridade e rotas externas herdadas do Diretor",
                True,
                validate_inherited_authority(director),
            ),
            ("fontes legadas intactas e cópias exatas", True, validate_source_integrity()),
            ("catálogo de evals", True, validate_evals()),
        ]
    )

    cases.append(("schema aceita CONTENT_MARKETING_BRIEF", True, validate_schema(brief(), schema, schema)))
    assignment_errors: list[str] = []
    for agent in AGENT_NAMES:
        assignment_errors.extend(validate_schema(assignment(agent), schema, schema))
    cases.append(("schema aceita as oito atribuições exclusivas", True, assignment_errors))
    cases.append(("schema aceita MARKETING_DELIVERABLE", True, validate_schema(deliverable(), schema, schema)))
    cases.append(("schema aceita CAMPAIGN_ASSET_MANIFEST", True, validate_schema(manifest(), schema, schema)))
    ready = readiness()
    cases.append(
        (
            "schema e recálculo aceitam CAMPAIGN_READINESS_RECORD",
            True,
            validate_schema(ready, schema, schema) + validate_readiness_semantics(ready),
        )
    )
    cases.append(("schema aceita MARKETING_CAPABILITY_GAP", True, validate_schema(gap(), schema, schema)))
    derived = derive_department_return(ready)
    cases.append(("Diretor aceita DEPARTMENT_RETURN produzido", True, validate_schema(derived, director, director)))

    invalid = brief("AUTHORIZED_ACTIVATION")
    invalid["authorization_refs"] = []
    cases.append(("brief de ativação exige autorização", False, validate_schema(invalid, schema, schema)))

    invalid = assignment()
    invalid["capability"] = "VIDEO"
    cases.append(("assignment rejeita capacidade trocada", False, validate_schema(invalid, schema, schema)))

    invalid = assignment(mode="AUTHORIZED_ACTIVATION")
    invalid["authorization_refs"] = []
    cases.append(("assignment de ativação exige autorização", False, validate_schema(invalid, schema, schema)))

    invalid = assignment()
    invalid["return_to"] = "diretor-de-lentes"
    cases.append(("assignment rejeita retorno fora da gerente", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable()
    invalid["causal"]["producer"] = "agente-publicidade-conversao"
    cases.append(("deliverable rejeita produtor forjado", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable()
    invalid["artifact_refs"] = []
    cases.append(("deliverable COMPLETED exige artefato", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable()
    invalid["evidence_refs"] = []
    cases.append(("deliverable COMPLETED exige evidência", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable()
    invalid["status"] = "BLOCKED"
    invalid["artifact_refs"] = []
    invalid["evidence_refs"] = []
    cases.append(("deliverable BLOCKED exige motivo", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable("agente-publicidade-conversao")
    invalid["external_action"] = "EXECUTED"
    cases.append(("ação executada exige autorização", False, validate_schema(invalid, schema, schema)))

    invalid = deliverable("agente-publicidade-conversao")
    invalid["external_action"] = "EXECUTED"
    invalid["authorization_refs"] = ["auth/media-001.json"]
    cases.append(("ação executada exige recibo", False, validate_schema(invalid, schema, schema)))

    invalid = manifest()
    invalid["pending_refs"] = ["pending/license.json"]
    cases.append(("manifesto READY rejeita pendência", False, validate_schema(invalid, schema, schema)))

    invalid = readiness()
    invalid["dimensions"].pop()
    cases.append(("readiness exige oito dimensões", False, validate_schema(invalid, schema, schema)))

    invalid = readiness()
    invalid["dimensions"][-1]["dimension"] = "BUSINESS_ALIGNMENT"
    invalid["dimensions"][-1]["reason"] = "Duplicata deliberada."
    errors = validate_schema(invalid, schema, schema) + validate_readiness_semantics(invalid)
    cases.append(("readiness rejeita dimensão duplicada", False, errors))

    invalid = readiness({"CLAIMS_EVIDENCE": "FAIL"}, declared_ready=True)
    errors = validate_schema(invalid, schema, schema) + validate_readiness_semantics(invalid)
    cases.append(("ready não mascara gate FAIL", False, errors))

    invalid = readiness({"RIGHTS_PROVENANCE": "NOT_PROVEN"}, declared_ready=True)
    errors = validate_schema(invalid, schema, schema) + validate_readiness_semantics(invalid)
    cases.append(("ready não mascara direito não provado", False, errors))

    invalid = readiness(gaps=["gaps/video-renderer.json"], declared_ready=True)
    cases.append(("ready rejeita lacuna aberta", False, validate_schema(invalid, schema, schema)))

    invalid = readiness()
    invalid["dimensions"][0]["evidence_refs"] = []
    cases.append(("PASS exige evidência", False, validate_schema(invalid, schema, schema)))

    invalid = gap()
    invalid["status"] = "CLOSED"
    cases.append(("gerente não fecha própria lacuna", False, validate_schema(invalid, schema, schema)))

    invalid = gap()
    invalid["discovery_evidence"] = ""
    cases.append(("lacuna exige causa observada", False, validate_schema(invalid, schema, schema)))

    invalid = copy.deepcopy(derived)
    invalid["state"] = "ACCEPTED"
    cases.append(("retorno departamental não se autoaceita", False, validate_schema(invalid, director, director)))

    invalid = copy.deepcopy(derived)
    invalid["causal"]["producer"] = "departamento-desenvolvimento"
    cases.append(("Diretor rejeita produtor causal forjado", False, validate_schema(invalid, director, director)))

    invalid = copy.deepcopy(derived)
    invalid["returned_to"] = "ceo-maestro"
    cases.append(("retorno não pula o Diretor", False, validate_schema(invalid, director, director)))

    behavior_errors: list[str] = []
    if not activation_allowed(
        "AUTHORIZED_ACTIVATION", ["auth/media.json"], ["receipts/media.json"]
    ):
        behavior_errors.append("ativação autorizada deveria ser permitida")
    if activation_allowed("PRODUCTION_ONLY", ["auth/media.json"], ["receipts/media.json"]):
        behavior_errors.append("produção não deveria executar ação externa")
    if activation_allowed("AUTHORIZED_ACTIVATION", [], ["receipts/media.json"]):
        behavior_errors.append("ativação sem AUTH foi permitida")
    if activation_allowed("AUTHORIZED_ACTIVATION", ["auth/media.json"], []):
        behavior_errors.append("ativação sem recibo foi considerada concluída")
    if derive_department_return(readiness())["test_summary"] != {
        "pass": 8,
        "fail": 0,
        "skip": 0,
        "skip_reasons": [],
        "critical_fail": False,
    }:
        behavior_errors.append("test_summary não foi recalculado dos gates")
    if derive_department_return(
        readiness({"ACCESSIBILITY": "NOT_APPLICABLE"})
    )["test_summary"]["skip"] != 1:
        behavior_errors.append("NOT_APPLICABLE não virou SKIP")
    if set(AGENT_CAPABILITY.values()) != {
        "STRATEGY", "NARRATIVE", "VISUAL", "VIDEO",
        "ADVERTISING", "EMAIL", "INTELLIGENCE", "COMPLIANCE",
    }:
        behavior_errors.append("cobertura de capacidades diverge do ADR-007")
    cases.append(("regras de ativação, gates e time são recalculadas", True, behavior_errors))

    positives = sum(expected for _, expected, _ in cases)
    negatives = len(cases) - positives
    if negatives < positives:
        cases.append(
            (
                "proporção de casos negativos ≥ positivos",
                True,
                [f"há {negatives} negativos e {positives} positivos"],
            )
        )

    failures = 0
    for name, expected_valid, errors in cases:
        actual_valid = not errors
        passed = actual_valid == expected_valid
        print(f"[{'PASS' if passed else 'FAIL'}] {name} — esperado "
              f"{'válido' if expected_valid else 'rejeitado'}")
        if not passed:
            failures += 1
            for error in errors or ["caso inválido foi aceito sem erro"]:
                print(f"       {error}")

    print(f"\nResultado: {len(cases) - failures}/{len(cases)} casos passaram.")
    print(f"Distribuição: {positives} positivos, {negatives} negativos.")
    return 1 if failures else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
