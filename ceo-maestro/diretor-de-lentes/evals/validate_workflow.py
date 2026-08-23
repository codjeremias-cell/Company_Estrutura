from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "diretor-de-lentes.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
SKILL_PATH = PACKAGE_ROOT / "SKILL.md"
CONTRACT_PATH = PACKAGE_ROOT / "CONTRATO-DE-COMPROMISSO.md"
OPENAI_PATH = PACKAGE_ROOT / "agents" / "openai.yaml"
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(PACKAGE_ROOT.parents[1]))
).resolve()
CEO_ROOT = STRUCTURE_ROOT / "ceo-maestro"
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        conferir_digest_das_regras,
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
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
        validate_contagem_ligada_ao_instrumento,
        validate_travas_compartilhadas_com_efeito,
        validate_pendencia_tem_dono,
        validate_sem_check_tautologico,
        validate_trava_de_digest,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{STRUCTURE_ROOT}/_compartilhado: {exc}"
    )
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

OPERATIONAL_DEPARTMENTS = [
    "departamento-arquitetura-software",
    "departamento-arquitetura-dados",
    "departamento-desenvolvimento",
    "departamento-design-ux-ui",
    "departamento-seguranca",
    "departamento-qa-usabilidade",
    "departamento-inovacao-melhoria",
    "departamento-auditoria-responsabilidades",
    "departamento-conteudo-marketing",
    "departamento-registros",
]


def causal(producer: str, candidate: str = "n/a", round_number: int = 1) -> dict[str, Any]:
    return {
        "work_item_id": "work-001",
        "front_id": "front-technical",
        "handoff_id": "handoff-001",
        "message_id": f"message-{producer}-001",
        "causation_message_ids": ["message-ceo-001"],
        "contract_id": "contract-001",
        "contract_version": 1,
        "contract_digest": digest("0"),
        "candidate_digest": candidate,
        "round": round_number,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": digest("1"),
        "created_at": "2026-07-26T16:00:00-03:00",
    }


def department_matrix() -> list[dict[str, Any]]:
    matrix = []
    for index, department in enumerate(OPERATIONAL_DEPARTMENTS):
        active = index in {0, 2, 5, 7}
        matrix.append(
            {
                "department": department,
                "mode": "ATUA" if active else "NAO_SE_APLICA",
                "reason": (
                    "Possui critério e entrega próprios."
                    if active
                    else "O domínio não é afetado por esta missão."
                ),
                "department_mission_ref": (
                    f"department-mission-{index + 1:02d}" if active else "n/a"
                ),
            }
        )
    return matrix


def director_plan() -> dict[str, Any]:
    return {
        "artifact_type": "DIRECTOR_PLAN",
        "director_plan_id": "director-plan-001",
        "causal": causal("diretor-de-lentes"),
        "executive_mission_ref": "mission-001",
        "state": "D_PLANNED",
        "department_matrix": department_matrix(),
        "dependencies": ["Arquitetura antes da implementação."],
        "integration_barriers": ["Contrato técnico aceito antes da construção."],
        "judge_gate_required": True,
        "blocking_pending_refs": [],
        "created_at": "2026-07-26T16:05:00-03:00",
    }


def department_mission(recipient: str = "departamento-desenvolvimento") -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "department-mission-03",
        "causal": causal("diretor-de-lentes"),
        "recipient": recipient,
        "mode": "ATUA",
        "objective": "Entregar a implementação definida pelo contrato técnico.",
        "scope_in": ["Implementação do comportamento autorizado."],
        "scope_out": [],
        "inputs": ["contracts/technical-contract-v1.json"],
        "deliverables": ["artifacts/implementation.zip"],
        "done": ["Testes aplicáveis executados sem falha."],
        "required_evidence": ["evidence/test-report.json"],
        "depends_on": ["department-mission-01"],
        "handoff_to": ["diretor-de-lentes", "departamento-juizes"],
        "decision_authority": ["Microdesign dentro do contrato aceito."],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": [],
            "allowed_resources": [],
            "expires_at": "2026-07-27T16:00:00-03:00",
        },
        "stop_when": ["Escopo ou decisão vinculante divergir."],
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T16:10:00-03:00",
    }


def department_return(
    department: str = "departamento-desenvolvimento",
) -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "department-return-003",
        "causal": causal(department, candidate),
        "department_mission_ref": "department-mission-03",
        "returned_by": department,
        "state": "RETURNED",
        "scope_touched": ["Implementação do comportamento autorizado."],
        "artifact_refs": ["artifacts/implementation.zip"],
        "evidence_refs": ["evidence/test-report.json"],
        "candidate_digest": candidate,
        "test_summary": {
            "pass": 12,
            "fail": 0,
            "skip": 0,
            "skip_reasons": [],
            "critical_fail": False,
        },
        "pending_refs": [],
        "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": "2026-07-26T17:00:00-03:00",
    }


def aggregation_rule(
    method: str = "MENOR", declared_at: str = "2026-07-26T17:00:00-03:00"
) -> dict[str, Any]:
    """ADR-016: a regra de combinação entre instâncias da mesma lente.

    O Diretor a fixa no pedido, antes de qualquer parecer existir. Regra
    escolhida depois de ver as notas não é regra: é seleção de resultado.
    """
    return {
        "method": method,
        "declared_at": declared_at,
        "rationale": "Fixada no pedido, antes de emitir qualquer atribuição aos Juízes.",
    }


def judgment_request(
    required_level: str = "PRODUCAO",
    instances_per_lens: int = 1,
    rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "JUDGMENT_REQUEST",
        "judgment_request_id": "judgment-request-001",
        "causal": causal("diretor-de-lentes", candidate),
        "department_return_ref": "department-return-003",
        "candidate_digest": candidate,
        "contract_digest": digest("0"),
        "required_level": required_level,
        "applicable_criteria": ["Fidelidade, robustez e experiência."],
        "instances_per_lens": instances_per_lens,
        "aggregation_rule": rule or aggregation_rule(),
        "artifact_refs": ["artifacts/implementation.zip"],
        "evidence_refs": ["evidence/test-report.json"],
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T17:05:00-03:00",
    }


def department_judge_report(
    scores: list[int] | None = None,
    verdict: str = "VALIDATED",
    required_level: str = "PRODUCAO",
    *,
    critical_fail: bool = False,
    blocking_pending_refs: list[str] | None = None,
    instances_per_lens: int = 1,
    score_range: tuple[int, int] | None = None,
    rule: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # ADR-014: VALIDATED exige 10 em todos os critérios aplicáveis. A fixture
    # padrão é o caso positivo, então ela sobe para 10 — o antigo [9.5, ...]
    # era o caso positivo sob a rubrica v1.
    values = [10, 10, 10] if scores is None else scores
    candidate = digest("a")
    needs_explanation = verdict != "VALIDATED"
    # ADR-016: com uma instância por lente, lo == hi == minimum_score, e o
    # comportamento anterior é preservado byte a byte.
    if score_range is None:
        score_range = (min(values), min(values))
    return {
        "artifact_type": "DEPARTMENT_JUDGE_REPORT",
        "report_id": "department-judge-report-001",
        "causal": causal("departamento-juizes", candidate),
        "judgment_request_ref": "judgment-request-001",
        "candidate_digest": candidate,
        "contract_digest": digest("0"),
        "round": 1,
        "instances_per_lens": instances_per_lens,
        "aggregation_rule": rule or aggregation_rule(),
        "scorecard": [
            {
                "criterion_id": f"criterion-{index + 1:02d}",
                "score": score,
                "evidence_refs": [f"evidence/criterion-{index + 1:02d}.json"],
            }
            for index, score in enumerate(values)
        ],
        "minimum_score": min(values),
        "minimum_score_range": {"lo": score_range[0], "hi": score_range[1]},
        "verdict": verdict,
        "required_level": required_level,
        "critical_fail": critical_fail,
        "blocking_pending_refs": blocking_pending_refs or [],
        "evidence_refs": ["evidence/judge-report.json"],
        "criticisms": (
            ["A robustez deixou risco ou falha observável."]
            if needs_explanation
            else []
        ),
        "required_changes": (
            ["Fechar o risco ou a falha e executar o reteste indicado."]
            if needs_explanation
            else []
        ),
        "issued_at": "2026-07-26T17:10:00-03:00",
        "expires_at": "2026-07-27T17:10:00-03:00",
    }


def department_gate_record(
    scores: list[int] | None = None,
    verdict: str = "VALIDATED",
    decision: str = "ACCEPTED_FOR_INTEGRATION",
    required_level: str = "PRODUCAO",
    *,
    critical_fail: bool = False,
    blocking_pending_refs: list[str] | None = None,
    instances_per_lens: int = 1,
    score_range: tuple[int, int] | None = None,
) -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "DEPARTMENT_GATE_RECORD",
        "gate_record_id": "department-gate-record-001",
        "causal": causal("diretor-de-lentes", candidate),
        "department_mission": department_mission(),
        "department_return": department_return(),
        "judgment_request": judgment_request(
            required_level, instances_per_lens=instances_per_lens
        ),
        "judge_report": department_judge_report(
            scores,
            verdict,
            required_level,
            critical_fail=critical_fail,
            blocking_pending_refs=blocking_pending_refs,
            instances_per_lens=instances_per_lens,
            score_range=score_range,
        ),
        "decision": decision,
        "recorded_at": "2026-07-26T17:12:00-03:00",
    }


