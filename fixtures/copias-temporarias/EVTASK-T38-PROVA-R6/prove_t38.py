from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


PASTAS_FORA_DA_RODADA = {
    "candidatos", "instrumentos", "lab", "fontes", "saida-crua", "backup",
}


def _objetos_json(texto: str, ndjson: bool) -> list[object]:
    saida = []
    if ndjson:
        for linha in texto.splitlines():
            if linha.strip():
                try:
                    saida.append(json.loads(linha))
                except json.JSONDecodeError:
                    pass
        return saida
    try:
        saida.append(json.loads(texto))
    except json.JSONDecodeError:
        pass
    return saida


def _percorre(obj):
    if isinstance(obj, dict):
        yield obj
        for valor in obj.values():
            yield from _percorre(valor)
    elif isinstance(obj, list):
        for valor in obj:
            yield from _percorre(valor)


def tem_judge_assignment(arquivos):
    for nome, conteudo in arquivos:
        if not nome.endswith((".json", ".ndjson")):
            continue
        for raiz in _objetos_json(conteudo, nome.endswith(".ndjson")):
            for obj in _percorre(raiz):
                if obj.get("artifact_type") == "JUDGE_ASSIGNMENT":
                    return True
    return False


def _arquivos_da_rodada(pasta: Path):
    arquivos = []
    for caminho in pasta.rglob("*"):
        if PASTAS_FORA_DA_RODADA & set(caminho.parts):
            continue
        if not caminho.is_file() or caminho.suffix not in (".json", ".ndjson"):
            continue
        arquivos.append((caminho.name, caminho.read_text(encoding="utf-8")))
    return arquivos


def _houve_julgamento(pasta: Path) -> bool:
    for caminho in pasta.rglob("*"):
        if PASTAS_FORA_DA_RODADA & set(caminho.parts):
            continue
        nome = caminho.name.upper()
        if nome.startswith("PARECER") or "VEREDITO" in nome or "JUDGE-OPINION" in nome:
            return True
    return False


def rodadas_em_bypass(raiz_evals: Path):
    bypass = []
    if not raiz_evals.is_dir():
        return bypass
    for pasta in sorted(raiz_evals.iterdir()):
        if not pasta.is_dir() or pasta.name in PASTAS_FORA_DA_RODADA:
            continue
        if not _houve_julgamento(pasta):
            continue
        if not tem_judge_assignment(_arquivos_da_rodada(pasta)):
            bypass.append(pasta.name)
    return bypass


def install(candidate: str):
    global tem_judge_assignment, _houve_julgamento, rodadas_em_bypass
    if candidate == "cand-A":
        def tem_judge_assignment(arquivos):
            required = {"artifact_type", "assignment_id", "causal", "judge_id", "lens", "mode", "candidate_digest", "anonymized_candidate", "criteria", "rubric_ref", "contract_excerpt", "evidence_index", "forbidden_context", "instance", "write_path", "custody_copy", "return_to", "issued_at"}
            for nome, conteudo in arquivos:
                if not nome.endswith((".json", ".ndjson")):
                    continue
                for raiz in _objetos_json(conteudo, nome.endswith(".ndjson")):
                    for obj in _percorre(raiz):
                        if obj.get("artifact_type") == "JUDGE_ASSIGNMENT" and required <= obj.keys() and set(obj) <= required:
                            return True
            return False
    elif candidate == "cand-B":
        def tem_judge_assignment(arquivos):
            for nome, conteudo in arquivos:
                if not nome.endswith((".json", ".ndjson")):
                    continue
                for raiz in _objetos_json(conteudo, nome.endswith(".ndjson")):
                    for obj in _percorre(raiz):
                        if obj.get("artifact_type") != "JUDGE_ASSIGNMENT":
                            continue
                        try:
                            JUDGE_ASSIGNMENT_VALIDATOR.validate(obj)
                        except jsonschema.ValidationError:
                            continue
                        return True
            return False
    elif candidate == "cand-C":
        def _houve_julgamento(pasta: Path) -> bool:
            for caminho in pasta.rglob("*"):
                if PASTAS_FORA_DA_RODADA & set(caminho.parts):
                    continue
                nome = caminho.name.upper()
                partes = {parte.upper() for parte in caminho.parts}
                if (nome.startswith("PARECER") or "VEREDITO" in nome
                        or "JUDGE-OPINION" in nome
                        or "JUDGE-ASSIGNMENTS" in partes
                        or "JUDGE-ASSIGNMENT" in nome):
                    return True
            return False
    elif candidate == "cand-D":
        def rodadas_em_bypass(raiz_evals: Path):
            bypass = []
            if not raiz_evals.is_dir():
                return bypass
            for pasta in sorted(raiz_evals.iterdir()):
                if not pasta.is_dir() or pasta.name in PASTAS_FORA_DA_RODADA:
                    continue
                arquivos = _arquivos_da_rodada(pasta)
                tem_footprint_de_julgamento = any(
                    "JUDGE-ASSIGNMENT" in nome.upper()
                    or "JUDGE-ASSIGNMENTS" in str(pasta / nome).upper()
                    for nome, _ in arquivos
                )
                if not (_houve_julgamento(pasta) or tem_footprint_de_julgamento):
                    continue
                if not tem_judge_assignment(arquivos):
                    bypass.append(pasta.name)
            return bypass


