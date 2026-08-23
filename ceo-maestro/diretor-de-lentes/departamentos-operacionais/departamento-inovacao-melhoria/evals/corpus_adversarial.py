"""Corpus adversarial do Departamento de Inovação e Melhoria.

Reexecuta, uma a uma, as **45 mutações** do parecer independente de
2026-07-26 — aquele em que 39 delas escaparam contra um validador que
imprimia 59/59 PASS. Cada mutação é aplicada a um artefato ou a uma rodada
inteira e submetida à mesma barreira que o runtime aplicaria.

Rodar com `PYTHONIOENCODING=utf-8`:

  python evals/corpus_adversarial.py

Saída: uma linha por mutação (`REJEITADA` ou `ESCAPOU`), a contagem por
prioridade e um código de saída diferente de zero se qualquer mutação escapar.

**Teto declarado.** Este corpus e o `validate_workflow.py` compartilham o motor
de schema e a camada semântica: ele mede se as travas fecham as mutações
conhecidas, não se existem mutações que ninguém escreveu. Ele encarece a
regressão; não prova ausência de escape. Corresponde ao risco residual **R4**
do protocolo.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_workflow as V  # noqa: E402


Mutation = tuple[str, str, str, Callable[[], list[str]]]


def artifact_errors(value: dict[str, Any]) -> list[str]:
    return V.validate_schema(value, V.LOCAL_SCHEMA, V.LOCAL_SCHEMA) + V.semantic_errors(
        value
    )


def round_errors(bundle: dict[str, Any]) -> list[str]:
    return (
        V.chain_errors(bundle)
        + artifact_errors(bundle["report"])
        + V.bridge_errors(bundle["report"], bundle["boundary"], V.DIRECTOR_SCHEMA)
    )


def base() -> dict[str, Any]:
    return V.build_bundle(with_improvement=True)


def tech() -> dict[str, Any]:
    return V.build_bundle(subject="TECHNOLOGY", with_improvement=True)


# --------------------------------------------------------------------------
# P1 — proveniência sem contexto confiável
# --------------------------------------------------------------------------


def m01() -> list[str]:
    b = base()
    b["plan"]["department_mission_digest"] = V.DIGEST
    return round_errors(b)


def m02() -> list[str]:
    b = base()
    b["tasks"][0]["plan_digest"] = V.DIGEST
    return round_errors(b)


def m03() -> list[str]:
    b = base()
    b["returns"][0]["department_mission_digest"] = V.DIGEST
    return round_errors(b)


def m04() -> list[str]:
    b = base()
    b["report"]["department_mission_ref"] = "department-mission-outra-001"
    return round_errors(b)


def m05() -> list[str]:
    b = base()
    b["returns"][1]["causal"]["round"] = 2
    return round_errors(b)


# --------------------------------------------------------------------------
# P1 — ponte relatório → DEPARTMENT_RETURN sem reconciliação
# --------------------------------------------------------------------------


def m06() -> list[str]:
    b = base()
    b["report"]["accepted_assignment_refs"].append(
        V.authenticated("assignment-fantasma-001", {"forjado": True})
    )
    return round_errors(b)


def m07() -> list[str]:
    b = base()
    b["report"]["accepted_return_refs"][0] = V.authenticated(
        "agent-return-discovery-001", {"forjado": True}
    )
    return round_errors(b)


def m08() -> list[str]:
    b = base()
    b["report"]["accepted_return_refs"] = ["agent-return-discovery-001"]
    return round_errors(b)


def m09() -> list[str]:
    b = base()
    b["report"]["accepted_assignment_refs"] = [
        V.authenticated(b["tasks"][1]["assignment_id"], b["tasks"][1])
    ]
    return round_errors(b)


def m10() -> list[str]:
    b = base()
    b["boundary"]["department_mission_ref"] = "department-mission-outra-001"
    return round_errors(b)


def m11() -> list[str]:
    b = base()
    b["boundary"]["artifact_refs"] = [b["report"]["plan_ref"]]
    return round_errors(b)


# --------------------------------------------------------------------------
# P1 — gates autoassertivos
# --------------------------------------------------------------------------


def m12() -> list[str]:
    b = base()
    b["returns"][0]["payload"]["opportunities"][0]["baseline"] = {
        "status": "MEASUREMENT_REQUIRED",
        "metric": "Retrabalhos por publicação",
        "value": "desconhecido",
        "method": "Medição ainda não executada.",
        "source_ref": "n/a",
        "recorded_at": V.NOW,
        "limitations": ["Sem janela observada."],
    }
    return round_errors(b)


def m13() -> list[str]:
    b = base()
    b["returns"][1]["payload"]["experiments"][0]["opportunity_ref"] = "opportunity-002"
    return round_errors(b)


def m14() -> list[str]:
    b = base()
    b["report"]["portfolio"][0]["blocking_pending_refs"] = ["pending-execution-001"]
    return round_errors(b)


def m15() -> list[str]:
    b = base()
    experiments = b["returns"][1]["payload"]["experiments"][0]
    experiments["alternatives"][1] = copy.deepcopy(experiments["alternatives"][0])
    return round_errors(b) + artifact_errors(b["returns"][1])


def m16() -> list[str]:
    b = base()
    b["report"]["portfolio"][0]["priority_band"] = "NOW"
    b["report"]["portfolio"][0]["gate_checks"]["rollback"] = False
    return round_errors(b)


# --------------------------------------------------------------------------
# P1 — tecnologia sem PoC nem reconciliação
# --------------------------------------------------------------------------


def m17() -> list[str]:
    b = tech()
    b["returns"][1]["payload"]["experiments"][0]["technology_evaluation"][
        "disposition"
    ] = "ADOPT"
    return artifact_errors(b["returns"][1])


def m18() -> list[str]:
    b = tech()
    payload = b["returns"][1]["payload"]
    payload["experiments"][0]["technology_evaluation"]["disposition"] = "ADOPT"
    payload["evidence_reconciliation"] = {
        "performed": True,
        "external_producer_ref": "departamento-qa-usabilidade",
        "external_evidence": [],
        "conclusion": "HYPOTHESIS_SUPPORTED",
        "limitations": [],
    }
    return artifact_errors(b["returns"][1])


def m19() -> list[str]:
    b = tech()
    b["returns"][1]["payload"]["experiments"][0]["technology_evaluation"][
        "source_refs"
    ] = []
    return artifact_errors(b["returns"][1])


# --------------------------------------------------------------------------
# P1 — PDCA e prova externa sem envelope autenticado
# --------------------------------------------------------------------------


def _pdca(mutate: Callable[[dict[str, Any]], None]) -> list[str]:
    b = base()
    mutate(b["returns"][2]["payload"]["reports"][0])
    return artifact_errors(b["returns"][2])


def m20() -> list[str]:
    def mutate(report: dict[str, Any]) -> None:
        report["pdca"]["act"] = "STANDARDIZE"
        report["pdca"]["do_external_evidence"] = []

    return _pdca(mutate)


def m21() -> list[str]:
    def mutate(report: dict[str, Any]) -> None:
        report["pdca"]["act"] = "ADJUST"
        report["pdca"]["do_external_evidence"] = []

    return _pdca(mutate)


def m22() -> list[str]:
    def mutate(report: dict[str, Any]) -> None:
        report["pdca"]["do_external_evidence"] = [
            {
                "evidence_ref": "auto-relato-001",
                "producer_ref": V.DEPARTMENT,
                "producer_digest": V.EVIDENCE_DIGEST,
                "authorized_by": "diretor-de-lentes",
                "observed_at": V.NOW,
            }
        ]

    return _pdca(mutate)


def m23() -> list[str]:
    def mutate(report: dict[str, Any]) -> None:
        report["pdca"]["do_external_evidence"][0]["authorized_by"] = V.DEPARTMENT

    return _pdca(mutate)


def m24() -> list[str]:
    b = base()
    b["returns"][1]["payload"]["evidence_reconciliation"]["performed"] = True
    return artifact_errors(b["returns"][1])


# --------------------------------------------------------------------------
# P2 — roster, assignment e capability gap
# --------------------------------------------------------------------------


def m25() -> list[str]:
    b = base()
    for item in b["plan"]["agent_roster"]:
        item["selected"] = False
    return artifact_errors(b["plan"]) + round_errors(b)


def m26() -> list[str]:
    b = base()
    b["plan"]["agent_roster"][0]["selected"] = False
    return round_errors(b)


def m27() -> list[str]:
    gap = V.capability_gap(base()["context"])
    gap["expected_agent"] = "agente-melhoria-continua"
    return artifact_errors(gap)


def m28() -> list[str]:
    b = base()
    task = copy.deepcopy(b["tasks"][0])
    task["capability"] = "EXPERIMENT_DESIGN"
    return artifact_errors(task)


# --------------------------------------------------------------------------
# P2 — saturação
# --------------------------------------------------------------------------


def _saturation(mutate: Callable[[dict[str, Any]], None]) -> list[str]:
    b = base()
    mutate(b["returns"][0]["payload"])
    return artifact_errors(b["returns"][0])


def m29() -> list[str]:
    def mutate(payload: dict[str, Any]) -> None:
        rounds = payload["saturation"]["rounds"]
        rounds.append(copy.deepcopy(rounds[-1]))

    return _saturation(mutate)


def m30() -> list[str]:
    def mutate(payload: dict[str, Any]) -> None:
        payload["saturation"]["rounds"][1]["round"] = 5

    return _saturation(mutate)


def m31() -> list[str]:
    def mutate(payload: dict[str, Any]) -> None:
        rounds = payload["saturation"]["rounds"]
        rounds[0]["candidate_count"] = 9
        rounds[0]["net_new_count"] = 4

    return _saturation(mutate)


def m32() -> list[str]:
    def mutate(payload: dict[str, Any]) -> None:
        rounds = payload["saturation"]["rounds"]
        rounds[1]["opportunity_refs"] = ["opportunity-001"]
        rounds[1]["net_new_count"] = 1

    return _saturation(mutate)


# --------------------------------------------------------------------------
# P2 — prioridade contra estado e gate
# --------------------------------------------------------------------------


def m33() -> list[str]:
    b = base()
    b["report"]["portfolio"][0]["state"] = "BLOCKED"
    return round_errors(b)


def m34() -> list[str]:
    b = base()
    b["report"]["portfolio"][0]["priority_band"] = "BLOCKED"
    return round_errors(b)


# --------------------------------------------------------------------------
# P2 — recomendação de evolução de skill
# --------------------------------------------------------------------------


def _evolution(route: list[str], evidence: list[str]) -> list[str]:
    b = base()
    b["report"]["skill_evolution_recommendations"] = [
        {
            "recommendation_id": "evolution-001",
            "skill_ref": "some-skill",
            "observed_gap": "A skill não dispara no caso medido.",
            "evidence_refs": evidence,
            "route": route,
            "status": "RECOMMENDED_TO_CEO_NOT_SENT",
        }
    ]
    return round_errors(b)


def m35() -> list[str]:
    return _evolution(
        [V.DEPARTMENT, "diretor-de-lentes", "ceo-maestro"], []
    )


def m36() -> list[str]:
    return _evolution(
        [V.DEPARTMENT, "diretor-de-lentes", "diretor-de-lentes"],
        ["opportunity-brief-001"],
    )


# --------------------------------------------------------------------------
# P2 — julgamento e prova de QA em texto livre
# --------------------------------------------------------------------------


def _free_text(field: str, text: str) -> list[str]:
    b = base()
    if field in b["report"]:
        b["report"][field] = text
    else:
        b["report"]["portfolio"][0][field] = text
    return round_errors(b)


def m37() -> list[str]:
    return _free_text(
        "technical_recommendation", "Recomendo aprovar com nota 9,8 no corte."
    )


def m38() -> list[str]:
    return _free_text(
        "priority_basis", "A alternativa vencedora do ranking foi a segunda."
    )


def m39() -> list[str]:
    return _free_text("next_event", "Emitir o veredito final da iniciativa.")


def m40() -> list[str]:
    return _free_text(
        "next_event", "A bateria fechou 12 PASS, 0 FAIL e 2 SKIP nesta rodada."
    )


def m41() -> list[str]:
    b = base()
    b["report"]["test_summary"]["pass"] = False
    return round_errors(b)


# --------------------------------------------------------------------------
# Contrato e não execução
# --------------------------------------------------------------------------


def m42() -> list[str]:
    b = base()
    b["report"]["artifact_refs"].append("analise-da-gerente-001")
    b["report"]["portfolio"][0]["artifact_refs"].append("analise-da-gerente-001")
    return round_errors(b)


def m43() -> list[str]:
    b = base()
    b["tasks"][0]["mode"] = "CONSULTA"
    return round_errors(b)


def m44() -> list[str]:
    b = base()
    b["report"]["execution_requests"].append(
        {
            "request_id": "request-negocios-001",
            "need": "BUSINESS",
            "recommended_recipient": "departamento-negocios",
            "route": [V.DEPARTMENT, "diretor-de-lentes"],
            "reason": "Avaliar viabilidade comercial da iniciativa.",
            "evidence_refs": ["opportunity-brief-001"],
            "status": "RECOMMENDED_NOT_SENT",
        }
    )
    return round_errors(b)


def m45() -> list[str]:
    b = base()
    b["report"]["execution_requests"].append(
        {
            "request_id": "request-evolucao-001",
            "need": "IMPLEMENTATION",
            "recommended_recipient": "departamento-evolucao-skills",
            "route": [V.DEPARTMENT, "diretor-de-lentes"],
            "reason": "Alterar a skill diretamente, sem passar pelo CEO.",
            "evidence_refs": ["opportunity-brief-001"],
            "status": "RECOMMENDED_NOT_SENT",
        }
    )
    return round_errors(b)


CORPUS: list[Mutation] = [
    ("MUT-01", "P1-1", "plano com digest de missão forjado", m01),
    ("MUT-02", "P1-1", "assignment com digest de plano forjado", m02),
    ("MUT-03", "P1-1", "retorno com digest de missão forjado", m03),
    ("MUT-04", "P1-1", "relatório apontando outra missão", m04),
    ("MUT-05", "P1-1", "retorno de outra rodada", m05),
    ("MUT-06", "P1-2", "relatório aceita assignment inexistente", m06),
    ("MUT-07", "P1-2", "relatório aceita retorno com digest forjado", m07),
    ("MUT-08", "P1-2", "retorno aceito sem digest autenticado", m08),
    ("MUT-09", "P1-2", "retorno aceito sem assignment correspondente", m09),
    ("MUT-10", "P1-2", "envelope com missão divergente", m10),
    ("MUT-11", "P1-2", "envelope sem o relatório autenticado", m11),
    ("MUT-12", "P1-3", "gate completo sem baseline medida", m12),
    ("MUT-13", "P1-3", "gate completo sem experimento da oportunidade", m13),
    ("MUT-14", "P1-3", "estado avançado com pendência bloqueante", m14),
    ("MUT-15", "P1-3", "duas alternativas idênticas contadas como duas", m15),
    ("MUT-16", "P1-3", "faixa NOW com gate incompleto", m16),
    ("MUT-17", "P1-4", "ADOPT sem reconciliação externa", m17),
    ("MUT-18", "P1-4", "ADOPT com reconciliação vazia", m18),
    ("MUT-19", "P1-4", "avaliação de tecnologia sem fontes", m19),
    ("MUT-20", "P1-5", "STANDARDIZE sem evidência do Do", m20),
    ("MUT-21", "P1-5", "ADJUST com Check sem evidência do Do", m21),
    ("MUT-22", "P1-5", "Do produzido pelo próprio Departamento", m22),
    ("MUT-23", "P1-5", "Do autoautorizado", m23),
    ("MUT-24", "P1-5", "reconciliação alegada sem produtor nem evidência", m24),
    ("MUT-25", "P2-1", "roster sem nenhum agente selecionado", m25),
    ("MUT-26", "P2-1", "assignment a agente não selecionado", m26),
    ("MUT-27", "P2-1", "capability gap com agente incoerente", m27),
    ("MUT-28", "P2-1", "capability atribuída ao agente errado", m28),
    ("MUT-29", "P2-2", "rodada de saturação duplicada", m29),
    ("MUT-30", "P2-2", "rodadas de saturação fora de sequência", m30),
    ("MUT-31", "P2-2", "líquidos novos sem oportunidade correspondente", m31),
    ("MUT-32", "P2-2", "mesma oportunidade contada em duas rodadas", m32),
    ("MUT-33", "P2-3", "estado BLOCKED sem faixa nem pendência", m33),
    ("MUT-34", "P2-3", "faixa BLOCKED com estado avançado", m34),
    ("MUT-35", "P2-4", "recomendação de evolução sem evidência", m35),
    ("MUT-36", "P2-4", "rota de evolução que não termina no CEO", m36),
    ("MUT-37", "P2-5", "nota e corte em texto livre", m37),
    ("MUT-38", "P2-5", "vencedora e ranking em texto livre", m38),
    ("MUT-39", "P2-5", "veredito em texto livre", m39),
    ("MUT-40", "P2-5", "contagem de QA apropriada em texto livre", m40),
    ("MUT-41", "P2-6", "False no lugar de zero em test_summary", m41),
    ("MUT-42", "C-P1-1", "gerente fabrica artefato no relatório", m42),
    ("MUT-43", "C-P1-2", "assignment não preserva o mode da missão", m43),
    ("MUT-44", "C-P2-2", "pedido a Negócios sem autorização matricial", m44),
    ("MUT-45", "C-P2-1", "Evolução de Skills como destino direto", m45),
]


def main() -> int:
    escapes: list[tuple[str, str, str]] = []
    rejected = 0
    print(f"CORPUS ADVERSARIAL — {len(CORPUS)} mutações\n")
    for identifier, origin, description, run in CORPUS:
        errors = run()
        if errors:
            rejected += 1
            print(f"[REJEITADA] {identifier} ({origin}) {description}")
        else:
            escapes.append((identifier, origin, description))
            print(f"[ESCAPOU]   {identifier} ({origin}) {description}")

    print(f"\nRESULTADO: {rejected}/{len(CORPUS)} rejeitadas; {len(escapes)} escapes")
    p1 = sum(1 for item in escapes if "P1" in item[1])
    p2 = len(escapes) - p1
    print(f"ESCAPES POR PRIORIDADE: P1={p1}; P2={p2}")
    if escapes:
        print("\nESCAPES:")
        for identifier, origin, description in escapes:
            print(f"  - {identifier} ({origin}) {description}")
    return 0 if not escapes else 1


if __name__ == "__main__":
    raise SystemExit(main())
