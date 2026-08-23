"""Validador determinístico do Departamento de Desenvolvimento.

Prova mecanicamente o que o ADR-012 fixou: aqui se EXECUTA (o test_summary carrega
número real, ao contrário de todos os outros Departamentos); quem implementa não
revisa nem atesta a si mesmo; os cinco inegociáveis nunca são simplificados; o
piso de bordas é vazio + limite + erro; e a Regra dos Três para na terceira falha.

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
SCHEMA_PATH = PACKAGE_ROOT / "schemas" / "departamento-desenvolvimento.schema.json"
# Valor DECLARADO do schema deste pacote, conferido a cada execucao por
# conferir_digest_declarado(). Receita: sha256 do conteudo com CRLF->LF e sem
# BOM (validador_schema.py::sha256_texto_normalizado) — a mesma da fonte
# normativa, para que a conferencia sobreviva a um clone com outro EOL.
# Quem alterar o schema atualiza esta linha no MESMO commit; sem isso, reprova.
SCHEMA_DIGEST_DECLARADO = (
    "sha256:29201676d2b09d9a6ecaf6f726f8e20d3ade3062e8e3a6b00f11551370d476f9"
)
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
        collect_property_names,
        conferir_digest_das_regras,
        conferir_digest_declarado,
        digest,
        find_const,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_agents_folder, validate_contract_sections,
        validate_frontmatter,
        validate_links, validate_openai_yaml, validate_required_files,
        validate_skill_tokens, SECOES_CONTRATO_AGENTE, TOKENS_SKILL_AGENTE,
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
    print(f"[FAIL] motor compartilhado ausente em {STRUCTURE_ROOT}/_compartilhado: {exc}")
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

DEPARTMENT = "departamento-desenvolvimento"

AGENT_CAPABILITY = {
    "agente-java-e-spring": "JAVA_SPRING",
    "agente-javafx-desktop": "JAVAFX_DESKTOP",
    "agente-web-frontend": "WEB_FRONTEND",
    "agente-tauri-desktop": "TAURI_DESKTOP",
    "agente-mobile-flutter": "MOBILE_FLUTTER",
    "agente-persistencia-e-sql": "PERSISTENCIA_SQL",
    "agente-revisao-e-refatoracao": "REVISAO_REFATORACAO",
    "agente-testes-e-depuracao": "TESTES_DEPURACAO",
}
CAP_AGENT = {v: k for k, v in AGENT_CAPABILITY.items()}
IMPLEMENTA = ["JAVA_SPRING", "JAVAFX_DESKTOP", "WEB_FRONTEND", "TAURI_DESKTOP",
              "MOBILE_FLUTTER", "PERSISTENCIA_SQL"]
INEGOCIAVEIS = ["VALIDACAO_FRONTEIRA", "ERRO_PERDA_DADO", "SEGURANCA",
                "ACESSIBILIDADE", "REQUISITO_EXPLICITO"]
AGENT_DISPLAY = {
    "agente-java-e-spring": "Agente Java e Spring Boot",
    "agente-javafx-desktop": "Agente JavaFX Desktop",
    "agente-web-frontend": "Agente Web Frontend",
    "agente-tauri-desktop": "Agente Tauri Desktop",
    "agente-mobile-flutter": "Agente Mobile Flutter",
    "agente-persistencia-e-sql": "Agente de Persistência e SQL",
    "agente-revisao-e-refatoracao": "Agente de Revisão e Refatoração",
    "agente-testes-e-depuracao": "Agente de Testes e Depuração",
}

FORBIDDEN_SCORING = {"score", "nota", "notas", "minimum_score", "scorecard", "veredito",
                     "verdict", "rubrica", "peso", "corte", "cut_score", "ranking", "winner"}
FORBIDDEN_MACRO = {"modulo", "modulos", "c4", "topologia", "bounded_context", "ownership",
                   "grao", "one_row_means", "expand_contract", "token_semantico", "paleta"}

DIG = "sha256:" + "a" * 64
DIG2 = "sha256:" + "b" * 64
STAMP = "2026-07-26T10:00:00Z"


def causal(producer: str = DEPARTMENT, **over: Any) -> dict[str, Any]:
    base = {
        "work_item_id": "WI-DEV-001", "front_id": "FR-DEV-001", "handoff_id": "HO-DEV-001",
        "message_id": "MSG-DEV-001", "causation_message_ids": ["MSG-DIRETOR-001"],
        "contract_id": "CT-DEV-001", "contract_version": 1, "contract_digest": DIG,
        "candidate_digest": DIG2, "round": 1, "attempt": 1, "producer": producer,
        "producer_version": "1.0.0", "producer_digest": DIG, "created_at": STAMP,
    }
    base.update(over)
    return base


def ladder(**over: Any) -> dict[str, Any]:
    base = {"change": "escrita do DAO de matricula", "step": "DEP_INSTALADA",
            "simplificado": False}
    base.update(over)
    return base


def edge(**over: Any) -> dict[str, Any]:
    base = {"unit": "MatriculaDao.salvar", "vazio": True, "limite": True, "erro": True}
    base.update(over)
    return base


def evidence(**over: Any) -> dict[str, Any]:
    base = {"pass": 14, "fail": 0, "skip": 0, "skip_reasons": [], "against_digest": DIG2,
            "executed_by": "agente-testes-e-depuracao", "executed_at": STAMP,
            "command": "mvn -q test"}
    base.update(over)
    return base


def ponytail(**over: Any) -> dict[str, Any]:
    base = {"locator": "CsvExporter.java:41",
            "simplificado": "escrita CSV sem aspas nem escape, formato interno",
            "teto": "valor com ';' embutido e rejeitado com erro claro",
            "upgrade": "primeiro campo real que precise de ';'",
            "falha_explicita": True}
    base.update(over)
    return base


def assumption(**over: Any) -> dict[str, Any]:
    base = {"locator": "MatriculaRepo.java:12",
            "claim": "assumindo findByTenant(UUID) como assinatura do repositorio",
            "why_unconfirmed": "a interface real nao foi anexada a missao"}
    base.update(over)
    return base


def assignment(capability: str = "JAVA_SPRING", **over: Any) -> dict[str, Any]:
    base = {"task_id": f"TASK-{capability}", "worker_id": CAP_AGENT[capability],
            "capability": capability,
            "wave": 3 if capability in ("REVISAO_REFATORACAO", "TESTES_DEPURACAO") else 2,
            "package": "matricula-dao", "issued_at": STAMP}
    base.update(over)
    return base


def plan(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DEV_PLAN", "dev_plan_id": "PLAN-DEV-001", "causal": causal(),
        "department_mission_ref": "DM-DEV-001", "track": "JAVA_SPRING",
        "upstream_present": True,
        "packages": [{"package": "matricula-dao", "lead_worker": "agente-java-e-spring",
                      "files": ["MatriculaDao.java"],
                      "done": "DAO com acesso parametrizado e teste verde"}],
        "assignments": [assignment("JAVA_SPRING"), assignment("REVISAO_REFATORACAO"),
                        assignment("TESTES_DEPURACAO")],
        "return_to": DEPARTMENT, "issued_at": STAMP,
    }
    base.update(over)
    return base


def task(capability: str = "JAVA_SPRING", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DEV_TASK", "task_id": f"TASK-{capability}", "causal": causal(),
        "capability": capability, "worker_id": CAP_AGENT[capability],
        "wave": 3 if capability in ("REVISAO_REFATORACAO", "TESTES_DEPURACAO") else 2,
        "package": "matricula-dao",
        "objective": "implementar o DAO de matricula conforme o grao entregue",
        "return_to": DEPARTMENT,
        "forbidden_context": ["nao decide grao, pacote nem token",
                              "nao inventa API, metodo ou assinatura"],
        "issued_at": STAMP,
    }
    base.update(over)
    return base


def worker_return(capability: str = "JAVA_SPRING", **over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DEV_RETURN", "task_id": f"TASK-{capability}", "causal": causal(),
        "capability": capability, "worker_id": CAP_AGENT[capability], "status": "COMPLETED",
        "assumptions": [], "ponytails": [], "delegated_dependencies": [], "pending": [],
        "return_to": DEPARTMENT, "issued_at": STAMP,
    }
    if capability in IMPLEMENTA:
        base.update({"artifacts": ["MatriculaDao.java"], "ladder": [ladder()],
                     "generator_used": "java-jdbc-dao"})
    if capability == "TESTES_DEPURACAO":
        base.update({"test_evidence": evidence(), "edges": [edge()]})
    if capability == "REVISAO_REFATORACAO":
        base.update({"review_of_worker": "agente-java-e-spring"})
    base.update(over)
    return base


def capability_gap(**over: Any) -> dict[str, Any]:
    base = {"artifact_type": "DEV_CAPABILITY_GAP", "reason": "TRACK_SEM_AGENTE",
            "capability": "implementacao em Go com framework Gin", "worker_id": "n/a",
            "expected_contract": "track declarado com gerador que o sustente",
            "discovery_evidence": "nenhum dos cinco tracks cobre Go",
            "impact": "improvisar executor produziria codigo sem convencao do acervo",
            "status": "OPEN", "owner": "diretor-de-lentes"}
    base.update(over)
    return base


def ledger(**over: Any) -> dict[str, Any]:
    base = {
        "artifact_type": "DEV_LEDGER", "dev_ledger_id": "LEDGER-DEV-001", "causal": causal(),
        "department_mission_ref": "DM-DEV-001", "track": "JAVA_SPRING", "plan": plan(),
        "assignments": [assignment("JAVA_SPRING"), assignment("TESTES_DEPURACAO")],
        "returns_seen": 3, "edges": [edge()], "test_evidence": evidence(),
        "candidate_digest": DIG2, "reviewed": True, "assumptions": [], "ponytails": [],
        "delegated_dependencies": [], "capability_gaps": [],
        "evidence_refs": ["evidencias/bateria-matricula.md"], "pending": [],
        "entrega": "ENTREGUE", "return_to": "diretor-de-lentes", "recorded_at": STAMP,
    }
    base.update(over)
    return base


def to_department_return(led: dict[str, Any]) -> dict[str, Any]:
    """Converte o livro-razao no envelope do Diretor — com numero real de teste."""
    ev = led["test_evidence"]
    return {
        "artifact_type": "DEPARTMENT_RETURN", "department_return_id": "DR-DEV-001",
        "causal": dict(led["causal"]),
        "department_mission_ref": led["department_mission_ref"],
        "returned_by": led["causal"]["producer"], "state": "RETURNED",
        "scope_touched": ["DAO de matricula"], "artifact_refs": ["MatriculaDao.java"],
        "evidence_refs": led["evidence_refs"], "candidate_digest": led["candidate_digest"],
        "test_summary": {"pass": ev["pass"], "fail": ev["fail"], "skip": ev["skip"],
                         "skip_reasons": ev["skip_reasons"], "critical_fail": ev["fail"] > 0},
        "pending_refs": [], "dissent_refs": [], "returned_to": "diretor-de-lentes",
        "returned_at": led["recorded_at"],
    }


# --- Regras recalculadas em codigo ------------------------------------------

def gate_fecha(led: dict[str, Any]) -> bool:
    for e in led.get("edges", []):
        if not (e.get("vazio") and e.get("limite") and e.get("erro")):
            return False
    if not led.get("edges"):
        return False
    ev = led.get("test_evidence", {})
    if ev.get("fail", 1) != 0:
        return False
    if ev.get("against_digest") != led.get("candidate_digest"):
        return False
    if ev.get("executed_by") != "agente-testes-e-depuracao":
        return False
    if not led.get("reviewed"):
        return False
    if not led.get("assignments"):
        return False
    if led.get("capability_gaps") or led.get("pending"):
        return False
    return True


def prova_fresca(led: dict[str, Any]) -> bool:
    return led.get("test_evidence", {}).get("against_digest") == led.get("candidate_digest")

def _admission_def(schema: dict[str, Any]) -> dict[str, Any]:
    return schema["$defs"]["departmentMissionAdmission"]


def director_mission(schema: dict[str, Any], *, causal_over: dict[str, Any] | None = None,
                     **over: Any) -> dict[str, Any]:
    """Payload de teste. A trava nao mora aqui: mora no const do schema, lido por mission_verdict."""
    director = "diretor-de-lentes"
    base: dict[str, Any] = {
        "artifact_type": "DEPARTMENT_MISSION",
        "department_mission_id": "DM-DEV-001",
        "causal": {
            "work_item_id": "WI-DEV-001", "front_id": "FR-DEV-001",
            "handoff_id": "HO-DEV-001", "message_id": "MSG-DIR-001",
            "causation_message_ids": ["MSG-CEO-001"],
            "contract_id": "CT-DEV-001", "contract_version": 1,
            "contract_digest": DIG, "candidate_digest": DIG2,
            "round": 1, "attempt": 1, "producer": director,
            "producer_version": "1.0.0", "producer_digest": DIG,
            "created_at": STAMP,
        },
        "recipient": DEPARTMENT, "mode": "ATUA",
        "objective": "implementar o DAO de matricula no track Java",
        "scope_in": ["DAO de matricula"],
        "scope_out": ["modelo de dados", "nota"],
        "inputs": ["contrato de arquitetura anexado"],
        "deliverables": ["DEV_LEDGER com evidencia executada"],
        "done": ["DAO com teste verde e revisao independente"],
        "required_evidence": ["bateria executada contra o digest"],
        "depends_on": ["grao da tabela de matricula"],
        "handoff_to": [director],
        "decision_authority": ["implementacao dentro das decisoes anexadas"],
        "permissions": {
            "default_policy": "deny",
            "allowed_tools": ["filesystem_read"],
            "allowed_resources": ["workspace"],
            "expires_at": STAMP,
        },
        "stop_when": ["ledger devolvido ao Diretor"],
        "return_to": director, "issued_at": STAMP,
    }
    if causal_over:
        base["causal"] = {**base["causal"], **causal_over}
    base.update(over)
    return base


def mission_verdict(mission: dict[str, Any], *, contract_digest: str,
                    schema: dict[str, Any],
                    target_present: bool = True) -> str:
    """Classifica a missao de entrada contra o contrato local. Sem const, nao ha trava."""
    adm = _admission_def(schema)
    expected_p = adm["properties"]["causal"]["properties"]["producer"].get("const")
    expected_r = adm["properties"]["return_to"].get("const")
    expected_dest = adm["properties"]["recipient"].get("const")
    if expected_p and mission.get("causal", {}).get("producer") != expected_p:
        return "BLOCKED_BYPASS_ATTEMPT"
    if expected_r and mission.get("return_to") != expected_r:
        return "BLOCKED_BYPASS_ATTEMPT"
    if expected_dest and mission.get("recipient") != expected_dest:
        return "BLOCKED_INVALID_MISSION"
    if not mission.get("causal", {}).get("contract_digest"):
        return "BLOCKED_INVALID_MISSION"
    if mission["causal"]["contract_digest"] != contract_digest:
        return "BLOCKED_CONTRACT_MISMATCH"
    if not target_present:
        return "BLOCKED_INVALID_MISSION"
    return "ACEITA"


def run() -> int:
    cases: list[tuple[str, bool, list[str]]] = []

    def case(name: str, ok: bool, errors: list[str]) -> None:
        cases.append((name, ok, errors))

    def check(name: str, cond: bool, detail: str = "condição falhou") -> None:
        cases.append((name, True, [] if cond else [detail]))

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    director = json.loads(DIRECTOR_SCHEMA_PATH.read_text(encoding="utf-8"))

    # --- A. Pacote -----------------------------------------------------------
    case("arquivos obrigatórios da gerente", True, validate_required_files(
        [SKILL_PATH, CONTRACT_PATH, OPENAI_PATH, SCHEMA_PATH, EVALS_PATH]))
    case("references/ completo", True, validate_required_files([
        REFERENCES_ROOT / "adr-012-desenvolvimento-executa-com-oito-agentes.md",
        REFERENCES_ROOT / "tracks-e-geradores.md",
        REFERENCES_ROOT / "politica-tecnica.md",
        REFERENCES_ROOT / "fronteiras-do-departamento.md",
        REFERENCES_ROOT / "protocolo-de-desenvolvimento.md",
        REFERENCES_ROOT / "origem-migracao.md"]))
    case("agentes/ contém exatamente os oito nomes", True,
         validate_agents_folder(AGENTS_ROOT, list(AGENT_CAPABILITY)))
    case("frontmatter da gerente", True, validate_frontmatter(SKILL_PATH, DEPARTMENT))

    err: list[str] = []
    for name, display in AGENT_DISPLAY.items():
        err += validate_frontmatter(AGENTS_ROOT / name / "SKILL.md", name)
        err += validate_openai_yaml(AGENTS_ROOT / name / "agents" / "openai.yaml",
                                    display, f"${name}")
    case("frontmatter e interface dos oito agentes", True, err)

    # --- Estrutura normativa dos contratos e SKILL de agente ------------------
    # GUIA, passos 7 e 8. Até 2026-07-27 este validador não olhava heading de
    # contrato nem token de SKILL, e os oito agentes deste pacote usavam uma
    # anatomia própria: zero dos seis tokens, trava anti-bypass ausente. A
    # conferência mora no _compartilhado; a lista do que é obrigatório continua
    # sendo decisão deste pacote.
    err = []
    for name in AGENT_CAPABILITY:
        err += validate_contract_sections(
            AGENTS_ROOT / name / "CONTRATO-DE-COMPROMISSO.md",
            SECOES_CONTRATO_AGENTE, name)
        err += validate_skill_tokens(
            AGENTS_ROOT / name / "SKILL.md", TOKENS_SKILL_AGENTE, name)
    case("estrutura normativa dos oito agentes", True, err)

    # As duas checagens de ESTRUTURA INTEIRA. Achado da rodada 4 do forward test de
    # cadeia (2026-07-27): este era o unico dos 15 validadores que nao chamava
    # nenhuma das duas -- ficava fora da trava global sem que nada acusasse.
    case("série global de ADR é única em toda a estrutura", True,
         validate_adr_series(STRUCTURE_ROOT))
    case("todo pacote gerente tem validador que roda a trava global", True,
         validate_cobertura_de_validadores(STRUCTURE_ROOT))
    case("a recusa de digest() dispara e ninguém tem cópia privada do motor", True,
         validate_trava_de_digest(STRUCTURE_ROOT))
    case("nenhuma asserção é verdadeira por construção sobre valor produzido", True,
         validate_sem_check_tautologico(STRUCTURE_ROOT))
    cases.append(("nenhum placar de pacote declara total de cadeia como estado corrente", True, validate_placar_nao_declara_cadeia(STRUCTURE_ROOT)))
    cases.append(("a contagem publicada aponta para o digest do instrumento vigente", True, validate_contagem_ligada_ao_instrumento(STRUCTURE_ROOT)))
    cases.append(("as travas do modulo compartilhado nao estao neutralizadas", True, validate_travas_compartilhadas_com_efeito(STRUCTURE_ROOT)))
    cases.append(("toda pendencia declarada nomeia quem responde por ela", True, validate_pendencia_tem_dono(STRUCTURE_ROOT)))
    case("a fonte normativa confere com o valor declarado em ORIGEM.md", True,
         validate_fonte_normativa_conferida(STRUCTURE_ROOT))
    case("contratos de gerente na anatomia canônica", True,
         validate_contratos_de_gerente(STRUCTURE_ROOT))
    case("interface da gerente", True, validate_openai_yaml(
        OPENAI_PATH, "Departamento de Desenvolvimento", f"${DEPARTMENT}"))
    case("todos os links markdown internos resolvem", True, validate_links(PACKAGE_ROOT))

    pos: list[str] = []
    if PACKAGE_ROOT.parent.name != "departamentos-operacionais":
        pos.append("fora de departamentos-operacionais/")
    if "../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in SKILL_PATH.read_text(encoding="utf-8"):
        pos.append("gerente sem fonte normativa no nível 4")
    for name in AGENT_CAPABILITY:
        if "../../../../../../regras-de-ouro/REGRAS-DE-OURO.md" not in (
                AGENTS_ROOT / name / "SKILL.md").read_text(encoding="utf-8"):
            pos.append(f"{name} sem fonte normativa no nível 6")
    case("posição e fonte normativa por nível", True, pos)
    case("enum workerId bate com as pastas reais", True,
         [] if sorted(schema["$defs"]["workerId"]["enum"]) == sorted(AGENT_CAPABILITY)
         else ["workerId divergente"])

    # --- B. Travas do ADR-012 ------------------------------------------------
    nomes: set[str] = set()
    collect_property_names(schema, nomes)
    for rot, proib in (("nota", FORBIDDEN_SCORING), ("decisão alheia", FORBIDDEN_MACRO)):
        achados = sorted(nomes & proib)
        case(f"schema não tem campo de {rot}", True,
             [] if not achados else [f"campos proibidos: {achados}"])
    case("producer travado por const", True,
         [] if find_const(schema, "producer", DEPARTMENT) else ["producer não travado"])
    # A trava que distingue este Departamento de todos os outros:
    case("test_summary NÃO está travado em zero — ADR-012 §1", True,
         [] if not find_const(schema, "pass", 0)
         else ["pass travado em 0: este Departamento executa e o número é real"])
    case("executed_by travado no agente de testes", True,
         [] if find_const(schema, "executed_by", "agente-testes-e-depuracao")
         else ["executed_by não travado"])
    case("falha_explicita do ponytail travada em true", True,
         [] if find_const(schema, "falha_explicita", True) else ["falha_explicita não travada"])

    # --- C. Artefatos aceitos ------------------------------------------------
    case("schema aceita DEV_PLAN com upstream presente", True,
         validate_schema(plan(), schema, schema))
    case("schema aceita DEV_PLAN com upstream ausente e zero atribuições", True,
         validate_schema(plan(upstream_present=False, assignments=[],
                              upstream_missing=["grão da tabela de matrícula"]),
                         schema, schema))
    for cap in AGENT_CAPABILITY.values():
        case(f"schema aceita DEV_TASK de {cap}", True,
             validate_schema(task(cap), schema, schema))
        case(f"schema aceita DEV_RETURN de {cap}", True,
             validate_schema(worker_return(cap), schema, schema))
    case("schema aceita DEV_CAPABILITY_GAP", True,
         validate_schema(capability_gap(), schema, schema))
    case("schema aceita DEV_LEDGER com o gate fechado", True,
         validate_schema(ledger(), schema, schema))

    # --- D. Negativos: plano -------------------------------------------------
    case("upstream ausente mas com atribuição emitida", False,
         validate_schema(plan(upstream_present=False,
                              upstream_missing=["grão"]), schema, schema))
    case("upstream ausente sem nomear o que falta", False,
         validate_schema(plan(upstream_present=False, assignments=[]), schema, schema))
    case("plano com produtor forjado", False,
         validate_schema(plan(causal=causal(producer="departamento-arquitetura-dados")),
                         schema, schema))

    # --- E. Negativos: tarefa ------------------------------------------------
    case("tarefa com capacidade trocada para o agente", False,
         validate_schema(task("JAVA_SPRING", worker_id="agente-mobile-flutter"),
                         schema, schema))
    case("verificação independente emitida fora da onda 3", False,
         validate_schema(task("TESTES_DEPURACAO", wave=2), schema, schema))
    case("forbidden_context sem a proibição de decidir ou inventar", False,
         validate_schema(task("JAVA_SPRING", forbidden_context=["nao pontua"]),
                         schema, schema))
    case("tarefa endereçada a agente de outro Departamento", False,
         validate_schema(task("JAVA_SPRING", worker_id="agente-modelo-e-grao"),
                         schema, schema))

    # --- F. Negativos: retorno ----------------------------------------------
    case("implementação concluída sem declarar o degrau da escada", False,
         validate_schema(worker_return("JAVA_SPRING", ladder=[]), schema, schema))
    case("implementação concluída sem artefato", False,
         validate_schema(worker_return("JAVA_SPRING", artifacts=[]), schema, schema))
    for ineg in INEGOCIAVEIS:
        case(f"inegociável {ineg} marcado como simplificado", False,
             validate_schema(worker_return("JAVA_SPRING", ladder=[
                 ladder(inegociavel=ineg, simplificado=True)]), schema, schema))
    case("inegociável não simplificado (aceito)", True,
         validate_schema(worker_return("JAVA_SPRING", ladder=[
             ladder(inegociavel="SEGURANCA", simplificado=False)]), schema, schema))
    case("quem implementa produzindo a própria evidência — ADR-012 §5", False,
         validate_schema(worker_return("JAVA_SPRING", test_evidence=evidence()),
                         schema, schema))
    case("revisor revisando a própria saída", False,
         validate_schema(worker_return("REVISAO_REFATORACAO",
                                       review_of_worker="agente-revisao-e-refatoracao"),
                         schema, schema))
    case("testes concluídos sem evidência de execução", False,
         validate_schema({k: v for k, v in worker_return("TESTES_DEPURACAO").items()
                          if k != "test_evidence"}, schema, schema))
    case("testes concluídos sem cobertura de borda", False,
         validate_schema(worker_return("TESTES_DEPURACAO", edges=[]), schema, schema))
    case("evidência produzida por quem não é o agente de testes", False,
         validate_schema(worker_return("TESTES_DEPURACAO", test_evidence=evidence(
             executed_by="agente-java-e-spring")), schema, schema))
    case("SKIP sem motivo", False,
         validate_schema(worker_return("TESTES_DEPURACAO",
                                       test_evidence=evidence(skip=2)), schema, schema))
    case("SKIP com motivo (aceito)", True,
         validate_schema(worker_return("TESTES_DEPURACAO", test_evidence=evidence(
             skip=2, skip_reasons=["ambiente sem Docker para o teste de integração"])),
             schema, schema))
    case("borda ausente sem justificativa", False,
         validate_schema(worker_return("TESTES_DEPURACAO",
                                       edges=[edge(erro=False)]), schema, schema))
    case("borda ausente com justificativa (aceita)", True,
         validate_schema(worker_return("TESTES_DEPURACAO", edges=[edge(
             erro=False,
             justificativa_ausencia="o metodo nao possui caminho de erro alcancavel")]),
             schema, schema))
    case("ponytail sem teto e sem gatilho", False,
         validate_schema(worker_return("JAVA_SPRING", ponytails=[{
             "locator": "X.java:1", "simplificado": "escrita simples",
             "falha_explicita": True}]), schema, schema))
    case("ponytail completo (aceito)", True,
         validate_schema(worker_return("JAVA_SPRING", ponytails=[ponytail()]),
                         schema, schema))
    case("SUPOSIÇÃO sem dizer por que não foi confirmada", False,
         validate_schema(worker_return("JAVA_SPRING", assumptions=[{
             "locator": "X.java:2", "claim": "assumindo assinatura do repositorio"}]),
             schema, schema))
    case("SUPOSIÇÃO completa (aceita)", True,
         validate_schema(worker_return("JAVA_SPRING", assumptions=[assumption()]),
                         schema, schema))
    case("quarta tentativa de correção — Regra dos Três", False,
         validate_schema(worker_return("TESTES_DEPURACAO", fix_attempts=4), schema, schema))
    case("terceira tentativa sem causa raiz declarada", False,
         validate_schema(worker_return("TESTES_DEPURACAO", fix_attempts=3), schema, schema))
    case("terceira tentativa com causa raiz e pendência (aceita)", True,
         validate_schema(worker_return(
             "TESTES_DEPURACAO", fix_attempts=3,
             root_cause="o catch da violacao esta dentro da transacao rollback-only",
             pending=["escalar ao Diretor: modelo mental da falha estava errado"]),
             schema, schema))
    case("retorno BLOCKED sem motivo", False,
         validate_schema(worker_return("TAURI_DESKTOP", status="BLOCKED", artifacts=[],
                                       ladder=[]), schema, schema))

    # --- G. Negativos: livro-razão ------------------------------------------
    for borda in ("vazio", "limite", "erro"):
        case(f"ENTREGUE com a borda {borda} descoberta", False,
             validate_schema(ledger(edges=[edge(**{borda: False,
                 "justificativa_ausencia": "sem motivo real, so pressa de entregar"})]),
                 schema, schema))
    case("ENTREGUE com FAIL na bateria", False,
         validate_schema(ledger(test_evidence=evidence(fail=2)), schema, schema))
    case("ENTREGUE sem revisão independente", False,
         validate_schema(ledger(reviewed=False), schema, schema))
    case("ENTREGUE sem registro de emissão", False,
         validate_schema(ledger(assignments=[]), schema, schema))
    case("ENTREGUE com pendência pendurada", False,
         validate_schema(ledger(pending=["falta confirmar a assinatura do repo"]),
                         schema, schema))
    case("lacuna aberta sem bloquear a entrega", False,
         validate_schema(ledger(capability_gaps=[capability_gap()]), schema, schema))
    case("lacuna aberta com entrega BLOQUEADA (aceito)", True,
         validate_schema(ledger(capability_gaps=[capability_gap()], entrega="BLOQUEADA"),
                         schema, schema))
    case("entrega INCOMPLETA com borda aberta (aceita)", True,
         validate_schema(ledger(entrega="INCOMPLETA", edges=[edge(
             limite=False, justificativa_ausencia="limite depende de dado real ausente")]),
             schema, schema))
    case("livro-razão devolvido para fora do Diretor", False,
         validate_schema(ledger(return_to="ceo-maestro"), schema, schema))

    # --- H. Fronteira com o consumidor --------------------------------------
    dept_return = to_department_return(ledger())
    case("Diretor aceita o DEPARTMENT_RETURN com número real de teste", True,
         validate_schema(dept_return, director["$defs"]["departmentReturn"], director))
    forjado = copy.deepcopy(dept_return)
    forjado["returned_by"] = "departamento-arquitetura-dados"
    case("Diretor rejeita autor divergente do produtor", False,
         validate_schema(forjado, director["$defs"]["departmentReturn"], director))
    op_enum = director["$defs"]["operationalDepartment"]["enum"]
    check("Diretor reconhece este Departamento como operacional", DEPARTMENT in op_enum)
    check("Diretor reconhece este Departamento como produtor causal",
          DEPARTMENT in json.dumps(director["$defs"].get("knownCapability", {}),
                                   ensure_ascii=False))
    for viz, campo in (("departamento-arquitetura-dados", "delegationTarget"),
                       ("departamento-arquitetura-software", "delegationTarget")):
        p = OPERATIONS_ROOT / viz / "schemas" / f"{viz}.schema.json"
        check(f"{viz} delega para cá",
              p.is_file() and DEPARTMENT in json.dumps(
                  json.loads(p.read_text(encoding="utf-8"))["$defs"][campo],
                  ensure_ascii=False),
              f"{viz} não aponta para {DEPARTMENT}")

    # --- I. Recalculado em código -------------------------------------------
    check("gate fecha com bordas cobertas, bateria verde e revisão feita", gate_fecha(ledger()))
    for borda in ("vazio", "limite", "erro"):
        check(f"gate não fecha com a borda {borda} descoberta",
              not gate_fecha(ledger(edges=[edge(**{borda: False})])))
    check("gate não fecha com FAIL", not gate_fecha(ledger(test_evidence=evidence(fail=1))))
    check("gate não fecha sem revisão", not gate_fecha(ledger(reviewed=False)))
    check("gate não fecha sem registro de emissão", not gate_fecha(ledger(assignments=[])))
    check("gate não fecha com lacuna aberta",
          not gate_fecha(ledger(capability_gaps=[capability_gap()])))
    check("prova de outra versão não é fresca",
          not prova_fresca(ledger(test_evidence=evidence(against_digest=DIG))))
    check("prova contra o candidato entregue é fresca", prova_fresca(ledger()))
    check("gate não fecha com prova de outra versão",
          not gate_fecha(ledger(test_evidence=evidence(against_digest=DIG))))
    check("gate não fecha se quem executou não é o agente de testes",
          not gate_fecha(ledger(test_evidence=evidence(executed_by="agente-web-frontend"))))
    check("seis capacidades implementam e duas verificam",
          len(IMPLEMENTA) == 6 and len(AGENT_CAPABILITY) - len(IMPLEMENTA) == 2)
    check("os cinco inegociáveis estão no enum do schema",
          sorted(schema["$defs"]["inegociavel"]["enum"]) == sorted(INEGOCIAVEIS))
    check("os cinco tracks estão no enum do schema",
          len(schema["$defs"]["track"]["enum"]) == 5)

    # --- J. Missao de entrada (CRIT-02 / SURPRESAS_BYPASS) -------------------
    check("literal BLOCKED_BYPASS_ATTEMPT existe no validador",
          "BLOCKED_BYPASS_ATTEMPT" in Path(__file__).read_text(encoding="utf-8"))
    check("schema local trava producer de entrada no Diretor",
          find_const(schema, "producer", "diretor-de-lentes"))
    check("DEPARTMENT_MISSION de entrada com producer alheio é BLOCKED_BYPASS_ATTEMPT",
          mission_verdict(director_mission(schema, causal_over={"producer": "ceo-maestro"}),
                          contract_digest=DIG, schema=schema) == "BLOCKED_BYPASS_ATTEMPT")
    check("DEPARTMENT_MISSION com return_to fora do Diretor é BLOCKED_BYPASS_ATTEMPT",
          mission_verdict(director_mission(schema, return_to="ceo-maestro"),
                          contract_digest=DIG, schema=schema) == "BLOCKED_BYPASS_ATTEMPT")
    check("DEPARTMENT_MISSION íntegra do Diretor é ACEITA",
          mission_verdict(director_mission(schema), contract_digest=DIG,
                          schema=schema) == "ACEITA")
    case("schema local rejeita DEPARTMENT_MISSION de entrada com producer forjado", False,
         validate_schema(director_mission(schema, causal_over={"producer": "ceo-maestro"}),
                         schema["$defs"]["departmentMissionAdmission"], schema))
    case("schema local aceita DEPARTMENT_MISSION de entrada do Diretor", True,
         validate_schema(director_mission(schema),
                         schema["$defs"]["departmentMissionAdmission"], schema))

    # --- Catálogo ------------------------------------------------------------
    cat = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    cs = cat.get("cases", [])
    check("catálogo tem ao menos 12 casos", len(cs) >= 12, f"{len(cs)} casos")
    check("todo caso declara acionou e aderiu",
          all({"acionou", "aderiu"} <= set(c) for c in cs))
    check("catálogo separa casos de PORTÃO e de OPERAÇÃO",
          {c.get("tipo") for c in cs} == {"PORTAO", "OPERACAO"},
          "a separação responde ao defeito de instrumento de 2026-07-26")
    check("há ao menos quatro casos de operação",
          sum(1 for c in cs if c.get("tipo") == "OPERACAO") >= 4)
    case("digest da fonte normativa confere com o declarado em ORIGEM.md", True,
         conferir_digest_das_regras(RULES_PATH))
    case("digest do próprio schema confere com o declarado", True,
         conferir_digest_declarado(SCHEMA_PATH, SCHEMA_DIGEST_DECLARADO,
                                   "schema do pacote"))

    failures = 0
    for name, expected, errors in cases:
        actual = not errors
        ok = actual == expected
        print(f"[{'PASS' if ok else 'FAIL'}] {name} — esperado "
              f"{'válido' if expected else 'rejeitado'}")
        if not ok:
            failures += 1
            for e in errors:
                print(f"       {e}")
            if not errors:
                print("       caso inválido foi aceito sem erro")
    print(f"\nResultado: {len(cases) - failures}/{len(cases)} casos passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    # T55: recusa medir a Estrutura a partir do runtime, onde a raiz
    # resolve para .claude/skills e as skills do Catalogo viram pacotes.
    recusar_execucao_fora_da_fonte(STRUCTURE_ROOT)
    sys.exit(run())