def direct_cases():
    return {
        "T32-C1-rotulo-apenas": [("invalid.json", '{"artifact_type": "JUDGE_ASSIGNMENT"}')],
        "T32-C2-prosa-e-opiniao": [
            ("RELATORIO.md", "Estou operando em BLOCKED_BYPASS_ATTEMPT e julguei assim mesmo — sem JUDGE_ASSIGNMENT."),
            ("PARECER.json", json.dumps({"artifact_type": "JUDGE_OPINION", "razao": "sem JUDGE_ASSIGNMENT"})),
        ],
        "T32-C3-executive-mission": [("01-EXECUTIVE-MISSION.json", json.dumps({"artifact_type": "EXECUTIVE_MISSION", "handoff_id": "HANDOFF-1", "return_to": "ceo-maestro"}))],
        "T32-C4-opiniao-cita-assignment": [("PARECER.json", json.dumps({"artifact_type": "JUDGE_OPINION", "assignment_id": "ASSIGN-1"}))],
        "T32-C5-designacao-real": [("ASSIGN-T12R3-FID-I1.json", json.dumps({"artifact_type": "JUDGE_ASSIGNMENT", "assignment_id": "ASSIGN-T12R3-FID-I1", "judge_id": "agente-julgar-fidelidade-e-contrato"}))],
    }


def directory_cases(root: Path):
    cases = {}
    for case_id, with_veredito in (("T32-C6-sem-veredito", False), ("T32-C7-com-veredito", True)):
        case_root = root / case_id / "rodada"
        assignment_dir = case_root / "03-JUDGE-ASSIGNMENTS"
        assignment_dir.mkdir(parents=True)
        (assignment_dir / "invalid.json").write_text('{"artifact_type": "JUDGE_ASSIGNMENT"}', encoding="utf-8")
        if with_veredito:
            (case_root / "VEREDITO.md").write_text("veredito autorizado", encoding="utf-8")
        cases[case_id] = case_root
    return cases


def run(candidate: str):
    install(candidate)
    result = {"candidate": candidate, "direct": {}, "directory": {}}
    for case_id, arquivos in direct_cases().items():
        baseline = tem_judge_assignment(arquivos) if candidate == "__baseline__" else None
        observed = tem_judge_assignment(arquivos)
        result["direct"][case_id] = {"baseline": baseline, "observed": observed}
    with tempfile.TemporaryDirectory(prefix="t38-") as td:
        cases = directory_cases(Path(td))
        for case_id, case_root in cases.items():
            result["directory"][case_id] = {
                "houve": _houve_julgamento(case_root),
                "bypass": rodadas_em_bypass(Path(td) / case_id),
            }
    return result


def main():
    candidate = sys.argv[1]
    if candidate == "__baseline__":
        # Baseline is run in a fresh process for each candidate invocation.
        pass
    try:
        print(json.dumps(run(candidate), ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        print(json.dumps({"candidate": candidate, "error_type": type(exc).__name__, "error": str(exc)}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