def executive_matrix_contract(
    required_level: str = "PRODUCAO",
) -> dict[str, Any]:
    return {
        "mission_id": "mission-001",
        "causal": causal("ceo-maestro"),
        "required_level": required_level,
        "recipients": ["diretor-de-lentes", "departamento-negocios"],
        "matrix_exchange": {
            "allowed": True,
            "topics": ["Viabilidade técnica e comercial."],
            "read_scope": ["Contrato e evidências compartilhadas."],
            "write_scope": ["Recomendação correlacionada."],
            "consolidation_owner": "diretor-de-lentes",
        },
    }


def matrix_exchange_message(
    sender: str = "diretor-de-lentes",
    required_level: str = "PRODUCAO",
) -> dict[str, Any]:
    recipient = (
        "departamento-negocios"
        if sender == "diretor-de-lentes"
        else "diretor-de-lentes"
    )
    return {
        "artifact_type": "MATRIX_EXCHANGE_MESSAGE",
        "matrix_message_id": "matrix-message-001",
        "causal": causal(sender),
        "executive_mission_ref": "mission-001",
        "required_level": required_level,
        "sender": sender,
        "recipient": recipient,
        "topic": "Viabilidade técnica e comercial.",
        "read_scope": ["Contrato e evidências compartilhadas."],
        "write_scope": ["Recomendação correlacionada."],
        "consolidation_owner": "diretor-de-lentes",
        "decision_requested": "Confirmar a compatibilidade entre valor e viabilidade.",
        "evidence_refs": ["evidence/matrix-analysis.json"],
        "sent_at": "2026-07-26T16:30:00-03:00",
    }


def rework_order() -> dict[str, Any]:
    candidate = digest("a")
    return {
        "artifact_type": "REWORK_ORDER",
        "rework_order_id": "rework-order-001",
        "causal": causal("diretor-de-lentes", candidate, 2),
        "department_mission_ref": "department-mission-03",
        "judge_report_ref": "judge-report-001",
        "target_department": "departamento-desenvolvimento",
        "below_cutoff_criteria": ["robustez: 9.49"],
        "required_changes": ["Cobrir a falha reproduzível indicada pelos Juízes."],
        "retest_criteria": ["Executar o teste de regressão ligado à crítica."],
        "round": 2,
        "max_rounds": 10,
        "return_to": "diretor-de-lentes",
        "issued_at": "2026-07-26T17:15:00-03:00",
    }


def director_gap() -> dict[str, Any]:
    return {
        "artifact_type": "DIRECTOR_CAPABILITY_GAP",
        "director_gap_id": "director-gap-001",
        "causal": causal("diretor-de-lentes"),
        "required_capability": "departamento-arquitetura-dados",
        "expected_path": (
            "diretor-de-lentes/departamentos-operacionais/"
            "departamento-arquitetura-dados/SKILL.md"
        ),
        "reason": "A skill e seu contrato ainda não foram migrados.",
        "impact": "A frente de dados não pode ser delegada.",
        "owner": "diretor-de-lentes",
        "safe_state": "D_BLOCKED",
        "recovery_condition": "Migrar e validar a capacidade no caminho aprovado.",
        "detected_at": "2026-07-26T16:05:00-03:00",
    }


def director_return(artifact_type: str = "PROGRESS") -> dict[str, Any]:
    blocked = artifact_type == "BLOCKED_RETURN"
    return {
        "artifact_type": artifact_type,
        "director_return_id": "director-return-001",
        "causal": causal("diretor-de-lentes"),
        "executive_mission_ref": "mission-001",
        "state": "D_BLOCKED" if blocked else "D_DELEGATED",
        "summary": (
            "Frente de dados bloqueada por capacidade ausente."
            if blocked
            else "Departamentos disponíveis receberam suas missões."
        ),
        "artifact_refs": [],
        "evidence_refs": ["evidence/capability-inventory.json"],
        "director_gap_refs": ["director-gap-001"] if blocked else [],
        "blocking_pending_refs": ["pending/data-capability"] if blocked else [],
        "next_event": "Migrar a capacidade ou receber os retornos contratados.",
        "returned_to": "ceo-maestro",
        "returned_at": "2026-07-26T16:20:00-03:00",
    }


def band_for(score: int) -> str:
    if score == 10:
        return "VALIDATED"
    if score >= 7:
        return "ACEITO_USO_INTERNO"
    return "REPROVED"


def verdict_for_scores(
    scores: list[int], score_range: dict[str, int] | None = None
) -> str:
    # ADR-016: com faixa que atravessa um corte, o veredito é NAO_DISCRIMINADO.
    # Com uma instância (lo == hi) a função devolve exatamente o que devolvia.
    if score_range and band_for(score_range["lo"]) != band_for(score_range["hi"]):
        return "NAO_DISCRIMINADO"
    return band_for(min(scores))


def verdict_reaches_level(verdict: str, required_level: str) -> bool:
    # ADR-016: NAO_DISCRIMINADO não alcança nenhum nível — não é reprovação nem
    # aceite, e não autoriza produção, publicação nem uso interno.
    if required_level == "PRODUCAO":
        return verdict == "VALIDATED"
    if required_level == "INTERNO":
        return verdict in {"VALIDATED", "ACEITO_USO_INTERNO"}
    return False


def route_after_judgment(
    scores: list[int],
    verdict: str,
    *,
    required_level: str = "PRODUCAO",
    critical_fail: bool = False,
    blocking_pending: bool = False,
    rules_compliant: bool = True,
    judges_available: bool = True,
    limitation_complete: bool = False,
    round_number: int = 1,
) -> str:
    if (
        not judges_available
        or not scores
        or required_level not in {"PRODUCAO", "INTERNO"}
        or any(type(score) is not int for score in scores)
        or critical_fail
        or blocking_pending
        or not rules_compliant
    ):
        return "D_BLOCKED"
    expected_verdict = verdict_for_scores(scores)
    if verdict != expected_verdict:
        return "D_BLOCKED"
    if verdict_reaches_level(verdict, required_level):
        return "D_READY_FOR_CEO"
    if limitation_complete:
        return "D_LIMITATION_VERIFIED"
    if round_number >= 10:
        return "D_LIMIT_REACHED_RETURNED"
    return "D_REWORK"


def matrix_allowed(
    recipients: list[str],
    allowed: bool,
    topics: list[str],
    read_scope: list[str],
    write_scope: list[str],
    owner: str | None,
) -> bool:
    both = {"diretor-de-lentes", "departamento-negocios"}.issubset(recipients)
    return (
        both
        and allowed
        and bool(topics)
        and bool(read_scope)
        and bool(write_scope)
        and owner in {"diretor-de-lentes", "departamento-negocios"}
    )


