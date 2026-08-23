# -*- coding: utf-8 -*-
"""Prova de mutação da trava `validate_pendencia_tem_dono` (T71, `CA-01`/`GR-01`).

Mesma disciplina de `prova_mutacao_selo.py`: cada mutante desfaz UMA garantia e a
bateria da testemunha tem de ficar VERMELHA. Os arquivos são fotografados e
restaurados com conferência por SHA-256.

Um dos mutantes é do TETO e escapa por construção — está declarado, não escondido.

    PYTHONIOENCODING=utf-8 python _compartilhado/prova_mutacao_dono.py
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
VIZINHO = (RAIZ / "ceo-maestro" / "diretor-de-lentes" / "departamentos-operacionais"
           / "departamento-qa-usabilidade" / "evals" / "PLACAR.md")
RESULTADO = re.compile(r"(?i)^\s*resultado:\s*(\d+)\s*/\s*(\d+)", re.M)


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rodar():
    saida = subprocess.run([sys.executable, "evals/validate_workflow.py"], cwd=str(TESTEMUNHA),
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace").stdout or ""
    caidos = re.findall(r"\[FAIL\] (.+?) —", saida)
    m = RESULTADO.findall(saida)
    if not m:
        return 0, 0, ["BATERIA NAO CONCLUIU"] + caidos
    return int(m[-1][0]), int(m[-1][1]), caidos


def m1_apaga_uma_linha():
    """Some UMA linha da tabela de donos do vizinho — o item fica órfão."""
    t = VIZINHO.read_text(encoding="utf-8")
    novo = re.sub(r"(?m)^\| 2 \|.*\n", "", t, count=1)
    assert novo != t, "M1 não achou a linha do item 2"
    VIZINHO.write_text(novo, encoding="utf-8", newline="\n")


def m2_esvazia_a_celula():
    """A linha fica, e o dono some. Forma satisfeita, ninguém nomeado."""
    t = VIZINHO.read_text(encoding="utf-8")
    novo = re.sub(r"(?m)^\| 2 \| [^|]* \|", "| 2 |  |", t, count=1)
    assert novo != t, "M2 não achou a célula do item 2"
    VIZINHO.write_text(novo, encoding="utf-8", newline="\n")


def m3_trava_inerte():
    """A trava do dono devolve vazio sempre — pega pela trava da T84."""
    t = MODULO.read_text(encoding="utf-8")
    marca = ('    if not structure_root.is_dir():\n'
             '        return [f"pendência sem dono: raiz da estrutura ausente em {structure_root}"]')
    assert marca in t
    MODULO.write_text(t.replace(marca, marca + "\n    return []", 1),
                      encoding="utf-8", newline="\n")


def m4_fora_das_obrigatorias():
    """O nome sai de FUNCOES_OBRIGATORIAS — pega pelo piso da T84."""
    t = MODULO.read_text(encoding="utf-8")
    i = t.index("FUNCOES_OBRIGATORIAS = (")
    f = t.index(")", i)
    marca = '    "validate_pendencia_tem_dono",\n'
    tupla = t[i:f]
    assert marca in tupla
    MODULO.write_text(t[:i] + tupla.replace(marca, "", 1) + t[f:],
                      encoding="utf-8", newline="\n")


def m5_autoteste_desligado():
    """O autoteste da trava para de ser somado — pega pela trava da T84."""
    t = MODULO.read_text(encoding="utf-8")
    marca = "    erros = _autoteste_do_dono()\n"
    assert marca in t
    MODULO.write_text(t.replace(marca, "    _autoteste_do_dono()\n    erros = []\n", 1),
                      encoding="utf-8", newline="\n")


def m6_detector_cego_a_bullets():
    """O TETO desta trava, e ele é de MEDIDA, não de mecanismo.

    O detector conta item numerado E item em traço porque a casa usa os dois — e
    descobrir isso custou dois falsos negativos nesta frente. Mas se alguém
    escrever pendência num formato que ele não conhece — tabela, parágrafo solto,
    lista com outro marcador —, ela não é contada e não é cobrada.

    O mutante troca `-` por `+` no marcador do vizinho. Espera-se ESCAPAR: nenhuma
    trava aqui dentro sabe o que é uma pendência escrita de forma nova.
    """
    t = VIZINHO.read_text(encoding="utf-8")
    novo = re.sub(r"(?m)^- ", "+ ", t)
    assert novo != t, "M6 não achou item em traço"
    VIZINHO.write_text(novo, encoding="utf-8", newline="\n")


MUTANTES = [
    ("M1 linha da tabela de donos apagada", m1_apaga_uma_linha, [VIZINHO]),
    ("M2 celula do dono esvaziada", m2_esvazia_a_celula, [VIZINHO]),
    ("M3 trava do dono inerte", m3_trava_inerte, [MODULO]),
    ("M4 trava do dono fora de FUNCOES_OBRIGATORIAS", m4_fora_das_obrigatorias, [MODULO]),
    ("M5 autoteste do dono desligado", m5_autoteste_desligado, [MODULO]),
    ("M6 pendencia em formato desconhecido — TETO DECLARADO, espera-se ESCAPAR",
     m6_detector_cego_a_bullets, [VIZINHO]),
]
TETO_ESPERADO = {"M6 pendencia em formato desconhecido — TETO DECLARADO, espera-se ESCAPAR"}


def main() -> int:
    guarda = pathlib.Path(tempfile.mkdtemp(prefix="dono-mutacao-"))
    tocados = sorted({p for _, _, ps in MUTANTES for p in ps})
    antes = {}
    for i, p in enumerate(tocados):
        shutil.copy2(p, guarda / str(i))
        antes[p] = sha(p)

    ok, total, caidos = rodar()
    print(f"BASE (testemunha {TESTEMUNHA.name}): {ok}/{total}"
          + (f"  CAIDOS: {caidos}" if caidos else "  — verde"))
    if ok != total or total == 0:
        print("ABORTADO: base vermelha não mede mutação nenhuma.")
        return 1
    print()

    escaparam = []
    for rotulo, aplicar, _ in MUTANTES:
        aplicar()
        ok_m, total_m, caidos_m = rodar()
        pegou = ok_m < total_m or total_m == 0
        if not pegou:
            escaparam.append(rotulo)
        print(f"{'PEGOU  ' if pegou else 'ESCAPOU'} {rotulo}")
        print(f"        {ok_m}/{total_m}" + (f" — caíram: {caidos_m}" if caidos_m else ""))
        for i, p in enumerate(tocados):
            shutil.copy2(guarda / str(i), p)
            assert sha(p) == antes[p], f"restauração falhou em {p}"

    print()
    inesperados = [r for r in escaparam if r not in TETO_ESPERADO]
    print(f"RESUMO: {len(MUTANTES) - len(escaparam)}/{len(MUTANTES)} mutantes pegos.")
    for r in escaparam:
        marca = "TETO CONFIRMADO" if r in TETO_ESPERADO else "ESCAPOU SEM EXPLICACAO"
        print(f"  {marca}: {r}")
    for r in TETO_ESPERADO - set(escaparam):
        print(f"  ATENCAO: o teto declarado NAO escapou — {r} — revise a declaracao")
    ok_f, total_f, _ = rodar()
    print(f"ARVORE RESTAURADA: {ok_f}/{total_f}")
    return 1 if inesperados else 0


if __name__ == "__main__":
    raise SystemExit(main())
