"""Validador determinístico do Departamento de Design UX/UI.

Verifica o pacote, o schema interno, os artefatos internos e — como regressão de
fronteira — que o contrato do `diretor-de-lentes` aceita o `DEPARTMENT_RETURN`
convertido a partir do `DESIGN_LEDGER`.

Prova mecanicamente o que o ADR-009 fixou: aqui não se pontua, não se compara em
painel cego, não se escreve código; o gate visual trava a dependência de
implementação; e `REPORTED`/`UNAVAILABLE` nunca sustentam um critério atendido.

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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-design-ux-ui.schema.json"
EVALS_PATH = PACKAGE_ROOT / "evals" / "evals.json"
AGENTS_ROOT = PACKAGE_ROOT / "agentes"
REFERENCES_ROOT = PACKAGE_ROOT / "references"

OPERATIONS_ROOT = PACKAGE_ROOT.parent
DIRECTOR_ROOT = OPERATIONS_ROOT.parent
CEO_ROOT = DIRECTOR_ROOT.parent
STRUCTURE_ROOT = Path(
    os.environ.get("SKILL_STRUCTURE_ROOT", str(CEO_ROOT.parent))
).resolve()
DIRECTOR_SCHEMA_PATH = DIRECTOR_ROOT / "schemas" / "diretor-de-lentes.schema.json"
RULES_PATH = STRUCTURE_ROOT / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        collect_property_names, digest, find_const, sha256_file, validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_adr_series,
        validate_agents_folder, validate_frontmatter, validate_links,
        validate_openai_yaml, validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print("[FAIL] motor compartilhado ausente em "
          f"{STRUCTURE_ROOT}/_compartilhado: {exc}")
    raise SystemExit(1)


DEPARTMENT = "departamento-design-ux-ui"

AGENT_CAPABILITY = {
    "agente-direcao-e-anti-slop": "DIRECAO_ANTI_SLOP",
    "agente-fluxo-estados-e-transicoes": "FLUXO_ESTADOS",
    "agente-linguagem-visual": "LINGUAGEM_VISUAL",
    "agente-design-system-e-tokens": "DESIGN_SYSTEM_TOKENS",
    "agente-nitidez-e-adaptacao": "NITIDEZ_ADAPTACAO",
    "agente-dataviz": "DATAVIZ",
    "agente-acessibilidade-medida": "ACESSIBILIDADE_MEDIDA",
}
CAPABILITY_AGENT = {v: k for k, v in AGENT_CAPABILITY.items()}
CAPABILITY_WAVE = {
    "DIRECAO_ANTI_SLOP": 1, "FLUXO_ESTADOS": 2, "LINGUAGEM_VISUAL": 3,
    "DESIGN_SYSTEM_TOKENS": 3, "NITIDEZ_ADAPTACAO": 3, "DATAVIZ": 3,
    "ACESSIBILIDADE_MEDIDA": 4,
}
DIMENSIONS = ["DIRECAO", "FLUXO_ESTADOS", "ACESSIBILIDADE", "LINGUAGEM_VISUAL",
              "NITIDEZ", "DATAVIZ", "ADAPTACAO_STACK", "POLISH", "EVIDENCIA"]

AGENT_DISPLAY = {
    "agente-direcao-e-anti-slop": "Agente de Direção e Anti-Slop",
    "agente-fluxo-estados-e-transicoes": "Agente de Fluxo, Estados e Transições",
    "agente-acessibilidade-medida": "Agente de Acessibilidade Medida",
    "agente-linguagem-visual": "Agente de Linguagem Visual",
    "agente-nitidez-e-adaptacao": "Agente de Nitidez e Adaptação",
    "agente-dataviz": "Agente de Data-viz",
    "agente-design-system-e-tokens": "Agente de Design System e Tokens",
}

# ADR-009: o que não pode existir como nome de propriedade no schema.
FORBIDDEN_SCORING = {
    "score", "nota", "notas", "minimum_score", "absolute_score", "scorecard",
    "veredito", "verdict", "rubrica", "peso", "pesos", "corte", "cut_score",
    "aprovado", "ranking",
}
FORBIDDEN_PANEL = {
    "painel", "panel", "blind_panel", "blind", "blind_panel_package", "winner",
    "vencedor", "alternativa_vencedora", "provenance_seal", "opaque_id",
    "preference_order", "pairwise",
}
FORBIDDEN_CODE = {
    "codigo", "code", "html", "css", "fxml", "jsx", "patch", "diff", "snippet",
    "implementacao", "script", "stylesheet",
}

DIG = "sha256:" + "a" * 64
STAMP = "2026-07-26T10:00:00Z"


def causal(producer: str = DEPARTMENT, **over: Any) -> dict[str, Any]:
    base = {
        "work_item_id": "WI-DESIGN-001", "front_id": "FR-DESIGN-001",
        "handoff_id": "HO-DESIGN-001", "message_id": "MSG-DESIGN-001",
        "causation_message_ids": ["MSG-DIRETOR-001"],
        "contract_id": "CT-DESIGN-001", "contract_version": 1,
        "contract_digest": DIG, "candidate_digest": "n/a",
        "round": 1, "attempt": 1, "producer": producer,
        "producer_version": "1.0.0", "producer_digest": DIG, "created_at": STAMP,
    }
    base.update(over)
    return base


def signal(label: str = "OBSERVADO", **over: Any) -> dict[str, Any]:
    base = {"subject": "tela de matricula atual", "label": label}
    if label == "OBSERVADO":
        base["locator"] = "capturas/matricula-v3.png"
    if label == "HIPOTESE":
        base["risk"] = "se o publico nao for este, a densidade muda inteira"
    base.update(over)
    return base


def evidence(kind: str = "OBSERVED", **over: Any) -> dict[str, Any]:
    base = {"claim": "contraste do texto principal sobre o fundo", "type": kind,
            "locator": "capturas/matricula-v3.png"}
    if kind == "MEASURED":
        base["measured_value"] = "5.2:1"
        base["measured_method"] = "amostragem dos pixels reais no par texto/fundo"
    if kind == "UNAVAILABLE":
        base["reason"] = "a superficie construida ainda nao existe para medir"
    base.update(over)
    return base


def criterion(state: str = "ATENDIDO", kind: str = "MEASURED", **over: Any) -> dict[str, Any]:
    base = {"criterion": "contraste minimo de 4.5:1 no texto normal",
            "state": state, "evidence": evidence(kind)}
    base.update(over)
    return base


def dimension(name: str, coverage: str = "COBERTA", **over: Any) -> dict[str, Any]:
    owner = {
        "DIRECAO": "agente-direcao-e-anti-slop",
        "FLUXO_ESTADOS": "agente-fluxo-estados-e-transicoes",
        "ACESSIBILIDADE": "agente-acessibilidade-medida",
        "LINGUAGEM_VISUAL": "agente-linguagem-visual",
        "NITIDEZ": "agente-nitidez-e-adaptacao",
        "DATAVIZ": "agente-dataviz",
        "ADAPTACAO_STACK": "agente-nitidez-e-adaptacao",
        "POLISH": DEPARTMENT,
        "EVIDENCIA": DEPARTMENT,
    }[name]
    base = {"dimension": name, "coverage": coverage, "owner": owner}
    if coverage == "NAO_APLICAVEL":
        base["reason"] = "esta superficie nao apresenta nenhum dado tabular ou serie"
    if coverage == "PARCIAL":
        base["missing"] = ["falta o estado parcial/offline"]
    base.update(over)
    return base


def all_dimensions(**over: str) -> list[dict[str, Any]]:
    return [dimension(d, over.get(d, "COBERTA")) for d in DIMENSIONS]


def assignment(capability: str = "FLUXO_ESTADOS", **over: Any) -> dict[str, Any]:
    base = {
        "task_id": f"TASK-{capability}", "worker_id": CAPABILITY_AGENT[capability],
        "capability": capability, "wave": CAPABILITY_WAVE[capability],
        "issued_at": STAMP, "destination": "evidencias/retorno-fluxo.md",
    }
    base.update(over)
    return base


def gate(state: str = "APPROVED", **over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"state": state}
    if state == "APPROVED":
        base.update({"approved_by": "Jeremias", "approved_at": STAMP,
                     "reviewable_surface": "mockups/matricula-v4.md"})
    if state == "REJECTED":
        base["rejection_reason"] = "a densidade proposta nao cabe no viewport alvo"
    base.update(over)
    return base


def dependency(**over: Any) -> dict[str, Any]:
    base = {
        "target": "departamento-desenvolvimento", "kind": "IMPLEMENTACAO",
        "need": "materializar a tela a partir da especificacao aprovada",
        "attached_decision": "tokens semanticos, estados e valores de a11y medidos anexados",
        "origin_rule": "ADR-009",
    }
    base.update(over)
    return base


def plan(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DESIGN_PLAN", "design_plan_id": "PLAN-DESIGN-001",
        "causal": causal(), "department_mission_ref": "DM-DESIGN-001",
        "mode": "PROJETO",
        "design_read": ("Lendo isto como: fluxo de matricula para aluno novo, tarefa concluir "
                        "inscricao, linguagem sobria, sob prazo curto, rumo a superficie densa."),
        "signals": [signal("OBSERVADO"), signal("INFORMADO", subject="publico alvo"),
                    signal("HIPOTESE", subject="frequencia de uso")],
        "waves": [assignment(c) for c in CAPABILITY_WAVE],
        "return_to": DEPARTMENT, "issued_at": STAMP,
    }
    base.update(over)
    return base


def task(capability: str = "FLUXO_ESTADOS", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DESIGN_TASK", "task_id": f"TASK-{capability}",
        "causal": causal(), "capability": capability,
        "worker_id": CAPABILITY_AGENT[capability], "wave": CAPABILITY_WAVE[capability],
        "question": "Qual o fluxo completo da matricula, com estados?",
        "return_to": DEPARTMENT,
        "forbidden_context": ["nao produz codigo, arquivo de tokens nem imagem",
                              "nao compara alternativas e nao pontua"],
        "issued_at": STAMP,
    }
    base.update(over)
    return base


def worker_return(capability: str = "FLUXO_ESTADOS", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DESIGN_RETURN", "task_id": f"TASK-{capability}",
        "causal": causal(), "capability": capability,
        "worker_id": CAPABILITY_AGENT[capability], "status": "COMPLETED",
        "criteria": [criterion()], "dimensions": [],
        "delegated_dependencies": [], "pending": [],
        "return_to": DEPARTMENT, "issued_at": STAMP,
    }
    extras = {
        "FLUXO_ESTADOS": {"states_covered": ["VAZIO", "CARREGANDO", "ERRO", "SUCESSO"]},
        "ACESSIBILIDADE_MEDIDA": {"criteria": [criterion("ATENDIDO", "MEASURED")]},
        "DIRECAO_ANTI_SLOP": {"anti_slop": {
            "first_order_pass": True, "second_order_pass": True,
            "subject_worker": "agente-linguagem-visual"}},
        "DESIGN_SYSTEM_TOKENS": {"tokens": [
            {"name": "cor-acao-primaria", "value": "oklch(0.55 0.18 250)", "category": "COR"}]},
        "NITIDEZ_ADAPTACAO": {"stack_primitives": ["JavaFX VBox", "JavaFX TableView"]},
    }
    base.update(extras.get(capability, {}))
    base.update(over)
    return base


def capability_gap(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DESIGN_CAPABILITY_GAP", "reason": "SUPERFICIE_AUSENTE",
        "capability": "inspecao da superficie existente para o modo POLISH",
        "worker_id": "n/a",
        "expected_contract": "tela, captura, codigo de interface ou URL acessivel",
        "discovery_evidence": "a missao pede polish e nao anexou nenhuma superficie",
        "impact": "afirmar polish sobre tela ausente seria alegacao sem base",
        "status": "OPEN", "owner": "diretor-de-lentes",
    }
    base.update(over)
    return base


def ledger(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DESIGN_LEDGER", "design_ledger_id": "LEDGER-DESIGN-001",
        "causal": causal(), "department_mission_ref": "DM-DESIGN-001",
        "mode": "PROJETO", "plan": plan(),
        "assignments": [assignment(c) for c in CAPABILITY_WAVE],
        "returns_seen": 7, "dimensions": all_dimensions(),
        "design_gate": gate("APPROVED"),
        "implementation_dependencies": [dependency()],
        "capability_gaps": [],
        "test_summary": {"pass": 0, "fail": 0, "skip": 1,
                         "skip_reasons": ["este Departamento nao executa teste"],
                         "critical_fail": False},
        "evidence_refs": ["evidencias/ledger-design.md"],
        "pending": [], "entrega": "ENTREGUE",
        "return_to": "diretor-de-lentes", "recorded_at": STAMP,
    }
    base.update(over)
    return base


def to_department_return(led: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "DEPARTMENT_RETURN",
        "department_return_id": "DR-DESIGN-001",
        "causal": dict(led["causal"]),
        "department_mission_ref": led["department_mission_ref"],
        "returned_by": led["causal"]["producer"],
        "state": "RETURNED",
        "scope_touched": ["superficie de matricula"],
        "artifact_refs": ["mockups/matricula-v4.md"],
        "evidence_refs": led["evidence_refs"],
        "candidate_digest": DIG,
        "test_summary": led["test_summary"],
        "pending_refs": [], "dissent_refs": [],
        "returned_to": "diretor-de-lentes",
        "returned_at": led["recorded_at"],
    }


# --- Regras recalculadas em código, sem ler o campo declarado ---------------

def entrega_fecha(led: dict[str, Any]) -> bool:
    dims = {d["dimension"]: d["coverage"] for d in led.get("dimensions", [])}
    if sorted(dims) != sorted(DIMENSIONS):
        return False
    if any(c == "AUSENTE" for c in dims.values()):
        return False
    if led.get("design_gate", {}).get("state") != "APPROVED":
        return False
    if not led.get("assignments"):
        return False
    if led.get("capability_gaps"):
        return False
    if led.get("pending"):
        return False
    return True


def gate_trava_implementacao(led: dict[str, Any]) -> bool:
    """Mockup-first: com o gate fora de APPROVED, nenhuma dependência sai."""
    aprovado = led.get("design_gate", {}).get("state") == "APPROVED"
    return aprovado or not led.get("implementation_dependencies")


def evidencia_sustenta(crit: dict[str, Any]) -> bool:
    if crit.get("state") != "ATENDIDO":
        return True
    return crit.get("evidence", {}).get("type") not in ("REPORTED", "UNAVAILABLE")


def estados_minimos(cobertos: list[str]) -> bool:
    return {"VAZIO", "CARREGANDO", "ERRO"} <= set(cobertos)


def run() -> int:
    cases: list[tuple[str, bool, list[str]]] = []

    def case(name: str, expected_valid: bool, errors: list[str]) -> None:
        cases.append((name, expected_valid, errors))

    def check(name: str, condition: bool, detail: str = "condição falhou") -> None:
        cases.append((name, True, [] if condition else [detail]))

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))

    # --- A. Pacote e vínculos ------------------------------------------------
    case("arquivos obrigatórios da gerente", True, validate_required_files(
        [SKILL_PATH, CONTRACT_PATH, OPENAI_PATH, SCHEMA_PATH, EVALS_PATH]))
    case("references/ completo", True, validate_required_files([
        REFERENCES_ROOT / "adr-009-design-sem-painel-cego-e-com-time-fixo.md",
        REFERENCES_ROOT / "fronteiras-do-departamento.md",
        REFERENCES_ROOT / "dimensoes-e-cobertura.md",
        REFERENCES_ROOT / "protocolo-de-design.md",
        REFERENCES_ROOT / "origem-migracao.md",
    ]))
    case("agentes/ contém exatamente os sete nomes canônicos", True,
         validate_agents_folder(AGENTS_ROOT, list(AGENT_CAPABILITY)))
    case("frontmatter da gerente", True, validate_frontmatter(SKILL_PATH, DEPARTMENT))

    agent_errors: list[str] = []
    for name, display in AGENT_DISPLAY.items():
        agent_errors += validate_frontmatter(AGENTS_ROOT / name / "SKILL.md", name)
        agent_errors += validate_openai_yaml(
            AGENTS_ROOT / name / "agents" / "openai.yaml", display, f"${name}")
    case("frontmatter e interface dos sete agentes", True, agent_errors)

    case("interface da gerente", True, validate_openai_yaml(
        OPENAI_PATH, "Departamento de Design UX/UI", f"${DEPARTMENT}"))
    case("todos os links markdown internos resolvem", True, validate_links(PACKAGE_ROOT))
    case("série global de ADR é única em toda a estrutura", True, validate_adr_series(STRUCTURE_ROOT))

    posicao: list[str] = []
    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        posicao.append("Departamento fora de departamentos-operacionais/")
    if DIRECTOR_ROOT.name != "diretor-de-lentes":
        posicao.append("Departamento fora do diretor-de-lentes")
    if not RULES_PATH.is_file():
        posicao.append(f"fonte normativa ausente em {RULES_PATH}")
    if "../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in SKILL_PATH.read_text(encoding="utf-8"):
        posicao.append("gerente sem fonte normativa no caminho relativo do nível 4")
    for name in AGENT_CAPABILITY:
        texto = (AGENTS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
        if "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in texto:
            posicao.append(f"{name} sem fonte normativa no caminho relativo do nível 6")
    case("posição na hierarquia e fonte normativa por nível", True, posicao)

    enum_worker = schema["$defs"]["workerId"]["enum"]
    case("enum workerId bate com as pastas reais de agentes/", True,
         [] if sorted(enum_worker) == sorted(AGENT_CAPABILITY)
         else [f"workerId {sorted(enum_worker)} != {sorted(AGENT_CAPABILITY)}"])
    case("as nove dimensões do schema batem com a referência", True,
         [] if schema["$defs"]["dimension"]["enum"] == DIMENSIONS
         else ["enum de dimensões divergente"])

    # --- B. Travas mecânicas do ADR-009 --------------------------------------
    nomes: set[str] = set()
    collect_property_names(schema, nomes)
    for rotulo, proibidos in (
        ("nota", FORBIDDEN_SCORING),
        ("painel comparativo", FORBIDDEN_PANEL),
        ("código", FORBIDDEN_CODE),
    ):
        achados = sorted(nomes & proibidos)
        case(f"schema não tem nenhum campo de {rotulo}", True,
             [] if not achados else [f"campos proibidos no schema: {achados}"])

    case("producer travado por const no causalHeader", True,
         [] if find_const(schema, "producer", DEPARTMENT)
         else ["causalHeader.producer não está travado por const"])
    case("test_summary com pass travado em zero", True,
         [] if find_const(schema, "pass", 0) else ["test_summary.pass não travado em 0"])

    # --- C. Artefatos aceitos ------------------------------------------------
    case("schema aceita DESIGN_PLAN em modo PROJETO", True,
         validate_schema(plan(), schema, schema))
    case("schema aceita DESIGN_PLAN em modo POLISH com superfície observável", True,
         validate_schema(plan(mode="POLISH",
                              observable_surface="capturas/matricula-v3.png"),
                         schema, schema))
    for capability in CAPABILITY_WAVE:
        case(f"schema aceita DESIGN_TASK de {capability}", True,
             validate_schema(task(capability), schema, schema))
        case(f"schema aceita DESIGN_RETURN de {capability}", True,
             validate_schema(worker_return(capability), schema, schema))
    case("schema aceita DESIGN_CAPABILITY_GAP", True,
         validate_schema(capability_gap(), schema, schema))
    case("schema aceita DESIGN_LEDGER com gate aprovado", True,
         validate_schema(ledger(), schema, schema))

    # --- D. Negativos: plano e Design Read -----------------------------------
    case("modo POLISH sem superfície observável", False,
         validate_schema(plan(mode="POLISH"), schema, schema))
    case("modo POLISH com superfície mas sem nenhum sinal OBSERVADO", False,
         validate_schema(plan(mode="POLISH", observable_surface="capturas/x.png",
                              signals=[signal("INFORMADO"), signal("HIPOTESE")]),
                         schema, schema))
    case("sinal OBSERVADO sem dizer onde foi visto", False,
         validate_schema(plan(signals=[{"subject": "tela atual", "label": "OBSERVADO"}]),
                         schema, schema))
    case("sinal HIPOTESE sem o risco declarado", False,
         validate_schema(plan(signals=[{"subject": "publico alvo", "label": "HIPOTESE"}]),
                         schema, schema))
    case("plano sem nenhum sinal classificado", False,
         validate_schema(plan(signals=[]), schema, schema))
    case("plano com produtor forjado por outro Departamento", False,
         validate_schema(plan(causal=causal(producer="departamento-desenvolvimento")),
                         schema, schema))

    # --- E. Negativos: tarefa ------------------------------------------------
    case("tarefa com capacidade trocada para o agente", False,
         validate_schema(task("FLUXO_ESTADOS", worker_id="agente-dataviz"), schema, schema))
    case("acessibilidade emitida fora da onda de verificação", False,
         validate_schema(task("ACESSIBILIDADE_MEDIDA", wave=3), schema, schema))
    case("forbidden_context sem a proibição de produzir código", False,
         validate_schema(task("FLUXO_ESTADOS",
                              forbidden_context=["nao compara alternativas"]), schema, schema))
    case("tarefa endereçada a agente de outro Departamento", False,
         validate_schema(task("FLUXO_ESTADOS", worker_id="agente-modelo-e-grao"),
                         schema, schema))
    case("tarefa com retorno endereçado ao Diretor", False,
         validate_schema(task("FLUXO_ESTADOS", return_to="diretor-de-lentes"), schema, schema))

    # --- F. Negativos: retorno -----------------------------------------------
    case("critério ATENDIDO sustentado por REPORTED", False,
         validate_schema(worker_return("LINGUAGEM_VISUAL",
                                       criteria=[criterion("ATENDIDO", "REPORTED")]),
                         schema, schema))
    case("critério ATENDIDO sustentado por UNAVAILABLE", False,
         validate_schema(worker_return("LINGUAGEM_VISUAL",
                                       criteria=[criterion("ATENDIDO", "UNAVAILABLE")]),
                         schema, schema))
    case("critério UNVERIFIED com evidência UNAVAILABLE (aceito)", True,
         validate_schema(worker_return("LINGUAGEM_VISUAL",
                                       criteria=[criterion("UNVERIFIED", "UNAVAILABLE")]),
                         schema, schema))
    case("MEASURED sem valor e sem método", False,
         validate_schema(worker_return("LINGUAGEM_VISUAL", criteria=[criterion(
             "ATENDIDO", "MEASURED", evidence={"claim": "contraste do texto principal",
                                               "type": "MEASURED"})]), schema, schema))
    case("UNAVAILABLE sem motivo", False,
         validate_schema(worker_return("LINGUAGEM_VISUAL", criteria=[criterion(
             "UNVERIFIED", "UNAVAILABLE",
             evidence={"claim": "contraste do texto principal", "type": "UNAVAILABLE"})]),
             schema, schema))
    case("fluxo concluído sem o estado VAZIO", False,
         validate_schema(worker_return("FLUXO_ESTADOS",
                                       states_covered=["CARREGANDO", "ERRO"]), schema, schema))
    case("fluxo concluído sem o estado ERRO", False,
         validate_schema(worker_return("FLUXO_ESTADOS",
                                       states_covered=["VAZIO", "CARREGANDO"]), schema, schema))
    case("fluxo concluído sem nenhum estado", False,
         validate_schema(worker_return("FLUXO_ESTADOS", states_covered=[]), schema, schema))
    case("a11y concluída sem nenhum critério medido", False,
         validate_schema(worker_return("ACESSIBILIDADE_MEDIDA",
                                       criteria=[criterion("ATENDIDO", "OBSERVED")]),
                         schema, schema))
    case("anti-slop rodado sobre a própria saída", False,
         validate_schema(worker_return("DIRECAO_ANTI_SLOP", anti_slop={
             "first_order_pass": True, "second_order_pass": True,
             "subject_worker": "agente-direcao-e-anti-slop"}), schema, schema))
    case("tokens concluídos sem nenhum token", False,
         validate_schema(worker_return("DESIGN_SYSTEM_TOKENS", tokens=[]), schema, schema))
    case("adaptação concluída sem nomear primitiva do stack", False,
         validate_schema(worker_return("NITIDEZ_ADAPTACAO", stack_primitives=[]),
                         schema, schema))
    case("retorno BLOCKED sem motivo", False,
         validate_schema(worker_return("DATAVIZ", status="BLOCKED"), schema, schema))
    case("retorno BLOCKED com motivo (aceito)", True,
         validate_schema(worker_return("DATAVIZ", status="BLOCKED",
                                       blocked_reason="a missao pede tuning de query, fora do escopo"),
                         schema, schema))
    case("dimensão NAO_APLICAVEL sem motivo específico", False,
         validate_schema(worker_return("DATAVIZ", dimensions=[
             {"dimension": "DATAVIZ", "coverage": "NAO_APLICAVEL",
              "owner": "agente-dataviz"}]), schema, schema))
    case("dimensão PARCIAL sem nomear o que falta", False,
         validate_schema(worker_return("FLUXO_ESTADOS", dimensions=[
             {"dimension": "FLUXO_ESTADOS", "coverage": "PARCIAL",
              "owner": "agente-fluxo-estados-e-transicoes"}]), schema, schema))

    # --- G. Negativos: livro-razão e gate visual -----------------------------
    case("dependência de implementação com o gate PENDING", False,
         validate_schema(ledger(design_gate=gate("PENDING"), entrega="INCOMPLETA"),
                         schema, schema))
    case("dependência de implementação com o gate REJECTED", False,
         validate_schema(ledger(design_gate=gate("REJECTED"), entrega="INCOMPLETA"),
                         schema, schema))
    case("gate PENDING sem nenhuma dependência de implementação (aceito)", True,
         validate_schema(ledger(design_gate=gate("PENDING"), entrega="INCOMPLETA",
                                implementation_dependencies=[],
                                dimensions=all_dimensions(EVIDENCIA="PARCIAL")),
                         schema, schema))
    case("aprovação sem ator nomeado", False,
         validate_schema(ledger(design_gate={"state": "APPROVED"}), schema, schema))
    case("aprovação sem superfície revisável", False,
         validate_schema(ledger(design_gate={
             "state": "APPROVED", "approved_by": "Jeremias", "approved_at": STAMP}),
             schema, schema))
    case("entrega ENTREGUE com a dimensão de fluxo e estados AUSENTE", False,
         validate_schema(ledger(dimensions=all_dimensions(FLUXO_ESTADOS="AUSENTE")),
                         schema, schema))
    case("entrega ENTREGUE com a dimensão de a11y AUSENTE", False,
         validate_schema(ledger(dimensions=all_dimensions(ACESSIBILIDADE="AUSENTE")),
                         schema, schema))
    case("livro-razão com oito dimensões", False,
         validate_schema(ledger(dimensions=all_dimensions()[:8]), schema, schema))
    case("livro-razão com dimensão duplicada", False,
         validate_schema(ledger(dimensions=all_dimensions()[:8] + [dimension("DIRECAO",
                                                                            "PARCIAL")]),
                         schema, schema))
    case("ENTREGUE sem registro de emissão das tarefas", False,
         validate_schema(ledger(assignments=[]), schema, schema))
    case("ENTREGUE com pendência pendurada", False,
         validate_schema(ledger(pending=["falta validar com usuario real"]), schema, schema))
    case("lacuna aberta sem bloquear a entrega", False,
         validate_schema(ledger(capability_gaps=[capability_gap()]), schema, schema))
    case("lacuna aberta com entrega BLOQUEADA (aceito)", True,
         validate_schema(ledger(capability_gaps=[capability_gap()], entrega="BLOQUEADA",
                                design_gate=gate("PENDING"),
                                implementation_dependencies=[]), schema, schema))
    case("livro-razão declarando teste executado", False,
         validate_schema(ledger(test_summary={"pass": 5, "fail": 0, "skip": 0,
                                              "skip_reasons": [], "critical_fail": False}),
                         schema, schema))
    case("livro-razão devolvido para fora do Diretor", False,
         validate_schema(ledger(return_to="ceo-maestro"), schema, schema))
    case("entrega INCOMPLETA com dimensão ausente (aceita)", True,
         validate_schema(ledger(entrega="INCOMPLETA",
                                dimensions=all_dimensions(DATAVIZ="AUSENTE")),
                         schema, schema))

    # --- H. Fronteira: validada contra o schema do CONSUMIDOR ----------------
    dept_return = to_department_return(ledger())
    case("Diretor aceita o DEPARTMENT_RETURN convertido do DESIGN_LEDGER", True,
         validate_schema(dept_return, director["$defs"]["departmentReturn"], director))

    forjado = copy.deepcopy(dept_return)
    forjado["returned_by"] = "departamento-arquitetura-dados"
    case("Diretor rejeita retorno com autor divergente do produtor", False,
         validate_schema(forjado, director["$defs"]["departmentReturn"], director))

    fora = copy.deepcopy(dept_return)
    fora["returned_to"] = "ceo-maestro"
    case("Diretor rejeita retorno endereçado ao CEO", False,
         validate_schema(fora, director["$defs"]["departmentReturn"], director))

    op_enum = director["$defs"]["operationalDepartment"]["enum"]
    check("Diretor reconhece este Departamento como operacional",
          DEPARTMENT in op_enum, f"{DEPARTMENT} ausente de operationalDepartment")
    known = json.dumps(director["$defs"].get("knownCapability", {}), ensure_ascii=False)
    check("Diretor reconhece este Departamento como produtor causal",
          DEPARTMENT in known, f"{DEPARTMENT} ausente de knownCapability")
    juizes_schema = json.loads(
        (DIRECTOR_ROOT / "departamento-juizes" / "schemas"
         / "departamento-juizes.schema.json").read_text(encoding="utf-8"))
    check("o modo comparativo continua sendo dos Juízes, não daqui",
          "DISPUTA" in json.dumps(juizes_schema, ensure_ascii=False),
          "modo DISPUTA ausente do schema dos Juízes")

    # --- I. Regras recalculadas em código ------------------------------------
    check("entrega fecha com as nove dimensões cobertas e gate aprovado",
          entrega_fecha(ledger()))
    for dim in ("FLUXO_ESTADOS", "ACESSIBILIDADE", "DIRECAO", "EVIDENCIA"):
        check(f"entrega não fecha com a dimensão {dim} ausente",
              not entrega_fecha(ledger(dimensions=all_dimensions(**{dim: "AUSENTE"}))))
    check("oito dimensões cobertas não compensam a nona ausente",
          not entrega_fecha(ledger(dimensions=all_dimensions(DATAVIZ="AUSENTE"))))
    check("entrega não fecha com o gate PENDING",
          not entrega_fecha(ledger(design_gate=gate("PENDING"))))
    check("entrega não fecha sem registro de emissão",
          not entrega_fecha(ledger(assignments=[])))
    check("entrega não fecha com lacuna aberta",
          not entrega_fecha(ledger(capability_gaps=[capability_gap()])))
    check("dimensão PARCIAL não impede a entrega",
          entrega_fecha(ledger(dimensions=all_dimensions(NITIDEZ="PARCIAL"))))
    check("gate aberto trava a dependência de implementação",
          not gate_trava_implementacao(ledger(design_gate=gate("PENDING"))))
    check("gate aprovado libera a dependência",
          gate_trava_implementacao(ledger()))
    check("gate aberto sem dependência não é violação",
          gate_trava_implementacao(ledger(design_gate=gate("PENDING"),
                                          implementation_dependencies=[])))
    check("REPORTED não sustenta atendido",
          not evidencia_sustenta(criterion("ATENDIDO", "REPORTED")))
    check("UNAVAILABLE não sustenta atendido",
          not evidencia_sustenta(criterion("ATENDIDO", "UNAVAILABLE")))
    check("MEASURED sustenta atendido", evidencia_sustenta(criterion("ATENDIDO", "MEASURED")))
    check("REPORTED em critério UNVERIFIED é legítimo",
          evidencia_sustenta(criterion("UNVERIFIED", "REPORTED")))
    check("os três estados mínimos são exigidos",
          not estados_minimos(["VAZIO", "CARREGANDO"]))
    check("os três estados mínimos presentes bastam",
          estados_minimos(["VAZIO", "CARREGANDO", "ERRO"]))
    check("cada dimensão tem exatamente uma dona",
          len({d["dimension"] for d in all_dimensions()}) == 9)
    check("as sete capacidades cobrem sete dimensões distintas mais o contrato",
          len(set(AGENT_CAPABILITY.values())) == 7)

    # --- Coerência do catálogo ----------------------------------------------
    catalogo = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    check("catálogo de evals tem ao menos 12 casos",
          len(catalogo.get("cases", [])) >= 12,
          f"catálogo com {len(catalogo.get('cases', []))} casos")
    check("todo caso do catálogo declara acionamento e aderência",
          all({"acionou", "aderiu"} <= set(c) for c in catalogo.get("cases", [])),
          "caso sem acionou/aderiu")
    check("catálogo tem ao menos um caso de recusa por fronteira",
          any(c.get("espera_recusa") for c in catalogo.get("cases", [])),
          "nenhum caso de recusa")
    check("digest das regras de ouro é verificável",
          RULES_PATH.is_file() and sha256_file(RULES_PATH).startswith("sha256:"))
    check("digest do próprio schema é verificável",
          digest(SCHEMA_PATH.read_text(encoding="utf-8")).startswith("sha256:"))

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
