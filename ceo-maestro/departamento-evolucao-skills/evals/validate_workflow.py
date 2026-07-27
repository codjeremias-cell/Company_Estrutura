"""Validador determinístico do Departamento de Evolução de Skills.

Verifica o pacote (arquivos, metadata, links), o schema interno, os artefatos
internos e — como regressão de fronteira — que o contrato do `ceo-maestro`
admite este Departamento como par executivo.

Uso: python evals/validate_workflow.py
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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-evolucao-skills.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"

CEO_ROOT = PACKAGE_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
CEO_SCHEMA_PATH = CEO_ROOT / "schemas" / "ceo-maestro.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

DEPARTMENT = "departamento-evolucao-skills"
AGENT_NAMES = [
    "agente-colheita-e-diagnostico",
    "agente-mineracao-externa",
    "agente-curador-de-candidatos",
    "agente-prova-de-evolucao",
]
AGENT_KIND = {
    "agente-colheita-e-diagnostico": "DIAGNOSTICO",
    "agente-mineracao-externa": "GEM",
    "agente-curador-de-candidatos": "CANDIDATO",
    "agente-prova-de-evolucao": "PROVA",
}
RULES_LINK_DEPARTMENT = "../../regras-de-ouro/REGRAS-DE-OURO.md"
RULES_LINK_AGENT = "../../../../regras-de-ouro/REGRAS-DE-OURO.md"

# ADR-004: aqui não se promove, não se pontua e não se escolhe vencedor.
FORBIDDEN_KEYS = {
    "score",
    "nota",
    "minimum_score",
    "absolute_score",
    "verdict",
    "winner",
    "promoted",
    "promotion",
    "selo",
}

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names,
        digest,
        find_const,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
        validate_agents_folder,
        validate_frontmatter,
        validate_links,
        validate_openai_yaml,
        validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{STRUCTURE_ROOT}/_compartilhado: {exc}"
    )
    raise SystemExit(1)


# --------------------------------------------------------------------------
# Regras comportamentais, recalculadas em código
# --------------------------------------------------------------------------

def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """`a` domina `b`: nunca pior em nenhum caso comparável, melhor em pelo menos um.

    Caso em que qualquer um dos dois deu `skip` não é comparável e fica fora.
    """
    comparable = [
        case
        for case in set(a) & set(b)
        if not str(a[case]).startswith("skip") and not str(b[case]).startswith("skip")
    ]
    if not comparable:
        return False
    value = {"passou": 1, "falhou": 0}
    if any(value[a[case]] < value[b[case]] for case in comparable):
        return False
    return any(value[a[case]] > value[b[case]] for case in comparable)


def frontier(candidates: dict[str, dict[str, Any]]) -> list[str]:
    """Não dominados. Empate mantém os dois — não há desempate aqui."""
    return sorted(
        name
        for name in candidates
        if not any(
            dominates(candidates[other], candidates[name])
            for other in candidates
            if other != name
        )
    )


def mean(results: dict[str, Any]) -> float:
    value = {"passou": 1.0, "falhou": 0.0}
    scored = [value[v] for v in results.values() if not str(v).startswith("skip")]
    return sum(scored) / len(scored) if scored else 0.0


def accepts_candidate(delta_lines: int, removed_text: str) -> bool:
    """Anti-sedimento: candidato que cresce sem remover nada é rejeitado."""
    return delta_lines <= 0 or len(removed_text) >= 20


def prover_is_independent(writer: str, prover: str) -> bool:
    return writer != prover


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

CONTRACT = digest("0")
PRODUCER = digest("1")


def causal(producer: str = DEPARTMENT) -> dict[str, Any]:
    return {
        "work_item_id": "work-002",
        "front_id": "front-evolucao",
        "handoff_id": "handoff-002",
        "message_id": "message-evolucao-001",
        "causation_message_ids": ["message-ceo-002"],
        "contract_id": "contract-002",
        "contract_version": 1,
        "contract_digest": CONTRACT,
        "candidate_digest": "n/a",
        "round": 1,
        "attempt": 1,
        "producer": producer,
        "producer_version": "1.0.0",
        "producer_digest": PRODUCER,
        "created_at": "2026-07-26T22:00:00-03:00",
    }


GAP_TEXT = (
    "A skill não dispara sem ser nomeada quando o pedido usa a palavra do usuário."
)
EXCERPT = (
    "trecho do transcript: o agente respondeu direto, sem invocar a skill, e resumiu"
    " o passo de verificação"
)


def front(material: str = "mineracao") -> dict[str, Any]:
    return {
        "front_ref": "front-acionamento",
        "gap": GAP_TEXT,
        "evidence_excerpt": EXCERPT,
        "targets": ["skills/java-jdbc-dao/SKILL.md", "skills/java-service-usecase/SKILL.md"],
        "reach": 2,
        "denominator": 4,
        "material": material,
    }


def evolution_plan(mode: str = "EVOLUCAO") -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_PLAN",
        "evolution_plan_id": "evolution-plan-001",
        "causal": causal(),
        "executive_mission_ref": "mission-002",
        "mode": mode,
        "fronts": [front()],
        "created_at": "2026-07-26T22:05:00-03:00",
    }


def evolution_task(worker: str = "agente-colheita-e-diagnostico") -> dict[str, Any]:
    kind = AGENT_KIND[worker]
    task: dict[str, Any] = {
        "artifact_type": "EVOLUTION_TASK",
        "task_id": f"task-{worker}",
        "causal": causal(),
        "worker_id": worker,
        "kind": kind,
        "front_ref": "front-acionamento",
        "gap": GAP_TEXT,
        "targets": ["skills/java-jdbc-dao/SKILL.md"],
        "inputs": ["evidencia/transcript-eval-01.md"],
        "forbidden_context": [
            "preferência da gerente ou candidato favorito",
            "retornos dos outros agentes",
            "veredito ou nota desejada",
            "identidade de quem escreveu o candidato",
        ],
        "stop_when": ["A frente tem todos os alvos cobertos ou em SKIP."],
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T22:10:00-03:00",
    }
    if kind == "PROVA":
        task["candidate_labels"] = ["cand-A", "cand-B"]
    return task


def gap_item() -> dict[str, Any]:
    return {
        "gap": GAP_TEXT,
        "evidence_excerpt": EXCERPT,
        "signals": {"acionou": "N", "aderiu": "—", "contorno": "skill não invocada"},
        "targets_affected": ["skills/java-jdbc-dao/SKILL.md"],
        "reach": 2,
        "denominator": 4,
    }


def gem_item(licenca: str = "MIT", degrau: int = 2) -> dict[str, Any]:
    return {
        "gem_id": "gem-001",
        "gap_alvo": GAP_TEXT,
        "fonte_url": "https://arxiv.org/abs/2507.19457",
        "fonte_titulo": "GEPA: Reflective Prompt Evolution",
        "fonte_versao": "v1 / 2026-07",
        "acessado_em": "2026-07-26T21:00:00-03:00",
        "licenca": licenca,
        "o_que_e": "Manter fronteira de Pareto em vez de campeão único, por instância.",
        "limite_declarado": "Números medidos com métrica automática, ausente aqui.",
        "degrau_proposto": degrau,
        "adaptacao": "Aplicar a fronteira sobre casos de eval desta casa.",
    }


def candidate_item(
    candidate_id: str = "cand-descricao",
    delta_lines: int = -4,
    removed: str = "removida a frase genérica de acionamento e o parágrafo duplicado",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "gap_ref": GAP_TEXT,
        "abordagem": "atacar a description, para corrigir acionamento",
        "change_summary": "Description passa a citar as frases reais observadas no transcript.",
        "removed_text": removed,
        "delta_lines": delta_lines,
    }


def scoreboard_line(
    label: str = "cand-A",
    case_id: str = "eval-01",
    baseline: str = "falhou",
    pos: str = "passou",
) -> dict[str, Any]:
    return {
        "candidate_label": label,
        "case_id": case_id,
        "origem": "real",
        "baseline": baseline,
        "pos": pos,
        "acionou": "S" if pos == "passou" else "N",
        "aderiu": "S" if pos == "passou" else "—",
        "excerpt": "trecho do transcript da execução",
    }


def evolution_return(kind: str = "DIAGNOSTICO", status: str = "COMPLETED") -> dict[str, Any]:
    worker = next(name for name, k in AGENT_KIND.items() if k == kind)
    result: dict[str, Any] = {
        "artifact_type": "EVOLUTION_RETURN",
        "task_id": f"task-{worker}",
        "worker_id": worker,
        "kind": kind,
        "gaps": [gap_item()] if kind == "DIAGNOSTICO" else [],
        "gems": [gem_item()] if kind == "GEM" else [],
        "candidates": (
            [candidate_item("cand-descricao"), candidate_item("cand-corpo")]
            if kind == "CANDIDATO"
            else []
        ),
        "scoreboard": (
            [scoreboard_line("cand-A"), scoreboard_line("cand-B", pos="falhou")]
            if kind == "PROVA"
            else []
        ),
        "pending": ["R6 — a existência das tarefas não é verificável pelo runtime."],
        "status": status,
        "return_to": DEPARTMENT,
        "issued_at": "2026-07-26T22:40:00-03:00",
    }
    if kind == "GEM":
        result["saturation"] = "2 rodadas com menos de 2 gems líquidos-novos: saturado."
    if status == "BLOCKED":
        result["gaps"] = []
        result["gems"] = []
        result["candidates"] = []
        result["scoreboard"] = []
        result["blocked_reason"] = "Candidato escrito por este agente: conflito de prova."
    return result


def candidate_set() -> dict[str, Any]:
    return {
        "artifact_type": "CANDIDATE_SET",
        "candidate_set_id": "candidate-set-001",
        "causal": causal(),
        "front_ref": "front-acionamento",
        "items": [
            {
                "candidate_id": "cand-descricao",
                "candidate_label": "cand-A",
                "status": "FRONTEIRA",
                "dominated_by": "n/a",
                "diversidade": False,
            },
            {
                "candidate_id": "cand-corpo",
                "candidate_label": "cand-B",
                "status": "FRONTEIRA",
                "dominated_by": "n/a",
                "diversidade": True,
            },
        ],
        "created_at": "2026-07-26T23:00:00-03:00",
    }


def capability_gap() -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_CAPABILITY_GAP",
        "capability": "Colheita de aprendizagem sem produtor no caminho canônico.",
        "worker_id": "n/a",
        "fronts": ["front-acionamento"],
        "expected_contract": "Relatório de aprendizagem do departamento-registros.",
        "discovery_evidence": "departamento-registros ausente do caminho canônico.",
        "impact": "A frente perde a fonte de lições e abre com TETO_PROVAVEL.",
        "status": "OPEN",
        "owner": "ceo-maestro",
    }


def evolution_ledger(
    mode: str = "EVOLUCAO",
    deliverable: str = "proposal",
    with_assignments: bool = True,
    with_scoreboard: bool = True,
) -> dict[str, Any]:
    return {
        "artifact_type": "EVOLUTION_LEDGER",
        "evolution_ledger_id": "evolution-ledger-001",
        "causal": causal(),
        "executive_mission_ref": "mission-002",
        "mode": mode,
        "deliverable_type": deliverable,
        "plan": evolution_plan(mode),
        "assignments": (
            [
                {
                    "task_id": f"task-{name}",
                    "worker_id": name,
                    "kind": AGENT_KIND[name],
                    "issued_at": "2026-07-26T22:10:00-03:00",
                    "destination": f"evolucao/task-{name}/",
                }
                for name in AGENT_NAMES
            ]
            if with_assignments
            else []
        ),
        "panel": [
            {
                "worker_id": name,
                "kind": AGENT_KIND[name],
                "status": "COMPLETED",
                "substrate": "desconhecido",
                "tier": "desconhecido",
            }
            for name in AGENT_NAMES
        ],
        "scoreboard": (
            [scoreboard_line("cand-A"), scoreboard_line("cand-B", pos="falhou")]
            if with_scoreboard
            else []
        ),
        "candidate_sets": [candidate_set()] if deliverable == "proposal" else [],
        "gems": [gem_item()],
        "metrics": {
            "alcance_total": 2,
            "denominador": 4,
            "material_admitido": 1,
            "casos_novos": 1,
            "vermelho_verde": 1,
        },
        "capability_gaps": [capability_gap()],
        "frentes_encerradas": [],
        "pending": [
            "R6 — a existência das tarefas não é verificável pelo runtime; emissão anexada.",
            "TETO_PROVAVEL não se aplica: a rodada teve material minerado.",
        ],
        "return_to": "ceo-maestro",
        "recorded_at": "2026-07-26T23:10:00-03:00",
    }


# --------------------------------------------------------------------------
# Verificações de pacote
# --------------------------------------------------------------------------

def validate_structure() -> list[str]:
    errors: list[str] = []
    errors.extend(
        validate_required_files(
            [
                SKILL_PATH,
                CONTRACT_PATH,
                OPENAI_PATH,
                SCHEMA_PATH,
                EVALS_PATH,
                PACKAGE_ROOT / "evals" / "PLACAR.md",
                PACKAGE_ROOT / "references" / "protocolo-de-evolucao.md",
                PACKAGE_ROOT / "references" / "metodo-e-fronteira-de-pareto.md",
                PACKAGE_ROOT / "references" / "mineracao-e-proveniencia.md",
                PACKAGE_ROOT / "references" / "origem-e-fundamentacao.md",
                PACKAGE_ROOT / "references" / "adr-004-evolucao-no-nivel-do-ceo.md",
            ],
            "arquivo local",
        )
    )
    errors.extend(
        validate_required_files(
            [
                CEO_SCHEMA_PATH,
                RULES_PATH,
                CEO_ROOT / "SKILL.md",
                STRUCTURE_ROOT / "ORGANOGRAMA.md",
                STRUCTURE_ROOT / "AGENTS.md",
                STRUCTURE_ROOT / "GUIA-DE-EXPANSAO-E-MIGRACAO.md",
                STRUCTURE_ROOT / "_compartilhado" / "validador_schema.py",
            ],
            "vínculo externo",
        )
    )
    if PACKAGE_ROOT.parent.name != "ceo-maestro":
        errors.append(
            "o Departamento deve responder direto ao CEO, sob ceo-maestro/, "
            f"está sob {PACKAGE_ROOT.parent.name}/"
        )
    errors.extend(validate_agents_folder(AGENTS_ROOT, AGENT_NAMES))
    return errors


def validate_metadata() -> list[str]:
    errors = validate_frontmatter(SKILL_PATH, DEPARTMENT)
    errors.extend(
        validate_openai_yaml(
            OPENAI_PATH, "Departamento de Evolução de Skills", f"${DEPARTMENT}"
        )
    )
    displays = {
        "agente-colheita-e-diagnostico": "Colheita e Diagnóstico",
        "agente-mineracao-externa": "Mineração Externa",
        "agente-curador-de-candidatos": "Curador de Candidatos",
        "agente-prova-de-evolucao": "Prova de Evolução",
    }
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        errors.extend(validate_frontmatter(root / "SKILL.md", name))
        errors.extend(
            validate_openai_yaml(root / "agents" / "openai.yaml", displays[name], f"${name}")
        )
    return errors


def validate_normative_source() -> list[str]:
    errors: list[str] = []
    skill = SKILL_PATH.read_text(encoding="utf-8")
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    if RULES_LINK_DEPARTMENT not in skill:
        errors.append("SKILL.md do Departamento sem a fonte normativa única")
    if RULES_LINK_DEPARTMENT not in contract:
        errors.append("contrato do Departamento sem a fonte normativa única")
    for token in [
        "ceo-maestro",
        "departamento-inovacao-melhoria",
        "departamento-registros",
        "departamento-juizes",
        "EVOLUTION_TASK",
        "EXECUTIVE_MISSION",
        "fronteira de Pareto",
        "Jeremias",
    ]:
        if token not in skill:
            errors.append(f"SKILL.md sem contrato obrigatório: {token}")
    for name in AGENT_NAMES:
        root = AGENTS_ROOT / name
        agent_skill = (root / "SKILL.md").read_text(encoding="utf-8")
        agent_contract = (root / "CONTRATO-DE-COMPROMISSO.md").read_text(encoding="utf-8")
        if RULES_LINK_AGENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a fonte normativa única")
        if RULES_LINK_AGENT not in agent_contract:
            errors.append(f"{name}: contrato sem a fonte normativa única")
        if "BLOCKED_BYPASS_ATTEMPT" not in agent_skill:
            errors.append(f"{name}: SKILL.md sem a trava anti-bypass")
        if DEPARTMENT not in agent_skill:
            errors.append(f"{name}: SKILL.md sem o superior declarado")
    return errors


def validate_no_promotion(schema: dict[str, Any]) -> list[str]:
    """ADR-004: aqui não se promove, não se pontua e não se escolhe vencedor."""
    found: set[str] = set()
    collect_property_names(schema, found)
    offenders = sorted(found.intersection(FORBIDDEN_KEYS))
    if offenders:
        return [f"schema contém campo proibido pelo ADR-004: {offenders}"]
    return []


def validate_schema_shape(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "evolutionPlan",
        "evolutionTask",
        "evolutionReturn",
        "candidateSet",
        "evolutionCapabilityGap",
        "evolutionLedger",
    }
    missing = expected.difference(schema.get("$defs", {}))
    if missing:
        errors.append(f"schema sem defs: {sorted(missing)}")
    worker_enum = schema.get("$defs", {}).get("workerId", {}).get("enum", [])
    if sorted(worker_enum) != sorted(AGENT_NAMES):
        errors.append(f"workerId divergente das pastas de agentes/: {worker_enum}")
    return errors


def validate_ceo_contract() -> list[str]:
    """O contrato do CEO precisa admitir este Departamento como par executivo."""
    if not CEO_SCHEMA_PATH.is_file():
        return ["schema do CEO ausente"]
    ceo = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    defs = ceo.get("$defs", {})
    errors: list[str] = []

    if DEPARTMENT not in defs.get("directExecutive", {}).get("enum", []):
        errors.append("directExecutive do CEO não admite este Departamento")
    mission = defs.get("executiveMission", {}).get("properties", {})
    if mission.get("recipients", {}).get("maxItems", 0) < 3:
        errors.append("recipients da EXECUTIVE_MISSION ainda limita a 2 destinatários")
    producer = (
        defs.get("causalHeader", {}).get("properties", {}).get("producer", {}).get("enum", [])
    )
    if DEPARTMENT not in producer:
        errors.append("producer causal do CEO não admite este Departamento")
    gap = (
        defs.get("capabilityGap", {})
        .get("properties", {})
        .get("required_capability", {})
        .get("enum", [])
    )
    if DEPARTMENT not in gap:
        errors.append("CAPABILITY_GAP do CEO não admite este Departamento")

    # o que NÃO pode ter mudado
    if not find_const(defs.get("judgeReport", {}), "producer", "departamento-juizes"):
        errors.append("a nota continua sendo dos Juízes: contrato alterado")
    if not find_const(defs.get("exceptionAuthorization", {}), "authorized_by", "jeremias"):
        errors.append("só Jeremias autoriza exceção: contrato alterado")
    if not find_const(defs.get("executiveDecision", {}), "producer", "ceo-maestro"):
        errors.append("a decisão executiva continua sendo do CEO: contrato alterado")

    agents_md = (STRUCTURE_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if DEPARTMENT not in agents_md:
        errors.append("AGENTS.md não reconhece este Departamento na hierarquia")
    return errors


def validate_evals() -> list[str]:
    errors: list[str] = []
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if evals.get("skill") != DEPARTMENT:
        errors.append("evals: skill incorreta")
    cases = evals.get("cases", [])
    if len(cases) < 12:
        errors.append(f"evals: necessários ao menos 12 casos, há {len(cases)}")
    if not any(case.get("origem") == "real" for case in cases):
        errors.append("evals: falta caso de origem real")
    if len({case["id"] for case in cases}) != len(cases):
        errors.append("evals: id duplicado")
    for case in cases:
        if f"${DEPARTMENT}" in case["prompt"]:
            errors.append(f"evals: {case['id']} nomeia a skill no prompt")
        if len(case.get("assertions", [])) < 3:
            errors.append(f"evals: {case['id']} com menos de 3 assertions")
    return errors


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def run() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))

    cases: list[tuple[str, bool, list[str]]] = []

    cases.append(("pacote, agentes e vínculos externos", True, validate_structure()))
    cases.append(("metadata da gerente e dos quatro agentes", True, validate_metadata()))
    cases.append(("fonte normativa única e tokens de contrato", True, validate_normative_source()))
    cases.append(("links internos do pacote resolvem", True, validate_links(PACKAGE_ROOT)))
    cases.append(("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT)))
    cases.append(("schema interno e workerId", True, validate_schema_shape(schema)))
    cases.append(("ADR-004: sem promoção, nota ou vencedor no schema", True, validate_no_promotion(schema)))
    cases.append(("contrato do CEO admite o par executivo", True, validate_ceo_contract()))
    cases.append(("catálogo de evals", True, validate_evals()))

    fixtures = [
        ("EVOLUTION_PLAN", evolution_plan()),
        ("EVOLUTION_TASK de diagnóstico", evolution_task()),
        ("EVOLUTION_TASK de prova", evolution_task("agente-prova-de-evolucao")),
        ("EVOLUTION_RETURN de diagnóstico", evolution_return("DIAGNOSTICO")),
        ("EVOLUTION_RETURN de gem", evolution_return("GEM")),
        ("EVOLUTION_RETURN de candidato", evolution_return("CANDIDATO")),
        ("EVOLUTION_RETURN de prova", evolution_return("PROVA")),
        ("CANDIDATE_SET", candidate_set()),
        ("EVOLUTION_CAPABILITY_GAP", capability_gap()),
        ("EVOLUTION_LEDGER", evolution_ledger()),
    ]
    for label, fixture in fixtures:
        cases.append((f"schema aceita {label}", True, validate_schema(fixture, schema, schema)))

    # --- tarefa: kind, capacidade e cegueira -------------------------------

    wrong_worker = evolution_task()
    wrong_worker["worker_id"] = "agente-curador-de-candidatos"
    cases.append(
        ("tarefa rejeita capacidade trocada para o kind", False,
         validate_schema(wrong_worker, schema, schema))
    )

    candidate_no_gap = evolution_task("agente-curador-de-candidatos")
    candidate_no_gap["gap"] = "n/a"
    cases.append(
        ("tarefa de candidato exige gap nomeado", False,
         validate_schema(candidate_no_gap, schema, schema))
    )

    prova_sem_rotulo = evolution_task("agente-prova-de-evolucao")
    prova_sem_rotulo.pop("candidate_labels")
    cases.append(
        ("tarefa de prova exige candidatos rotulados", False,
         validate_schema(prova_sem_rotulo, schema, schema))
    )

    prova_um_so = evolution_task("agente-prova-de-evolucao")
    prova_um_so["candidate_labels"] = ["cand-A"]
    cases.append(
        ("tarefa de prova exige dois ou mais rótulos", False,
         validate_schema(prova_um_so, schema, schema))
    )

    leaky = evolution_task()
    leaky["forbidden_context"] = [
        "preferência da gerente",
        "retornos dos outros agentes",
        "veredito desejado",
        "rodada anterior",
    ]
    cases.append(
        ("tarefa exige proibir a identidade de quem escreveu", False,
         validate_schema(leaky, schema, schema))
    )

    wrong_return = evolution_task()
    wrong_return["return_to"] = "ceo-maestro"
    cases.append(
        ("tarefa rejeita retorno fora da gerente", False,
         validate_schema(wrong_return, schema, schema))
    )

    # --- retorno: carga por kind -------------------------------------------

    one_candidate = evolution_return("CANDIDATO")
    one_candidate["candidates"] = [candidate_item("cand-unico")]
    cases.append(
        ("retorno de candidato exige dois ou mais", False,
         validate_schema(one_candidate, schema, schema))
    )

    grew_without_removing = evolution_return("CANDIDATO")
    grew_without_removing["candidates"] = [
        candidate_item("cand-a", delta_lines=12, removed="nada"),
        candidate_item("cand-b"),
    ]
    cases.append(
        ("candidato que cresce sem remover é rejeitado", False,
         validate_schema(grew_without_removing, schema, schema))
    )

    gem_no_saturation = evolution_return("GEM")
    gem_no_saturation.pop("saturation")
    cases.append(
        ("retorno de gem exige saturação declarada", False,
         validate_schema(gem_no_saturation, schema, schema))
    )

    unlicensed_deep = evolution_return("GEM")
    unlicensed_deep["gems"] = [gem_item(licenca="desconhecida", degrau=3)]
    cases.append(
        ("licença desconhecida trava o degrau em 0 ou 1", False,
         validate_schema(unlicensed_deep, schema, schema))
    )

    unlicensed_shallow = evolution_return("GEM")
    unlicensed_shallow["gems"] = [gem_item(licenca="desconhecida", degrau=1)]
    cases.append(
        ("licença desconhecida aceita degrau 1", True,
         validate_schema(unlicensed_shallow, schema, schema))
    )

    prova_com_candidato = evolution_return("PROVA")
    prova_com_candidato["candidates"] = [candidate_item()]
    cases.append(
        ("quem prova não devolve candidato escrito", False,
         validate_schema(prova_com_candidato, schema, schema))
    )

    blocked = evolution_return("PROVA", status="BLOCKED")
    cases.append(
        ("retorno BLOCKED com motivo é válido", True,
         validate_schema(blocked, schema, schema))
    )

    blocked_mute = evolution_return("PROVA", status="BLOCKED")
    blocked_mute.pop("blocked_reason")
    cases.append(
        ("retorno BLOCKED exige motivo declarado", False,
         validate_schema(blocked_mute, schema, schema))
    )

    incoerente = evolution_return("DIAGNOSTICO")
    incoerente["gaps"][0]["signals"]["acionou"] = "N"
    incoerente["gaps"][0]["signals"]["aderiu"] = "S"
    cases.append(
        ("acionou N obriga aderiu em travessão", False,
         validate_schema(incoerente, schema, schema))
    )

    # --- fronteira ----------------------------------------------------------

    dominated_no_dominator = candidate_set()
    dominated_no_dominator["items"][1]["status"] = "DOMINADO"
    cases.append(
        ("dominado exige dominador nomeado", False,
         validate_schema(dominated_no_dominator, schema, schema))
    )

    dominated_ok = candidate_set()
    dominated_ok["items"][1]["status"] = "DOMINADO"
    dominated_ok["items"][1]["dominated_by"] = "cand-descricao"
    dominated_ok["items"][1]["diversidade"] = False
    cases.append(
        ("dominado com dominador é aceito", True,
         validate_schema(dominated_ok, schema, schema))
    )

    single = candidate_set()
    single["items"] = [single["items"][0]]
    cases.append(
        ("fronteira exige comparar ao menos dois", False,
         validate_schema(single, schema, schema))
    )

    # --- ledger -------------------------------------------------------------

    proposal_no_scoreboard = evolution_ledger(with_scoreboard=False)
    cases.append(
        ("proposta sem placar é rejeitada", False,
         validate_schema(proposal_no_scoreboard, schema, schema))
    )

    proposal_no_assignments = evolution_ledger(with_assignments=False)
    cases.append(
        ("proposta sem registro de emissão é rejeitada (R6)", False,
         validate_schema(proposal_no_assignments, schema, schema))
    )

    analysis_with_candidates = evolution_ledger(mode="AVALIACAO", deliverable="proposal")
    cases.append(
        ("modo AVALIACAO não devolve proposta", False,
         validate_schema(analysis_with_candidates, schema, schema))
    )

    analysis_ok = evolution_ledger(mode="AVALIACAO", deliverable="analysis")
    analysis_ok["candidate_sets"] = []
    cases.append(
        ("modo AVALIACAO devolve análise sem candidatos", True,
         validate_schema(analysis_ok, schema, schema))
    )

    no_r6 = evolution_ledger()
    no_r6["pending"] = ["fingerprint residual anotado"]
    cases.append(
        ("ledger exige R6 nomeado em pending", False,
         validate_schema(no_r6, schema, schema))
    )

    to_director = evolution_ledger()
    to_director["return_to"] = "diretor-de-lentes"
    cases.append(
        ("ledger rejeita retorno fora do CEO", False,
         validate_schema(to_director, schema, schema))
    )

    forged = evolution_ledger()
    forged["causal"]["producer"] = "diretor-de-lentes"
    cases.append(
        ("ledger rejeita produtor forjado", False,
         validate_schema(forged, schema, schema))
    )

    # --- fronteira de Pareto, recalculada em código -------------------------

    a = {"c1": "passou", "c2": "passou", "c3": "falhou"}
    b = {"c1": "falhou", "c2": "falhou", "c3": "passou"}
    c = {"c1": "passou", "c2": "passou", "c3": "passou"}
    d = {"c1": "passou", "c2": "falhou", "c3": "falhou"}
    equal = {"c1": "passou", "c2": "passou", "c3": "falhou"}
    skipped = {"c1": "skip:sem ambiente", "c2": "skip:sem ambiente", "c3": "skip:sem ambiente"}

    checks = [
        ("dominância: melhor em tudo domina", dominates(c, a)),
        ("dominância: pior em um caso não domina", not dominates(a, b)),
        ("dominância: empate não domina", not dominates(a, equal)),
        ("dominância: caso em skip não conta", not dominates(a, skipped)),
        ("fronteira mantém os dois complementares", frontier({"a": a, "b": b}) == ["a", "b"]),
        ("fronteira remove o dominado", frontier({"a": a, "c": c, "d": d}) == ["c"]),
        (
            "candidato pior na média e melhor em um caso permanece",
            mean(b) < mean(a) and "b" in frontier({"a": a, "b": b}),
        ),
        ("fronteira de um elemento é detectável", len(frontier({"a": a, "d": d})) == 1),
        ("anti-sedimento: cresce sem remover é rejeitado", not accepts_candidate(12, "nada")),
        ("anti-sedimento: encolher é aceito", accepts_candidate(-4, "n/a")),
        (
            "anti-sedimento: cresce removendo o equivalente é aceito",
            accepts_candidate(3, "removida a seção duplicada de acionamento"),
        ),
        (
            "independência: quem escreve não prova",
            not prover_is_independent("agente-curador-de-candidatos", "agente-curador-de-candidatos")
            and prover_is_independent("agente-curador-de-candidatos", "agente-prova-de-evolucao"),
        ),
        ("digest das regras é verificável",
         RULES_PATH.is_file() and sha256_file(RULES_PATH).startswith("sha256:")),
    ]
    for name, passed in checks:
        cases.append((name, True, [] if passed else ["condição comportamental falhou"]))

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
    sys.exit(run())
