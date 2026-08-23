"""Sonda da T71 — em qual camada a independência do recibo pode virar condição.

NÃO é o conserto. É o instrumento que mediu a decisão de desenho: percorre as três
camadas (AUDIT_RECEIPT, AUDIT_LEDGER, governanceReport do CEO) e pergunta a cada uma
se ela RECUSA um veredito positivo quando a independência é falsa.

Rodar de dentro de:
  Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/
  departamento-auditoria-responsabilidades/evals/

  PYTHONIOENCODING=utf-8 python sonda_t71_camadas.py

Regra de leitura: toda mutação abaixo só significa alguma coisa porque a BASE
correspondente foi medida VÁLIDA antes. Base inválida transforma "REJEITADO" em ruído
— foi o que aconteceu na primeira corrida desta sonda, com digest fora do padrão.
"""

import copy
import importlib.util
import io
import json
import pathlib

import jsonschema

# A sonda se localiza pelo DIRETORIO DE TRABALHO (a pasta evals/ do pacote), e nao
# por __file__: assim ela roda igual estando no scratchpad ou ja canonizada em evals/.
AQUI = pathlib.Path.cwd().resolve()
PACOTE = AQUI.parent
RAIZ = PACOTE.parents[3]  # Estrutura Final de Skills
SCHEMA_AUDITORIA = PACOTE / "schemas" / "departamento-auditoria-responsabilidades.schema.json"
SCHEMA_CEO = RAIZ / "ceo-maestro" / "schemas" / "ceo-maestro.schema.json"
VALIDADOR = PACOTE / "evals" / "validate_workflow.py"


def _carregar_validador():
    spec = importlib.util.spec_from_file_location("vw_t71", VALIDADOR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _relatar(rotulo, erros):
    print(f"{rotulo:<58} -> {'ACEITO' if not erros else 'REJEITADO'}")
    for erro in erros[:2]:
        print("      .", list(erro.path), erro.message[:130])
    return not erros


def main() -> None:
    vw = _carregar_validador()
    auditoria = json.loads(SCHEMA_AUDITORIA.read_text(encoding="utf-8"))
    ceo = json.loads(SCHEMA_CEO.read_text(encoding="utf-8"))
    v_aud = jsonschema.Draft202012Validator(auditoria)

    relatorio = ceo["$defs"]["governanceReport"]
    sub = dict(relatorio)
    sub["$defs"] = ceo["$defs"]
    v_ceo = jsonschema.Draft202012Validator(sub)

    print("=== CAMADA 1 — AUDIT_RECEIPT (review_chain.independent) ===")
    recibo = vw.audit_receipt()
    _relatar("BASE do recibo", list(v_aud.iter_errors(recibo)))
    mut = copy.deepcopy(recibo)
    mut["review_chain"]["independent"] = False
    _relatar("independent=False SEM independence_notes", list(v_aud.iter_errors(mut)))
    mut["review_chain"]["independence_notes"] = (
        "o revisor leu o rascunho do outro inspetor na mesma pasta, medido na sessao"
    )
    _relatar("independent=False COM independence_notes", list(v_aud.iter_errors(mut)))

    print()
    print("=== CAMADA 2 — AUDIT_LEDGER (panel[].independent) ===")
    ledger = vw.audit_ledger()
    print(f"      fixture: internal_verdict={ledger['internal_verdict']} "
          f"governance_verdict={ledger['governance_verdict']}")
    _relatar("BASE do ledger", list(v_aud.iter_errors(ledger)))
    mut = copy.deepcopy(ledger)
    for item in mut["panel"]:
        item["independent"] = False
    _relatar("COMPLIANT com TODO o painel independent=False", list(v_aud.iter_errors(mut)))
    controle = copy.deepcopy(ledger)
    controle["candidate_identity"]["status"] = "NAO_CONFERIDO"
    _relatar("CONTROLE: COMPLIANT com identidade NAO_CONFERIDO", list(v_aud.iter_errors(controle)))

    print()
    print("=== CAMADA 3 — governanceReport do CEO (envelope da barreira) ===")
    print("      carrega painel?", "panel" in relatorio.get("properties", {}))
    print("      additionalProperties:", relatorio.get("additionalProperties"))
    envelope = {
        "report_id": "GOV-REPORT-T71-SONDA",
        "auditor_ref": "departamento-auditoria-responsabilidades",
        "auditor_digest": "sha256:" + "0" * 64,
        "candidate_digest": "sha256:" + "0" * 64,
        "contract_digest": "sha256:" + "0" * 64,
        "rules_digest": "sha256:" + "0" * 64,
        "verdict": "COMPLIANT",
        "violations": [],
        "evidence_refs": ["evals/sonda-t71/README.md"],
        "issued_at": "2026-08-08T18:00:00-03:00",
        "pending": [c["contains"]["const"] for c in relatorio["properties"]["pending"]["allOf"]],
        "candidate_digest_source": "RECOMPUTADO",
        "candidate_identity_status": "CONFERIDO",
        "candidate_manifest_status": "CONFERIDO",
        # T71 — o escalar derivado do painel. Antes desta frente o campo nao
        # existia, e a BASE desta sonda passava sem ele.
        "panel_independence_status": "INDEPENDENTE",
        "compliance_claim": {
            "certifies": relatorio["properties"]["compliance_claim"]["properties"]["certifies"]["const"],
            "does_not_certify": relatorio["properties"]["compliance_claim"]["properties"]["does_not_certify"]["const"],
            "ceiling_ref": "R11",
            "source": "scripts/inspecao_executada.py::ALEGACAO_DO_COMPLIANT",
        },
    }
    _relatar("BASE do envelope", list(v_ceo.iter_errors(envelope)))
    for rotulo, campo, valor in [
        ("M1 identidade NAO_CONFERIDO", "candidate_identity_status", "NAO_CONFERIDO"),
        ("M2 digest DECLARADO_NAO_CONFERIDO", "candidate_digest_source", "DECLARADO_NAO_CONFERIDO"),
        ("M4 manifesto DIVERGENTE", "candidate_manifest_status", "DIVERGENTE"),
        ("M6 painel NAO_INDEPENDENTE", "panel_independence_status", "NAO_INDEPENDENTE"),
    ]:
        mut = copy.deepcopy(envelope)
        mut[campo] = valor
        _relatar(rotulo, list(v_ceo.iter_errors(mut)))
    mut = copy.deepcopy(envelope)
    mut["violations"] = ["violacao qualquer"]
    _relatar("M3 violations nao vazio", list(v_ceo.iter_errors(mut)))
    mut = copy.deepcopy(envelope)
    mut["governance_verdict"] = "COMPLIANT"
    _relatar("M5 envelope tenta carregar governance_verdict", list(v_ceo.iter_errors(mut)))


if __name__ == "__main__":
    main()