def validate_department_gate_record(
    record: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors = validate_schema(record, schema, schema)
    if errors:
        return errors

    mission_artifact = record["department_mission"]
    return_artifact = record["department_return"]
    request_artifact = record["judgment_request"]
    report_artifact = record["judge_report"]

    if return_artifact["department_mission_ref"] != mission_artifact[
        "department_mission_id"
    ]:
        errors.append("gate: retorno não referencia a missão departamental")
    if return_artifact["returned_by"] != mission_artifact["recipient"]:
        errors.append("gate: Departamento retornado difere do destinatário")
    if return_artifact["causal"]["producer"] != return_artifact["returned_by"]:
        errors.append("gate: produtor causal difere de returned_by")
    if request_artifact["department_return_ref"] != return_artifact[
        "department_return_id"
    ]:
        errors.append("gate: pedido não referencia o retorno")
    if report_artifact["judgment_request_ref"] != request_artifact[
        "judgment_request_id"
    ]:
        errors.append("gate: parecer não referencia o pedido")

    candidate_values = {
        record["causal"]["candidate_digest"],
        return_artifact["candidate_digest"],
        return_artifact["causal"]["candidate_digest"],
        request_artifact["candidate_digest"],
        request_artifact["causal"]["candidate_digest"],
        report_artifact["candidate_digest"],
        report_artifact["causal"]["candidate_digest"],
    }
    if len(candidate_values) != 1:
        errors.append("gate: candidate_digest divergente")

    contract_values = {
        record["causal"]["contract_digest"],
        mission_artifact["causal"]["contract_digest"],
        return_artifact["causal"]["contract_digest"],
        request_artifact["causal"]["contract_digest"],
        request_artifact["contract_digest"],
        report_artifact["causal"]["contract_digest"],
        report_artifact["contract_digest"],
    }
    if len(contract_values) != 1:
        errors.append("gate: contract_digest divergente")

    contract_ids = {
        artifact["causal"]["contract_id"]
        for artifact in [
            record,
            mission_artifact,
            return_artifact,
            request_artifact,
            report_artifact,
        ]
    }
    if len(contract_ids) != 1:
        errors.append("gate: contract_id divergente")

    contract_versions = {
        artifact["causal"]["contract_version"]
        for artifact in [
            record,
            mission_artifact,
            return_artifact,
            request_artifact,
            report_artifact,
        ]
    }
    if len(contract_versions) != 1:
        errors.append("gate: contract_version divergente")

    rounds = {
        record["causal"]["round"],
        mission_artifact["causal"]["round"],
        return_artifact["causal"]["round"],
        request_artifact["causal"]["round"],
        report_artifact["causal"]["round"],
        report_artifact["round"],
    }
    if len(rounds) != 1:
        errors.append("gate: rodada divergente")

    computed_minimum = min(
        item["score"] for item in report_artifact["scorecard"]
    )
    if report_artifact["minimum_score"] != computed_minimum:
        errors.append("gate: minimum_score não corresponde ao scorecard")

    if request_artifact["required_level"] != report_artifact["required_level"]:
        errors.append("gate: required_level divergente entre pedido e parecer")

    # ADR-016: a regra de agregação é FIXADA NO PEDIDO e apenas COPIADA pelos
    # Juízes. Divergência entre pedido e parecer significa regra trocada depois
    # de ver as notas — que é exatamente o que o ADR existe para impedir.
    if request_artifact.get("aggregation_rule") != report_artifact.get(
        "aggregation_rule"
    ):
        errors.append("gate: aggregation_rule divergente entre pedido e parecer")
    if request_artifact.get("instances_per_lens") != report_artifact.get(
        "instances_per_lens"
    ):
        errors.append("gate: instances_per_lens divergente entre pedido e parecer")
    faixa = report_artifact.get("minimum_score_range")
    if not isinstance(faixa, dict):
        errors.append("gate: parecer sem minimum_score_range")
    else:
        if faixa["lo"] > faixa["hi"]:
            errors.append("gate: minimum_score_range invertida")
        if faixa["lo"] != report_artifact["minimum_score"]:
            errors.append(
                "gate: minimum_score não é a ponta baixa da faixa medida"
            )
        if report_artifact.get("instances_per_lens", 1) == 1 and faixa["lo"] != faixa["hi"]:
            errors.append("gate: faixa aberta com uma única instância por lente")

    expected_verdict = (
        "REPROVED"
        if report_artifact["critical_fail"]
        or report_artifact["blocking_pending_refs"]
        else verdict_for_scores(
            [item["score"] for item in report_artifact["scorecard"]],
            faixa if isinstance(faixa, dict) else None,
        )
    )
    if report_artifact["verdict"] != expected_verdict:
        errors.append("gate: veredito não corresponde à faixa e aos bloqueios")

    if record["decision"] == "ACCEPTED_FOR_INTEGRATION":
        if not verdict_reaches_level(
            report_artifact["verdict"],
            request_artifact["required_level"],
        ):
            errors.append("gate: veredito não alcança o required_level")
        if report_artifact["critical_fail"]:
            errors.append("gate: integração aceita com falha crítica")
        if report_artifact["blocking_pending_refs"]:
            errors.append("gate: integração aceita com pendência bloqueante")
    return errors


def validate_matrix_exchange_message(
    message: dict[str, Any],
    mission_contract: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors = validate_schema(message, schema, schema)
    if errors:
        return errors
    matrix = mission_contract["matrix_exchange"]
    recipients = set(mission_contract["recipients"])
    if recipients != {"diretor-de-lentes", "departamento-negocios"}:
        errors.append("matriz: missão não contém os dois interlocutores")
    if not matrix["allowed"]:
        errors.append("matriz: troca não autorizada")
    if message["executive_mission_ref"] != mission_contract["mission_id"]:
        errors.append("matriz: referência da missão divergente")
    if message["required_level"] != mission_contract["required_level"]:
        errors.append("matriz: required_level divergente da missao")
    if message["topic"] not in matrix["topics"]:
        errors.append("matriz: tópico fora do contrato")
    if not set(message["read_scope"]).issubset(matrix["read_scope"]):
        errors.append("matriz: leitura fora do escopo")
    if not set(message["write_scope"]).issubset(matrix["write_scope"]):
        errors.append("matriz: escrita fora do escopo")
    if message["consolidation_owner"] != matrix["consolidation_owner"]:
        errors.append("matriz: dono da consolidação divergente")
    if message["causal"]["producer"] != message["sender"]:
        errors.append("matriz: produtor causal difere do remetente")
    causal_keys = ["contract_id", "contract_version", "contract_digest", "round"]
    for key in causal_keys:
        if message["causal"][key] != mission_contract["causal"][key]:
            errors.append(f"matriz: {key} divergente")
    if (
        message["causal"]["candidate_digest"]
        != mission_contract["causal"]["candidate_digest"]
    ):
        errors.append("matriz: candidate_digest divergente")
    return errors


def validate_ceo_authority_contract() -> list[str]:
    if not CEO_SCHEMA_PATH.is_file():
        return [f"schema do CEO ausente: {CEO_SCHEMA_PATH}"]
    schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    definitions = schema.get("$defs", {})
    checks = [
        (
            "capabilityGap",
            "producer",
            "ceo-maestro",
            "CAPABILITY_GAP deve ser autoria do CEO",
        ),
        (
            "exceptionRequest",
            "producer",
            "ceo-maestro",
            "EXCEPTION_REQUEST deve ser autoria do CEO",
        ),
        (
            "executiveDecision",
            "producer",
            "ceo-maestro",
            "decisão executiva deve ser autoria do CEO",
        ),
        (
            "exceptionAuthorization",
            "authorized_by",
            "jeremias",
            "autorização de exceção deve ser de Jeremias",
        ),
        (
            "judgeReport",
            "producer",
            "departamento-juizes",
            "JUDGE_REPORT deve ser autoria dos Juízes",
        ),
    ]
    errors: list[str] = []
    for definition, property_name, expected, message in checks:
        if definition not in definitions:
            errors.append(f"CEO schema sem $defs/{definition}")
        elif not find_const(
            definitions[definition], property_name, expected
        ):
            errors.append(message)
    executive_mission = definitions.get("executiveMission", {})
    if "required_level" not in executive_mission.get("required", []):
        errors.append("EXECUTIVE_MISSION do CEO não exige required_level")
    level_enum = (
        executive_mission.get("properties", {})
        .get("required_level", {})
        .get("enum", [])
    )
    if set(level_enum) != {"PRODUCAO", "INTERNO"}:
        errors.append("EXECUTIVE_MISSION do CEO não fixa PRODUCAO|INTERNO")
    return errors


# ---------------------------------------------------------------------------
# TAREFA 43 — o gate existe como FORMA e nunca existiu como FATO
# ---------------------------------------------------------------------------
#
# `validate_department_gate_record` (acima) confere a FORMA do envelope contra
# fixtures, e passa. O que ninguém conferia é se ele **existe** para os retornos
# reais. Medido em 2026-08-08, varrendo 2137 envelopes com `artifact_type` na
# árvore: **38 `DEPARTMENT_RETURN` em disco e 0 `DEPARTMENT_GATE_RECORD`**.
#
# O `SKILL.md` deste Diretor, linha 310: *"retorno departamental só integra por
# `DEPARTMENT_GATE_RECORD` completo"*. A única porta obrigatória nunca foi
# aberta, e 38 retornos passaram assim mesmo. Não é defeito de instrumento —
# nenhum conserto de medição alcança isto. É a cadeia não sendo usada.
#
# POR QUE TETO NUMÉRICO E NÃO LISTA DE NOMES. O precedente da casa é a
# `BYPASS_HISTORICO_2026_08_06` da T32, uma lista de nomes sob o comentário
# "só pode ENCOLHER". Medido em 2026-08-08: ela nasceu com 7 e hoje tem 13 —
# cinco entradas entraram sem justificativa escrita e o comentário ainda diz 7.
# Lista de nomes cresce em silêncio porque acrescentar uma linha parece
# inofensivo no diff. Um TETO obriga quem cresce a **mudar um número**, que é
# a menor unidade de mudança que um revisor não deixa passar. (Tarefa 53.)
#
# E o teto é `<=`, não `==`, de propósito: exigir igualdade proibiria a
# melhora, que é o `gate-de-maximalidade-proibe-o-futuro`. Quando a contagem
# cair, a trava DIZ para baixar o teto, em vez de reprovar quem melhorou.
#
# A UNIDADE É O RETORNO DISTINTO, NÃO O ARQUIVO. Medido em 2026-08-08: há **38
# envelopes** `DEPARTMENT_RETURN` em disco, **35** com `department_return_id` e
# apenas **19 ids distintos** — o mesmo retorno viaja copiado entre campanhas.
# Contar arquivos daria 38 e inflaria a dívida por duplicação de cópia, que não
# é dívida de governança. O primeiro número que escrevi aqui foi 38, e era o
# denominador errado pelo mesmo motivo que os 90/19 da própria tarefa 43 não
# reproduziam: contagem de instância não é contagem de coisa.
#
# LIMITE DECLARADO: os **3** envelopes sem `department_return_id` são invisíveis
# para esta trava — sem id não há o que correlacionar. Ficam nomeados aqui em
# vez de escondidos; fechá-los é exigir o campo no schema, que é outra frente.
#
# ---------------------------------------------------------------------------
# 19 → 35, em 2026-08-20, POR DECISÃO EXPLÍCITA DE JEREMIAS.
#
# A trava fez o que devia: recusou-se a deixar a dívida crescer em silêncio e
# obrigou a mudar um número. Este comentário é o preço desse número, e é o que
# o mecanismo pede em troca — subir o teto sem escrever aqui seria burlá-lo.
#
# O QUE CRESCEU, e não é duplicação de cópia: são **16 `department_return_id`
# distintos** emitidos sem `DEPARTMENT_GATE_RECORD` correlacionado, todos de
# campanhas da vertente empresa —
#   DEPTRET-T87-AUDITORIA-R1..R4                    (4)
#   DEPTRETURN-T14-AUDITORIA-R2-20260803            (1)
#   DEPTRETURN-T15-{AUDITORIA-R5,R6,R9}-2026080{2,3}(3)
#   DEPTRETURN-T15-DESENVOLVIMENTO-R6,R7-20260802   (2)
#   DEPTRETURN-T15-QA-R6,R7-20260802                (2)
#   DEPTRETURN-T15-REGISTROS-R7-20260802            (1)
#   DEPTRETURN-T15-SEGURANCA-R6-20260802            (1)
#   DR-T13-AUDIT-R2, DR-T13-AUDIT-R3                (2)
#
# ISTO NÃO É CONSERTO, É RECONHECIMENTO DE DÍVIDA. O defeito que a linha 310 do
# `SKILL.md` descreve continua aberto: *"retorno departamental só integra por
# `DEPARTMENT_GATE_RECORD` completo"*, e trinta e cinco retornos integraram sem
# ele. Fechar de verdade é emitir os gates que faltam — o que **não** se faz
# retroativamente sem forjar registro de rodada que já passou.
#
# A CATRACA CONTINUA VALENDO, e é o que impede este número de virar hábito: 36
# reprova, e 34 reprova pedindo para baixar o teto. O único caminho daqui é
# para baixo.
# --- T94, decisao (b) de Jeremias em 2026-08-21: EXIGIR O GATE NO FLUXO VIVO.
#
# A catraca anterior era por CONTAGEM, e tinha um buraco que so aparece quando se
# procura: se um retorno historico ganhasse gate e um NOVO aparecesse sem, o total
# continuaria 35 e a trava ficaria MUDA. Contagem nao sabe QUAIS. O conjunto sabe.
#
# Esta tupla e a divida HISTORICA, congelada em 2026-08-22 a partir da MEDICAO (nao
# digitada): sao os retornos que ja integraram sem gate, todos de campanhas T12, T13,
# T14, T15, T71 e T87, encerradas. Emitir os gates deles hoje seria escrever que um
# portao foi aberto quando nao foi -- forjar evidencia, que e o que a cadeia inteira
# existe para impedir.
#
# A REGRA QUE PASSA A VALER: retorno que NAO esteja nesta lista e nao tenha gate
# REPROVA na hora, sem teto e sem folga. E se um destes ganhar gate, a lista tem de
# encolher no mesmo ato -- senao a folga volta a crescer calada. O unico caminho e
# para baixo, e agora por NOME.
DIVIDA_HISTORICA_SEM_GATE = (
    "DEPTRET-T12-AUDITORIA-20260803",
    "DEPTRET-T12-AUDITORIA-R3-20260803",
    "DEPTRET-T12-AUDITORIA-R4-20260804",
    "DEPTRET-T12-AUDITORIA-REBASE-20260803",
    "DEPTRET-T12-DESENVOLVIMENTO-REBASE-20260803",
    "DEPTRET-T12-EVOLUCAO-CONSERTO-AUD-T12R-07-E-05-20260803",
    "DEPTRET-T15-AUDITORIA-R7-20260803",
    "DEPTRET-T71-AUDITORIA-R1",
    "DEPTRET-T71-AUDITORIA-R10",
    "DEPTRET-T71-AUDITORIA-R2",
    "DEPTRET-T71-AUDITORIA-R3",
    "DEPTRET-T71-AUDITORIA-R4",
    "DEPTRET-T71-AUDITORIA-R5",
    "DEPTRET-T71-AUDITORIA-R6",
    "DEPTRET-T71-AUDITORIA-R7",
    "DEPTRET-T71-AUDITORIA-R8",
    "DEPTRET-T71-AUDITORIA-R9",
    "DEPTRET-T71-C10-AUDITORIA-R1",
    "DEPTRET-T71-C10-AUDITORIA-R2",
    "DEPTRET-T87-AUDITORIA-R1",
    "DEPTRET-T87-AUDITORIA-R2",
    "DEPTRET-T87-AUDITORIA-R3",
    "DEPTRET-T87-AUDITORIA-R4",
    "DEPTRETURN-T14-AUDITORIA-R2-20260803",
    "DEPTRETURN-T15-AUDITORIA-R5-20260802",
    "DEPTRETURN-T15-AUDITORIA-R6-20260802",
    "DEPTRETURN-T15-AUDITORIA-R9-20260803",
    "DEPTRETURN-T15-DESENVOLVIMENTO-R6-20260802",
    "DEPTRETURN-T15-DESENVOLVIMENTO-R7-20260802",
    "DEPTRETURN-T15-QA-R6-20260802",
    "DEPTRETURN-T15-QA-R7-20260802",
    "DEPTRETURN-T15-REGISTROS-R7-20260802",
    "DEPTRETURN-T15-SEGURANCA-R6-20260802",
    "DR-T13-AUDIT-R2",
    "DR-T13-AUDIT-R3",
)

# Mantido DERIVADO da lista, e nao ao lado dela: numero que se edita sozinho e o que
# deixou a divida crescer de 19 para 35 sem ninguem ver.
TETO_RETORNOS_SEM_GATE = len(DIVIDA_HISTORICA_SEM_GATE)

_PASTAS_FORA = {"candidatos", "lab", "overlay", "instrumentos", "fontes",
                "__pycache__", "backup"}


def _envelopes_em_disco(raiz: Path) -> list[dict[str, Any]]:
    """Todo objeto com `artifact_type` no topo de um .json ou linha de .ndjson."""
    achados: list[dict[str, Any]] = []
    for caminho in list(raiz.rglob("*.json")) + list(raiz.rglob("*.ndjson")):
        if _PASTAS_FORA & set(caminho.parts):
            continue
        try:
            texto = caminho.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        objetos: list[Any] = []
        try:
            objetos.append(json.loads(texto))
        except json.JSONDecodeError:
            for linha in texto.splitlines():
                if linha.strip():
                    try:
                        objetos.append(json.loads(linha))
                    except json.JSONDecodeError:
                        pass
        for obj in objetos:
            if isinstance(obj, dict) and isinstance(obj.get("artifact_type"), str):
                achados.append(obj)
    return achados


def retornos_sem_gate(envelopes: list[dict[str, Any]]) -> list[str]:
    """Os `department_return_id` que nenhum `DEPARTMENT_GATE_RECORD` correlaciona.

    Recebe os envelopes já lidos para poder ser exercitada com fixture — uma
    trava que só sabe ler o disco não tem como provar que fica vermelha.
    """
    retornos = {
        e["department_return_id"]
        for e in envelopes
        if e["artifact_type"] == "DEPARTMENT_RETURN"
        and isinstance(e.get("department_return_id"), str)
    }
    cobertos = set()
    for e in envelopes:
        if e["artifact_type"] != "DEPARTMENT_GATE_RECORD":
            continue
        ref = e.get("department_return")
        if isinstance(ref, dict):
            ref = ref.get("id") or ref.get("ref") or ref.get("artifact_id")
        if isinstance(ref, str):
            cobertos.add(ref)
    return sorted(retornos - cobertos)


def validate_gate_record_cobre_os_retornos(raiz: Path) -> list[str]:
    """Nenhum retorno NOVO integra sem gate, e a dívida antiga só encolhe.

    Compara CONJUNTOS, não contagens. A versão por contagem era cega à troca —
    um histórico ganhando gate e um novo aparecendo sem mantinham o total em 35,
    e a trava não dizia nada. Aqui os dois lados falam:

      * `novos`    — sem gate e fora da dívida congelada: reprova na hora, sem
                     teto, sem folga. É a decisão (b) do Jeremias, e é o único
                     caminho que faz o número cair com o tempo.
      * `quitados` — na dívida congelada e já com gate: reprova pedindo para
                     tirar da lista, senão a folga volta a crescer calada.
    """
    return _comparar_com_divida(set(retornos_sem_gate(_envelopes_em_disco(raiz))))


def _comparar_com_divida(descobertos: set[str]) -> list[str]:
    """A comparacao, separada do disco para poder ser EXERCITADA.

    Ficava embutida na varredura, e por isso so era testavel rodando a arvore
    inteira -- o que significa que os dois ramos so eram exercitados se a arvore
    real contivesse o caso. Como ela nao contem (a divida esta congelada e nada
    novo apareceu), nenhum dos dois tinha prova. Separar torna o autoteste
    possivel, e ele chama a funcao de PRODUCAO, nao uma copia dela.
    """
    historica = set(DIVIDA_HISTORICA_SEM_GATE)
    erros: list[str] = []

    novos = sorted(descobertos - historica)
    if novos:
        erros.append(
            f"RETORNO_NOVO_SEM_GATE: {len(novos)} DEPARTMENT_RETURN fora da dívida "
            f"congelada e sem DEPARTMENT_GATE_RECORD correlacionado — retorno "
            f"departamental só integra por gate completo (SKILL.md:310), e desde "
            f"2026-08-22 isso vale no fluxo vivo. Os novos: {novos[:5]}"
        )

    quitados = sorted(historica - descobertos)
    if quitados:
        erros.append(
            f"DIVIDA_ENCOLHEU: {len(quitados)} retorno(s) da dívida histórica já "
            f"têm gate. Remova-os de DIVIDA_HISTORICA_SEM_GATE no mesmo ato — a "
            f"lista só pode encolher, e lista que não acompanha vira folga que "
            f"cresce calada: {quitados[:5]}"
        )
    return erros


def _autoteste_do_gate() -> list[str]:
    """A trava se exercita com fixture, nos dois sentidos.

    Sem isto ela seria só uma contagem do disco: verde hoje por acaso, e sem
    nada provando que sabe ficar vermelha.
    """
    erros = []
    ret = {"artifact_type": "DEPARTMENT_RETURN", "department_return_id": "DR-X"}
    gate = {"artifact_type": "DEPARTMENT_GATE_RECORD", "department_return": "DR-X"}
    if retornos_sem_gate([ret]) != ["DR-X"]:
        erros.append("autoteste do gate: retorno sem gate não foi detectado")
    if retornos_sem_gate([ret, gate]) != []:
        erros.append("autoteste do gate: retorno COM gate foi acusado — a trava "
                     "reprovaria quem cumpriu")
    aninhado = {"artifact_type": "DEPARTMENT_GATE_RECORD",
                "department_return": {"id": "DR-X"}}
    if retornos_sem_gate([ret, aninhado]) != []:
        erros.append("autoteste do gate: referência aninhada não foi reconhecida")

    # --- T94: os DOIS ramos da comparacao com a divida congelada.
    # Cada amostra isola UM ramo. Sem isso, mutar `novos` ou `quitados` nao muda
    # nada na arvore de hoje -- a divida esta congelada e nada novo apareceu --,
    # e o mutante sobrevive por a arvore nao conter o caso, nao por a trava valer.
    congelada = set(DIVIDA_HISTORICA_SEM_GATE)
    um_historico = next(iter(congelada))

    if _comparar_com_divida(set(congelada)):
        erros.append("autoteste do gate: a divida congelada INTACTA foi acusada — "
                     "a trava reprovaria o estado que ela mesma declara aceito")
    so_novo = _comparar_com_divida(congelada | {"DEPTRET-INVENTADO-R1"})
    if not any("RETORNO_NOVO_SEM_GATE" in e for e in so_novo):
        erros.append("autoteste do gate: retorno NOVO sem gate nao foi acusado — "
                     "e o ramo que a decisao (b) existe para criar")
    so_quitado = _comparar_com_divida(congelada - {um_historico})
    if not any("DIVIDA_ENCOLHEU" in e for e in so_quitado):
        erros.append("autoteste do gate: divida que ENCOLHEU nao foi acusada — sem "
                     "isso a lista deixa de acompanhar e a folga cresce calada")
    return erros


def validate_package() -> list[str]:
    errors: list[str] = []
    required_local = [
        SKILL_PATH,
        CONTRACT_PATH,
        OPENAI_PATH,
        SCHEMA_PATH,
        EVALS_PATH,
        PACKAGE_ROOT / "evals" / "PLACAR.md",
        PACKAGE_ROOT / "evals" / "FORWARD-TEST.md",
        PACKAGE_ROOT / "references" / "workflow-operacional.md",
        PACKAGE_ROOT / "references" / "protocolo-de-handoff.md",
        PACKAGE_ROOT / "references" / "gate-juizes-e-retrabalho.md",
        PACKAGE_ROOT / "references" / "comunicacao-matricial-negocios.md",
        PACKAGE_ROOT / "references" / "bootstrap.md",
        PACKAGE_ROOT / "references" / "origem-migracao.md",
        PACKAGE_ROOT
        / "references"
        / "adr-001-diretoria-e-camada-de-juizes.md",
    ]
    errors.extend(validate_required_files(required_local, "arquivo local"))
    required_external = [
        STRUCTURE_ROOT / "AGENTS.md",
        CEO_ROOT / "SKILL.md",
        CEO_SCHEMA_PATH,
        RULES_PATH,
        STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
    ]
    errors.extend(validate_required_files(required_external, "vínculo externo"))
    errors.extend(validate_frontmatter(SKILL_PATH, "diretor-de-lentes"))
    errors.extend(
        validate_openai_yaml(
            OPENAI_PATH,
            "Diretor de Lentes",
            "$diretor-de-lentes",
            expected_short="Coordena Departamentos e propaga o nível do gate",
        )
    )
    errors.extend(
        validate_links(
            PACKAGE_ROOT,
            exclude=[
                PACKAGE_ROOT / "departamento-juizes",
                PACKAGE_ROOT / "departamentos-operacionais",
                PACKAGE_ROOT / "evals" / "regularizacao-dados7-2026-07-29",
            ],
        )
    )

    skill = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    required_tokens = [
        "ceo-maestro",
        "departamento-negocios",
        "departamento-juizes",
        "DIRECTOR_CAPABILITY_GAP",
        "EXECUTIVE_SUBMISSION",
        "LIMITATION_REPORT",
        "required_level",
        "ACEITO_USO_INTERNO",
        "Jeremias",
        "../../regras-de-ouro/REGRAS-DE-OURO.md",
    ]
    for token in required_tokens:
        if token not in skill:
            errors.append(f"SKILL.md sem contrato obrigatório: {token}")
    if "../../regras-de-ouro/REGRAS-DE-OURO.md" not in contract:
        errors.append("contrato sem fonte normativa única")
    return errors


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected_defs = {
        "directorPlan",
        "departmentMission",
        "departmentReturn",
        "judgmentRequest",
        "departmentJudgeReport",
        "departmentGateRecord",
        "reworkOrder",
        "matrixExchangeMessage",
        "directorCapabilityGap",
        "directorReturn",
    }
    missing = expected_defs.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")

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


def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, vínculos e metadata", True, validate_package()))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("todo pacote gerente tem validador que roda a trava global", True, validate_cobertura_de_validadores(STRUCTURE_ROOT)))
    cases.append(("a recusa de digest() dispara e ninguém tem cópia privada do motor", True, validate_trava_de_digest(STRUCTURE_ROOT)))
    cases.append(("nenhuma asserção é verdadeira por construção sobre valor produzido", True, validate_sem_check_tautologico(STRUCTURE_ROOT)))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    cases.append(("a fonte normativa confere com o valor declarado em ORIGEM.md", True, validate_fonte_normativa_conferida(STRUCTURE_ROOT)))
    # T43: o gate existe como forma e nunca como fato — 38 retornos, 0 gates.
    cases.append(("todo DEPARTMENT_RETURN tem GATE_RECORD, dentro do teto declarado",
                  True, validate_gate_record_cobre_os_retornos(STRUCTURE_ROOT)))
    cases.append(("a trava do gate sabe ficar vermelha (fixture nos dois sentidos)",
                  True, _autoteste_do_gate()))
    # GUIA, passo 7: as 12 secoes do contrato de gerente, em toda a estrutura.
    cases.append(("contratos de gerente na anatomia canônica", True, validate_contratos_de_gerente(STRUCTURE_ROOT)))
    cases.append(("schema e referências locais", True, validate_schema_shape(schema)))
    cases.append(
        (
            "autoridades herdadas do schema do CEO",
            True,
            validate_ceo_authority_contract(),
        )
    )
    eval_errors = []
    if evals.get("skill") != "diretor-de-lentes":
        eval_errors.append("evals: skill incorreta")
    if len(evals.get("cases", [])) < 12:
        eval_errors.append("evals: necessários ao menos 12 casos")
    if not any(case.get("origem") == "real" for case in evals.get("cases", [])):
        eval_errors.append("evals: falta caso real")
    if not all("$diretor-de-lentes" not in case["prompt"] for case in evals["cases"]):
        eval_errors.append("evals: prompts devem testar acionamento sem nomear $skill")
    cases.append(("catálogo de evals", True, eval_errors))

    fixtures = [
        ("DIRECTOR_PLAN", director_plan()),
        ("DEPARTMENT_MISSION", department_mission()),
        ("DEPARTMENT_RETURN", department_return()),
        (
            "DEPARTMENT_RETURN de Conteúdo e Marketing",
            department_return("departamento-conteudo-marketing"),
        ),
        ("JUDGMENT_REQUEST", judgment_request()),
        ("DEPARTMENT_JUDGE_REPORT", department_judge_report()),
        ("DEPARTMENT_GATE_RECORD", department_gate_record()),
        ("REWORK_ORDER", rework_order()),
        ("MATRIX_EXCHANGE_MESSAGE", matrix_exchange_message()),
        ("DIRECTOR_CAPABILITY_GAP", director_gap()),
        ("PROGRESS", director_return("PROGRESS")),
        ("BLOCKED_RETURN", director_return("BLOCKED_RETURN")),
    ]
    for label, fixture in fixtures:
        cases.append(
            (
                f"schema aceita {label}",
                True,
                validate_schema(fixture, schema, schema),
            )
        )

    request_without_level = judgment_request()
    request_without_level.pop("required_level")
    cases.append(
        (
            "JUDGMENT_REQUEST exige required_level",
            False,
            validate_schema(request_without_level, schema, schema),
        )
    )

    report_without_level = department_judge_report()
    report_without_level.pop("required_level")
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT exige required_level",
            False,
            validate_schema(report_without_level, schema, schema),
        )
    )

    fractional_report = department_judge_report(
        [9.5, 10, 10],
        "ACEITO_USO_INTERNO",
        "INTERNO",
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita score fracionário",
            False,
            validate_schema(fractional_report, schema, schema),
        )
    )

    request_unknown_level = judgment_request("DESCONHECIDO")
    cases.append(
        (
            "JUDGMENT_REQUEST rejeita required_level desconhecido",
            False,
            validate_schema(request_unknown_level, schema, schema),
        )
    )

    # --- ADR-016: a regra de agregação nasce no pedido do Diretor -----------

    request_without_rule = judgment_request()
    request_without_rule.pop("aggregation_rule")
    cases.append(
        (
            "JUDGMENT_REQUEST exige aggregation_rule",
            False,
            validate_schema(request_without_rule, schema, schema),
        )
    )

    request_without_instances = judgment_request()
    request_without_instances.pop("instances_per_lens")
    cases.append(
        (
            "JUDGMENT_REQUEST exige instances_per_lens",
            False,
            validate_schema(request_without_instances, schema, schema),
        )
    )

    request_unknown_method = judgment_request()
    request_unknown_method["aggregation_rule"]["method"] = "MEDIA"
    cases.append(
        (
            "JUDGMENT_REQUEST rejeita método de agregação fora do enum",
            False,
            validate_schema(request_unknown_method, schema, schema),
        )
    )

    request_rule_without_time = judgment_request()
    request_rule_without_time["aggregation_rule"].pop("declared_at")
    cases.append(
        (
            "JUDGMENT_REQUEST rejeita regra sem declared_at",
            False,
            validate_schema(request_rule_without_time, schema, schema),
        )
    )

    for method in ("MENOR", "MEDIANA", "EMPATE_DECLARADO"):
        cases.append(
            (
                f"JUDGMENT_REQUEST aceita agregação {method}",
                True,
                validate_schema(
                    judgment_request(rule=aggregation_rule(method=method)),
                    schema,
                    schema,
                ),
            )
        )

    report_without_range = department_judge_report()
    report_without_range.pop("minimum_score_range")
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT exige minimum_score_range",
            False,
            validate_schema(report_without_range, schema, schema),
        )
    )

    report_without_rule = department_judge_report()
    report_without_rule.pop("aggregation_rule")
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT exige aggregation_rule",
            False,
            validate_schema(report_without_rule, schema, schema),
        )
    )

    undiscriminated_report = department_judge_report(
        [6, 10, 10],
        "NAO_DISCRIMINADO",
        "INTERNO",
        instances_per_lens=2,
        score_range=(6, 8),
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT aceita NAO_DISCRIMINADO com faixa que atravessa",
            True,
            validate_schema(undiscriminated_report, schema, schema),
        )
    )

    undiscriminated_stable = copy.deepcopy(undiscriminated_report)
    undiscriminated_stable["minimum_score_range"] = {"lo": 5, "hi": 6}
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita NAO_DISCRIMINADO sem faixa que atravessa",
            False,
            validate_schema(undiscriminated_stable, schema, schema),
        )
    )

    undiscriminated_solo = copy.deepcopy(undiscriminated_report)
    undiscriminated_solo["instances_per_lens"] = 1
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita NAO_DISCRIMINADO com uma instância",
            False,
            validate_schema(undiscriminated_solo, schema, schema),
        )
    )

    accepted_crossing = department_judge_report(
        [7, 10, 10],
        "ACEITO_USO_INTERNO",
        "INTERNO",
        instances_per_lens=2,
        score_range=(6, 7),
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita aceite interno com faixa que atravessa",
            False,
            validate_schema(accepted_crossing, schema, schema),
        )
    )

    cases.append(
        (
            "NAO_DISCRIMINADO não alcança PRODUCAO nem INTERNO",
            True,
            []
            if not verdict_reaches_level("NAO_DISCRIMINADO", "PRODUCAO")
            and not verdict_reaches_level("NAO_DISCRIMINADO", "INTERNO")
            else ["NAO_DISCRIMINADO alcançou um required_level"],
        )
    )

    gate_undiscriminated = department_gate_record(
        [6, 10, 10],
        "NAO_DISCRIMINADO",
        "ACCEPTED_FOR_INTEGRATION",
        "INTERNO",
        instances_per_lens=2,
        score_range=(6, 8),
    )
    cases.append(
        (
            "gate INTERNO não integra NAO_DISCRIMINADO",
            False,
            validate_department_gate_record(gate_undiscriminated, schema),
        )
    )

    gate_rule_swapped = department_gate_record(
        [10, 10, 10],
        "VALIDATED",
        "ACCEPTED_FOR_INTEGRATION",
        "PRODUCAO",
    )
    gate_rule_swapped["judge_report"]["aggregation_rule"] = aggregation_rule(
        method="MEDIANA"
    )
    cases.append(
        (
            "gate rejeita regra de agregação trocada entre pedido e parecer",
            False,
            validate_department_gate_record(gate_rule_swapped, schema),
        )
    )

    gate_range_forged = department_gate_record(
        [10, 10, 10],
        "VALIDATED",
        "ACCEPTED_FOR_INTEGRATION",
        "PRODUCAO",
    )
    gate_range_forged["judge_report"]["minimum_score_range"] = {"lo": 6, "hi": 10}
    cases.append(
        (
            "gate rejeita faixa que não bate com o minimum_score declarado",
            False,
            validate_department_gate_record(gate_range_forged, schema),
        )
    )

    gate_open_range_solo = department_gate_record(
        [10, 10, 10],
        "VALIDATED",
        "ACCEPTED_FOR_INTEGRATION",
        "PRODUCAO",
    )
    gate_open_range_solo["judge_report"]["minimum_score"] = 10
    gate_open_range_solo["judge_report"]["minimum_score_range"] = {"lo": 10, "hi": 9}
    cases.append(
        (
            "gate rejeita faixa invertida",
            False,
            validate_department_gate_record(gate_open_range_solo, schema),
        )
    )

    reproved_nine = department_judge_report(
        [9, 10, 10],
        "REPROVED",
        "INTERNO",
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita REPROVED limpo com mínimo 9",
            False,
            validate_schema(reproved_nine, schema, schema),
        )
    )

    accepted_ten = department_judge_report(
        [10, 10, 10],
        "ACEITO_USO_INTERNO",
        "INTERNO",
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita ACEITO_USO_INTERNO com mínimo 10",
            False,
            validate_schema(accepted_ten, schema, schema),
        )
    )

    validated_nine = department_judge_report(
        [9, 10, 10],
        "VALIDATED",
        "PRODUCAO",
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT rejeita VALIDATED com mínimo 9",
            False,
            validate_schema(validated_nine, schema, schema),
        )
    )

    reproved_six = department_judge_report(
        [6, 10, 10],
        "REPROVED",
        "INTERNO",
    )
    cases.append(
        (
            "DEPARTMENT_JUDGE_REPORT aceita REPROVED com mínimo 6",
            True,
            validate_schema(reproved_six, schema, schema),
        )
    )

    agent_mission = department_mission("agente-seguranca-aplicacao")
    cases.append(
        (
            "schema rejeita bypass para agente",
            False,
            validate_schema(agent_mission, schema, schema),
        )
    )

    incomplete_plan = director_plan()
    incomplete_plan["department_matrix"].pop()
    cases.append(
        (
            "plano exige dez Departamentos",
            False,
            validate_schema(incomplete_plan, schema, schema),
        )
    )

    duplicate_plan = director_plan()
    duplicate_plan["department_matrix"][-1] = copy.deepcopy(
        duplicate_plan["department_matrix"][0]
    )
    duplicate_plan["department_matrix"][-1]["reason"] = (
        "Duplicata com conteúdo diferente para testar a cobertura exata."
    )
    duplicate_errors = validate_schema(duplicate_plan, schema, schema)
    departments = [
        item["department"] for item in duplicate_plan["department_matrix"]
    ]
    if len(departments) != len(set(departments)):
        duplicate_errors.append("matriz contém Departamento duplicado")
    cases.append(("matriz não aceita cobertura duplicada", False, duplicate_errors))

    accepted_return = department_return()
    accepted_return["state"] = "ACCEPTED"
    cases.append(
        (
            "retorno departamental não se autoaceita",
            False,
            validate_schema(accepted_return, schema, schema),
        )
    )

    spoofed_plan = director_plan()
    spoofed_plan["causal"]["producer"] = "departamento-negocios"
    cases.append(
        (
            "plano exige autoria do Diretor",
            False,
            validate_schema(spoofed_plan, schema, schema),
        )
    )

    spoofed_return = department_return()
    spoofed_return["causal"]["producer"] = "departamento-seguranca"
    cases.append(
        (
            "retorno exige produtor igual ao Departamento",
            False,
            validate_schema(spoofed_return, schema, schema),
        )
    )

    cases.append(
        (
            "cadeia retorno-pedido-Juízes íntegra",
            True,
            validate_department_gate_record(
                department_gate_record(), schema
            ),
        )
    )

    internal_nine = department_gate_record(
        [9, 10, 10],
        "ACEITO_USO_INTERNO",
        "ACCEPTED_FOR_INTEGRATION",
        "INTERNO",
    )
    cases.append(
        (
            "gate INTERNO integra ACEITO_USO_INTERNO com mínimo 9",
            True,
            validate_department_gate_record(internal_nine, schema),
        )
    )

    internal_seven = department_gate_record(
        [7, 10, 10],
        "ACEITO_USO_INTERNO",
        "ACCEPTED_FOR_INTEGRATION",
        "INTERNO",
    )
    cases.append(
        (
            "gate INTERNO integra ACEITO_USO_INTERNO com mínimo 7",
            True,
            validate_department_gate_record(internal_seven, schema),
        )
    )

    internal_ten = department_gate_record(
        [10, 10, 10],
        "VALIDATED",
        "ACCEPTED_FOR_INTEGRATION",
        "INTERNO",
    )
    cases.append(
        (
            "gate INTERNO integra VALIDATED com mínimo 10",
            True,
            validate_department_gate_record(internal_ten, schema),
        )
    )

    production_nine = department_gate_record(
        [9, 10, 10],
        "ACEITO_USO_INTERNO",
        "ACCEPTED_FOR_INTEGRATION",
        "PRODUCAO",
    )
    cases.append(
        (
            "gate PRODUCAO rejeita ACEITO_USO_INTERNO",
            False,
            validate_department_gate_record(production_nine, schema),
        )
    )

    internal_six = department_gate_record(
        [6, 10, 10],
        "REPROVED",
        "ACCEPTED_FOR_INTEGRATION",
        "INTERNO",
    )
    cases.append(
        (
            "gate INTERNO rejeita REPROVED com mínimo 6",
            False,
            validate_department_gate_record(internal_six, schema),
        )
    )

    mismatched_level = department_gate_record()
    mismatched_level["judge_report"]["required_level"] = "INTERNO"
    cases.append(
        (
            "gate rejeita required_level divergente",
            False,
            validate_department_gate_record(mismatched_level, schema),
        )
    )

    critical_reproved = department_gate_record(
        [10, 10, 10],
        "REPROVED",
        "BLOCKED",
        "PRODUCAO",
        critical_fail=True,
    )
    cases.append(
        (
            "falha crítica força REPROVED mesmo com 10",
            True,
            validate_department_gate_record(critical_reproved, schema),
        )
    )

    pending_reproved = department_gate_record(
        [10, 10, 10],
        "REPROVED",
        "BLOCKED",
        "INTERNO",
        blocking_pending_refs=["pending/blocking-001"],
    )
    cases.append(
        (
            "pendência bloqueante força REPROVED mesmo com 10",
            True,
            validate_department_gate_record(pending_reproved, schema),
        )
    )

    mismatched_candidate = department_gate_record()
    mismatched_candidate["judge_report"]["candidate_digest"] = digest("b")
    cases.append(
        (
            "gate rejeita candidato divergente",
            False,
            validate_department_gate_record(
                mismatched_candidate, schema
            ),
        )
    )

    mismatched_contract = department_gate_record()
    mismatched_contract["judgment_request"]["contract_digest"] = digest("c")
    cases.append(
        (
            "gate rejeita contrato divergente",
            False,
            validate_department_gate_record(
                mismatched_contract, schema
            ),
        )
    )

    mismatched_version = department_gate_record()
    mismatched_version["department_mission"]["causal"]["contract_version"] = 2
    cases.append(
        (
            "gate rejeita versão de contrato divergente",
            False,
            validate_department_gate_record(
                mismatched_version, schema
            ),
        )
    )

    mismatched_round = department_gate_record()
    mismatched_round["department_mission"]["causal"]["round"] = 2
    cases.append(
        (
            "gate rejeita missão de outra rodada",
            False,
            validate_department_gate_record(
                mismatched_round, schema
            ),
        )
    )

    below_gate = department_gate_record(
        [9.49, 10.0, 10.0],
        "REPROVED",
        "ACCEPTED_FOR_INTEGRATION",
    )
    cases.append(
        (
            "gate departamental não aceita 9,49",
            False,
            validate_department_gate_record(below_gate, schema),
        )
    )

    missing_report = department_gate_record()
    missing_report.pop("judge_report")
    cases.append(
        (
            "gate exige parecer dos Juízes",
            False,
            validate_department_gate_record(missing_report, schema),
        )
    )

    cases.append(
        (
            "troca matricial correlacionada",
            True,
            validate_matrix_exchange_message(
                matrix_exchange_message(),
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    cases.append(
        (
            "troca matricial INTERNO preserva required_level",
            True,
            validate_matrix_exchange_message(
                matrix_exchange_message(required_level="INTERNO"),
                executive_matrix_contract(required_level="INTERNO"),
                schema,
            ),
        )
    )

    matrix_without_level = matrix_exchange_message()
    matrix_without_level.pop("required_level")
    cases.append(
        (
            "troca matricial exige required_level",
            False,
            validate_matrix_exchange_message(
                matrix_without_level,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_unknown_level = matrix_exchange_message(
        required_level="DESCONHECIDO"
    )
    cases.append(
        (
            "troca matricial rejeita required_level desconhecido",
            False,
            validate_matrix_exchange_message(
                matrix_unknown_level,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_divergent_level = matrix_exchange_message(
        required_level="INTERNO"
    )
    cases.append(
        (
            "troca matricial rejeita required_level divergente",
            False,
            validate_matrix_exchange_message(
                matrix_divergent_level,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_outside_topic = matrix_exchange_message()
    matrix_outside_topic["topic"] = "Alterar o orçamento do produto."
    cases.append(
        (
            "troca matricial rejeita tópico externo",
            False,
            validate_matrix_exchange_message(
                matrix_outside_topic,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_spoofed = matrix_exchange_message()
    matrix_spoofed["causal"]["producer"] = "departamento-negocios"
    cases.append(
        (
            "troca matricial rejeita remetente forjado",
            False,
            validate_matrix_exchange_message(
                matrix_spoofed,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    matrix_wrong_candidate = matrix_exchange_message()
    matrix_wrong_candidate["causal"]["candidate_digest"] = digest("d")
    cases.append(
        (
            "troca matricial rejeita candidato divergente",
            False,
            validate_matrix_exchange_message(
                matrix_wrong_candidate,
                executive_matrix_contract(),
                schema,
            ),
        )
    )

    judges_gap = director_gap()
    judges_gap["required_capability"] = "departamento-juizes"
    cases.append(
        (
            "lacuna interna aceita Juízes ausentes",
            True,
            validate_schema(judges_gap, schema, schema),
        )
    )

    wrong_gap = director_gap()
    wrong_gap["required_capability"] = "departamento-negocios"
    cases.append(
        (
            "lacuna dirigida rejeita capacidade lateral",
            False,
            validate_schema(wrong_gap, schema, schema),
        )
    )

    progress_blocked = director_return("PROGRESS")
    progress_blocked["state"] = "D_BLOCKED"
    cases.append(
        (
            "PROGRESS não mascara estado bloqueado",
            False,
            validate_schema(progress_blocked, schema, schema),
        )
    )

    checks = [
        (
            "10 em tudo prepara CEO",
            route_after_judgment([10, 10, 10], "VALIDATED")
            == "D_READY_FOR_CEO",
        ),
        (
            "nota fracionária 9,5 é bloqueada",
            route_after_judgment([9.5, 9.7, 10.0], "VALIDATED")
            == "D_BLOCKED",
        ),
        (
            "nota fracionária 9,49 não arredonda",
            route_after_judgment([9.49, 10, 10], "ACEITO_USO_INTERNO")
            == "D_BLOCKED",
        ),
        (
            "média alta não compensa menor nota",
            route_after_judgment([6, 10, 10], "REPROVED") == "D_REWORK",
        ),
        (
            "INTERNO aceita mínimo 9",
            route_after_judgment(
                [9, 10, 10],
                "ACEITO_USO_INTERNO",
                required_level="INTERNO",
            )
            == "D_READY_FOR_CEO",
        ),
        (
            "PRODUCAO não aceita mínimo 9",
            route_after_judgment(
                [9, 10, 10],
                "ACEITO_USO_INTERNO",
                required_level="PRODUCAO",
            )
            == "D_REWORK",
        ),
        (
            "INTERNO aceita mínimo 7",
            route_after_judgment(
                [7, 10, 10],
                "ACEITO_USO_INTERNO",
                required_level="INTERNO",
            )
            == "D_READY_FOR_CEO",
        ),
        (
            "INTERNO reprova mínimo 6",
            route_after_judgment(
                [6, 10, 10],
                "REPROVED",
                required_level="INTERNO",
            )
            == "D_REWORK",
        ),
        (
            "veredito divergente da faixa bloqueia",
            route_after_judgment(
                [9, 10, 10],
                "REPROVED",
                required_level="INTERNO",
            )
            == "D_BLOCKED",
        ),
        (
            "required_level desconhecido bloqueia",
            route_after_judgment(
                [10, 10, 10],
                "VALIDATED",
                required_level="DESCONHECIDO",
            )
            == "D_BLOCKED",
        ),
        (
            "Auditoria não substitui Juízes ausentes",
            route_after_judgment(
                [10], "VALIDATED", judges_available=False
            )
            == "D_BLOCKED",
        ),
        (
            "falha crítica bloqueia",
            route_after_judgment([10], "VALIDATED", critical_fail=True)
            == "D_BLOCKED",
        ),
        (
            "RI/RO violada bloqueia",
            route_after_judgment([10], "VALIDATED", rules_compliant=False)
            == "D_BLOCKED",
        ),
        (
            "pendência bloqueante impede submissão",
            route_after_judgment(
                [10], "VALIDATED", blocking_pending=True
            )
            == "D_BLOCKED",
        ),
        (
            "limite completo segue ao CEO sem validar",
            route_after_judgment(
                [6, 10], "REPROVED", limitation_complete=True
            )
            == "D_LIMITATION_VERIFIED",
        ),
        (
            "décima rodada retorna limite ao CEO",
            route_after_judgment(
                [6, 10], "REPROVED", round_number=10
            )
            == "D_LIMIT_REACHED_RETURNED",
        ),
        (
            "troca matricial completa é permitida",
            matrix_allowed(
                ["diretor-de-lentes", "departamento-negocios"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                "diretor-de-lentes",
            ),
        ),
        (
            "troca com destinatário único é negada",
            not matrix_allowed(
                ["diretor-de-lentes"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                "diretor-de-lentes",
            ),
        ),
        (
            "troca sem dono único é negada",
            not matrix_allowed(
                ["diretor-de-lentes", "departamento-negocios"],
                True,
                ["Viabilidade."],
                ["Contrato."],
                ["Recomendação."],
                None,
            ),
        ),
    ]
    for name, passed in checks:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

    # --- C04 — a fonte normativa confere contra o valor DECLARADO ------------
    # Fora da lista de booleanos de propósito: quando isto reprova, quem lê
    # precisa do valor declarado, do recomputado e da receita. A lista acima só
    # sabe dizer "condição comportamental falhou", e número sem receita é
    # exatamente o que o C04 proíbe.
    cases.append((
        "digest da fonte normativa confere com o declarado em ORIGEM.md",
        True,
        conferir_digest_das_regras(RULES_PATH),
    ))

    failures = 0
    for name, expected_valid, errors in cases:
        actual_valid = not errors
        passed = actual_valid == expected_valid
        marker = "PASS" if passed else "FAIL"
        expectation = "válido" if expected_valid else "rejeitado"
        print(f"[{marker}] {name} — esperado {expectation}")
        if not passed:
            failures += 1
            if errors:
                for error in errors:
                    print(f"       {error}")
            else:
                print("       caso inválido foi aceito sem erro")

    print(f"\nResultado: {len(cases) - failures}/{len(cases)} casos passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
