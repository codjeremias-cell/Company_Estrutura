# -*- coding: utf-8 -*-
"""Prova de mutação da trava do selo de contagem (T71, achado `EA-01`).

Cada mutante desfaz UMA garantia e roda a bateria de um pacote-testemunha. A
trava só conta como trava se a bateria ficar VERMELHA — e a saída nomeia quais
casos caíram, porque "ficou vermelho" sem dizer onde já enganou esta casa antes.

Os arquivos tocados são fotografados e restaurados, com conferência por SHA-256.

    PYTHONIOENCODING=utf-8 python _compartilhado/prova_mutacao_selo.py
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
MODULO = RAIZ / "_compartilhado" / "verificacoes_estrutura.py"
TESTEMUNHA = (RAIZ / "ceo-maestro" / "diretor-de-lentes" / "departamentos-operacionais"
              / "departamento-auditoria-responsabilidades")
VIZINHO = RAIZ / "ceo-maestro" / "departamento-evolucao-skills"
RESULTADO = re.compile(r"(?i)^\s*resultado:\s*(\d+)\s*/\s*(\d+)", re.M)


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rodar(pacote: pathlib.Path):
    saida = subprocess.run([sys.executable, "evals/validate_workflow.py"], cwd=str(pacote),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace").stdout or ""
    caidos = re.findall(r"\[FAIL\] (.+?) —", saida)
    m = RESULTADO.findall(saida)
    if not m:
        return 0, 0, ["BATERIA NAO CONCLUIU"] + caidos
    return int(m[-1][0]), int(m[-1][1]), caidos


# --------------------------------------------------------------------- mutantes
def m1_apaga_selo():
    """O selo some do placar do vizinho — é a ausência que a trava nomeia."""
    placar = VIZINHO / "evals" / "PLACAR.md"
    t = placar.read_text(encoding="utf-8")
    novo = "\n".join(l for l in t.split("\n") if not l.startswith("CONTAGEM-VIGENTE:"))
    assert novo != t
    placar.write_text(novo, encoding="utf-8", newline="\n")


def m2_selo_de_outra_versao():
    """O selo fica, com o digest de outra versão: é a prova envelhecida."""
    placar = VIZINHO / "evals" / "PLACAR.md"
    t = placar.read_text(encoding="utf-8")
    novo = re.sub(r"sha256-normalizado: `sha256:[a-f0-9]{64}`",
                  "sha256-normalizado: `sha256:" + "b" * 64 + "`", t, count=1)
    assert novo != t
    placar.write_text(novo, encoding="utf-8", newline="\n")


def m3_edita_validador_sem_reselar():
    """O caso REAL: alguém muda o validador e não regenera o selo."""
    alvo = VIZINHO / "evals" / "validate_workflow.py"
    alvo.write_text(alvo.read_text(encoding="utf-8") + "\n# comentario novo\n",
                    encoding="utf-8", newline="\n")


def m4_trava_inerte():
    """A trava devolve vazio sempre — presença sem efeito, no módulo COMPARTILHADO."""
    t = MODULO.read_text(encoding="utf-8")
    marca = '    if not structure_root.is_dir():\n        return [f"contagem ligada ao instrumento: raiz ausente em {structure_root}"]'
    assert marca in t
    MODULO.write_text(t.replace(marca, marca + "\n    return []", 1),
                      encoding="utf-8", newline="\n")


def m5_autoteste_desligado():
    """O autoteste do selo para de ser somado — a trava deixa de se provar."""
    t = MODULO.read_text(encoding="utf-8")
    marca = "    erros.extend(_autoteste_do_selo(motor))"
    assert marca in t
    MODULO.write_text(t.replace(marca, "    _autoteste_do_selo(motor)", 1),
                      encoding="utf-8", newline="\n")


def m6_fora_das_obrigatorias():
    """A trava sai de FUNCOES_OBRIGATORIAS: ninguém é mais obrigado a chamá-la.

    Tira só da PRIMEIRA tupla — que é `FUNCOES_OBRIGATORIAS`, definida antes do
    piso. É exatamente a edição de um lugar só que o piso da T84 passou a cobrar.
    """
    t = MODULO.read_text(encoding="utf-8")
    inicio = t.index("FUNCOES_OBRIGATORIAS = (")
    fim = t.index(")", inicio)
    marca = '    "validate_contagem_ligada_ao_instrumento",\n'
    tupla = t[inicio:fim]
    assert marca in tupla, "o nome nao esta na tupla das obrigatorias"
    MODULO.write_text(t[:inicio] + tupla.replace(marca, "", 1) + t[fim:],
                      encoding="utf-8", newline="\n")


def m7_trava_irma_inerte():
    """A trava da T34, ALHEIA a esta frente, fica inerte.

    É o que prova que o conserto da T84 vale para as cinco obrigatórias e não só
    para a que a descobriu. Antes da T84 este mutante escapava.
    """
    t = MODULO.read_text(encoding="utf-8")
    marca = "    return _autoteste_da_cadeia() + _varrer_declaradores(structure_root.resolve())"
    assert marca in t
    MODULO.write_text(t.replace(marca, "    return []", 1), encoding="utf-8", newline="\n")


def m8_o_proprio_vigia_inerte():
    """O TETO, e ele é publicado em vez de escondido.

    Neutralizar `validate_travas_compartilhadas_com_efeito` — quem confere as
    outras — não é pego por nada aqui dentro: quem confereria é ela mesma. Este
    mutante existe para que o limite seja MEDIDO e apareça no relatório, não para
    passar. Fechá-lo exige executor externo ao pacote (tarefas 50 e 57).
    """
    t = MODULO.read_text(encoding="utf-8")
    marca = '    erros: list[str] = []\n\n    faltando = sorted(set(PISO_DE_FUNCOES_OBRIGATORIAS)'
    assert marca in t
    MODULO.write_text(t.replace(marca, "    return []\n" + marca, 1),
                      encoding="utf-8", newline="\n")


MUTANTES = [
    ("M1 selo apagado do placar do vizinho", m1_apaga_selo, [VIZINHO / "evals" / "PLACAR.md"]),
    ("M2 selo com digest de outra versão", m2_selo_de_outra_versao, [VIZINHO / "evals" / "PLACAR.md"]),
    ("M3 validador editado sem reselar (caso real)", m3_edita_validador_sem_reselar,
     [VIZINHO / "evals" / "validate_workflow.py"]),
    ("M4 trava inerte (devolve vazio sempre)", m4_trava_inerte, [MODULO]),
    ("M5 autoteste do selo desligado", m5_autoteste_desligado, [MODULO]),
    ("M6 trava fora de FUNCOES_OBRIGATORIAS", m6_fora_das_obrigatorias, [MODULO]),
    ("M7 trava IRMA (T34) inerte — vale para as cinco?", m7_trava_irma_inerte, [MODULO]),
    ("M8 o proprio vigia inerte — TETO DECLARADO, espera-se ESCAPAR", m8_o_proprio_vigia_inerte, [MODULO]),
]

# O M8 nao e falha: e o teto medido. Quem confere as obrigatorias e uma delas, e
# o laco nao fecha de dentro. Publicar o custo da forja vale mais do que uma taxa
# de aprovacao que esconde o que sobrou aberto.
TETO_ESPERADO = {"M8 o proprio vigia inerte — TETO DECLARADO, espera-se ESCAPAR"}


def main() -> int:
    guarda = pathlib.Path(tempfile.mkdtemp(prefix="selo-mutacao-"))
    tocados = sorted({p for _, _, ps in MUTANTES for p in ps})
    antes = {}
    for i, p in enumerate(tocados):
        shutil.copy2(p, guarda / f"{i}")
        antes[p] = sha(p)

    ok, total, caidos = rodar(TESTEMUNHA)
    print(f"BASE (testemunha {TESTEMUNHA.name}): {ok}/{total}"
          + (f"  CAIDOS: {caidos}" if caidos else "  — verde"))
    if ok != total or total == 0:
        print("ABORTADO: base vermelha não mede mutação nenhuma.")
        return 1
    print()

    escaparam = []
    for rotulo, aplicar, _ in MUTANTES:
        aplicar()
        ok_m, total_m, caidos_m = rodar(TESTEMUNHA)
        pegou = ok_m < total_m or total_m == 0
        if not pegou:
            escaparam.append(rotulo)
        print(f"{'PEGOU  ' if pegou else 'ESCAPOU'} {rotulo}")
        print(f"        {ok_m}/{total_m}" + (f" — caíram: {caidos_m}" if caidos_m else ""))
        for i, p in enumerate(tocados):
            shutil.copy2(guarda / f"{i}", p)
            assert sha(p) == antes[p], f"restauração falhou em {p}"
    print()
    inesperados = [r for r in escaparam if r not in TETO_ESPERADO]
    teto_confirmado = [r for r in escaparam if r in TETO_ESPERADO]
    nao_escapou_o_teto = [r for r in TETO_ESPERADO if r not in escaparam]
    print(f"RESUMO: {len(MUTANTES) - len(escaparam)}/{len(MUTANTES)} mutantes pegos.")
    for r in teto_confirmado:
        print("  TETO CONFIRMADO (escapar era o esperado):", r)
    for r in inesperados:
        print("  ESCAPOU SEM EXPLICACAO:", r)
    for r in nao_escapou_o_teto:
        print("  ATENCAO: o teto declarado NAO escapou —", r,
              "— revise a declaracao do limite antes de comemorar")
    ok_f, total_f, _ = rodar(TESTEMUNHA)
    print(f"ÁRVORE RESTAURADA: {ok_f}/{total_f}")
    return 1 if inesperados else 0


if __name__ == "__main__":
    raise SystemExit(main())
