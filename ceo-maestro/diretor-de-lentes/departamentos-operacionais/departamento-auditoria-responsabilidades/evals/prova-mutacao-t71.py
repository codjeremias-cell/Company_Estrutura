# -*- coding: utf-8 -*-
"""T71 — prova de mutação. Verde é pergunta; vermelho sob mutação é resposta.

Cada mutação desfaz UMA das travas desta frente e roda a bateria inteira. A trava
só conta como trava se a bateria ficar VERMELHA — e a saída nomeia QUAIS casos
caíram, porque "ficou vermelho" sem dizer onde já me enganou antes.

Os quatro arquivos são fotografados antes e restaurados depois de cada rodada, e a
restauração é conferida por SHA-256. Rodar da pasta do pacote da Auditoria.
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

PACOTE = pathlib.Path.cwd()
RAIZ = PACOTE.parents[3]
ALVOS = {
    "schema_aud": PACOTE / "schemas" / "departamento-auditoria-responsabilidades.schema.json",
    "schema_ceo": RAIZ / "ceo-maestro" / "schemas" / "ceo-maestro.schema.json",
    "validador": PACOTE / "evals" / "validate_workflow.py",
    "emissor": PACOTE / "scripts" / "emitir_governanca.py",
}
BATERIA = [sys.executable, str(PACOTE / "evals" / "validate_workflow.py")]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rodar():
    """Devolve (total, passaram, [rotulos que falharam])."""
    saida = subprocess.run(BATERIA, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=str(PACOTE)).stdout or ""
    caidos = re.findall(r"\[FAIL\] (.+?) —", saida)
    m = re.search(r"Resultado: (\d+)/(\d+)", saida)
    return (int(m.group(2)), int(m.group(1)), caidos) if m else (0, 0, ["BATERIA NAO CONCLUIU"] + caidos)


# ------------------------------------------------------------------ mutações
def m1_ledger_sem_gate():
    """Desfaz a exigência de painel independente no ramo COMPLIANT do ledger."""
    d = json.loads(ALVOS["schema_aud"].read_text(encoding="utf-8"))
    for c in d["$defs"]["auditLedger"]["allOf"]:
        if c.get("if", {}).get("properties", {}).get("internal_verdict", {}).get("const") == "REPROVADO":
            c["else"]["properties"].pop("panel", None)
    ALVOS["schema_aud"].write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")


def m2_ceo_sem_clausula():
    """Remove do envelope a cláusula que exige painel INDEPENDENTE."""
    d = json.loads(ALVOS["schema_ceo"].read_text(encoding="utf-8"))
    rel = d["$defs"]["governanceReport"]
    rel["allOf"] = [c for c in rel["allOf"]
                    if "panel_independence_status" not in (c.get("then", {}).get("required") or [])]
    ALVOS["schema_ceo"].write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")


def m3_ceo_chave_morta():
    """Rechaveia a cláusula nova em `governance_verdict` — o defeito da T83.

    A cláusula continua ESCRITA e continua parecendo certa numa leitura. Se a
    bateria ficar verde, a trava não distingue cláusula viva de cláusula morta.
    """
    d = json.loads(ALVOS["schema_ceo"].read_text(encoding="utf-8"))
    for c in d["$defs"]["governanceReport"]["allOf"]:
        if "panel_independence_status" in (c.get("then", {}).get("required") or []):
            c["if"] = {"properties": {"governance_verdict": {"const": "COMPLIANT"}},
                       "required": ["governance_verdict"]}
    ALVOS["schema_ceo"].write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")


def m4_derivador_sem_guarda():
    """Tira o guarda do painel vazio no derivador do validador: all([]) é True."""
    t = ALVOS["validador"].read_text(encoding="utf-8")
    novo = t.replace(
        '            if ledger["panel"]\n'
        '            and all(bool(item.get("independent")) for item in ledger["panel"])\n',
        '            if all(bool(item.get("independent")) for item in ledger["panel"])\n', 1)
    assert novo != t, "M4 não encontrou o guarda — mutação não aplicada"
    ALVOS["validador"].write_text(novo, encoding="utf-8", newline="\n")


def m5_emissor_sem_guarda():
    """O mesmo guarda, no EMISSOR — a função que a operação de fato chama."""
    t = ALVOS["emissor"].read_text(encoding="utf-8")
    novo = t.replace('    if not painel:\n        return "NAO_INDEPENDENTE"\n', "", 1)
    assert novo != t, "M5 não encontrou o guarda no emissor"
    ALVOS["emissor"].write_text(novo, encoding="utf-8", newline="\n")


def m6_fixture_do_ledger():
    """Vira a fixture do painel para False: o caso positivo tem de CAIR.

    Prova o outro lado — que os casos verdes acima passam pelo campo, e não
    apesar dele.
    """
    t = ALVOS["validador"].read_text(encoding="utf-8")
    i = t.index("def audit_ledger(")
    cabeca, cauda = t[:i], t[i:]
    novo = cabeca + cauda.replace('"independent": True', '"independent": False', 1)
    assert novo != t, "M6 não encontrou a fixture do ledger"
    ALVOS["validador"].write_text(novo, encoding="utf-8", newline="\n")


def m7_emissor_digita_o_valor():
    """O emissor para de CHAMAR o derivador e digita `INDEPENDENTE` no envelope.

    O helper continua no arquivo, correto e testado. Se a bateria ficar verde, a
    trava protege o helper e não a emissão.
    """
    t = ALVOS["emissor"].read_text(encoding="utf-8")
    novo = t.replace(
        '"panel_independence_status": derivar_independencia_do_painel(ledger["panel"]),',
        '"panel_independence_status": "INDEPENDENTE",', 1)
    assert novo != t, "M7 não encontrou a chamada no emissor"
    ALVOS["emissor"].write_text(novo, encoding="utf-8", newline="\n")


MUTACOES = [
    ("M1 ledger sem o gate de painel independente", m1_ledger_sem_gate),
    ("M2 envelope do CEO sem a cláusula de independência", m2_ceo_sem_clausula),
    ("M3 cláusula do CEO rechaveada em `governance_verdict` (defeito da T83)", m3_ceo_chave_morta),
    ("M4 derivador do validador sem o guarda do painel vazio", m4_derivador_sem_guarda),
    ("M5 emissor sem o guarda do painel vazio", m5_emissor_sem_guarda),
    ("M6 fixture do painel virada para independent=False", m6_fixture_do_ledger),
    ("M7 emissor digita INDEPENDENTE em vez de chamar o derivador", m7_emissor_digita_o_valor),
]


def main():
    guarda = pathlib.Path(tempfile.mkdtemp(prefix="t71-mutacao-"))
    antes = {}
    for nome, caminho in ALVOS.items():
        shutil.copy2(caminho, guarda / nome)
        antes[nome] = sha(caminho)

    total, ok, caidos = rodar()
    print(f"BASE (sem mutação): {ok}/{total}" + (f"  CAIDOS: {caidos}" if caidos else "  — verde"))
    if ok != total or total == 0:
        print("ABORTADO: a base não está verde; mutação sobre base vermelha não mede nada.")
        return 1
    print()

    veredito = []
    for rotulo, aplicar in MUTACOES:
        aplicar()
        total_m, ok_m, caidos_m = rodar()
        pegou = ok_m < total_m or total_m == 0
        veredito.append((rotulo, pegou, f"{ok_m}/{total_m}", caidos_m))
        print(f"{'PEGOU  ' if pegou else 'ESCAPOU'} {rotulo}")
        print(f"        {ok_m}/{total_m}" + (f" — caíram: {caidos_m}" if caidos_m else ""))
        for nome, caminho in ALVOS.items():
            shutil.copy2(guarda / nome, caminho)
            assert sha(caminho) == antes[nome], f"restauração falhou em {nome}"
    print()
    escaparam = [r for r, pegou, *_ in veredito if not pegou]
    print(f"RESUMO: {len(veredito) - len(escaparam)}/{len(veredito)} mutações pegas.")
    if escaparam:
        print("ESCAPARAM (a trava correspondente não decide):")
        for r in escaparam:
            print("  -", r)
    total_f, ok_f, _ = rodar()
    print(f"ÁRVORE RESTAURADA: {ok_f}/{total_f}")
    return 1 if escaparam else 0


if __name__ == "__main__":
    raise SystemExit(main())
