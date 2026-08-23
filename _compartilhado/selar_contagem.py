# -*- coding: utf-8 -*-
"""Regenera o **selo de contagem** dos pacotes canônicos da Estrutura.

O que o selo é
--------------
Uma linha, no `evals/PLACAR.md` de cada pacote, que liga três coisas que até
2026-08-08 viviam separadas: a **contagem**, o **digest do instrumento** que a
produziu e a **data** da corrida. É a condição corretiva literal do achado
`EA-01` da remedição de 2026-08-03 — *"fechada quando um terceiro reabrir o
PLACAR e conseguir ligar a contagem ao digest do instrumento vigente"*.

Por que um gerador e não a mão
------------------------------
Porque à mão já foi feito, e envelheceu nos quinze. Medido por execução em
2026-08-08, antes desta frente: dos 16 pacotes, 15 publicavam número próprio e
**os 15 estavam defasados** — `ceo-maestro` dizia 55/55 contra 148/148 vivos, a
Auditoria dizia 65/65 contra 175/175. Cada um esteve certo no dia em que foi
escrito. O que faltava não era cuidado: era um gerador e uma trava.

A trava é `validate_contagem_ligada_ao_instrumento`, em `FUNCOES_OBRIGATORIAS`.
Editar um validador sem regenerar o selo derruba a bateria do próprio pacote —
o número não consegue mais envelhecer em silêncio.

Passadas até PONTO FIXO, de propósito
------------------------------------
A trava varre a árvore inteira: um selo velho em **qualquer** pacote avermelha
os dezesseis. Então selar em uma passada não converge — enquanto o pacote 16
ainda não foi selado, a corrida do pacote 1 é vermelha, e o número que ela
mediria não é o que vai valer. Medido nesta frente: com passada única, 11 dos 16
ficaram com selo de corrida vermelha.

Por isso o laço externo: repete a varredura inteira até que uma passada não mude
mais nada e todos fechem verdes, ou até o teto de rodadas. Declarar como vigente
o resultado de uma corrida que a própria trava reprova seria publicar número
que já nasce falso.

Uso, a partir da raiz de `Estrutura Final de Skills`:

    PYTHONIOENCODING=utf-8 python _compartilhado/selar_contagem.py
    PYTHONIOENCODING=utf-8 python _compartilhado/selar_contagem.py --conferir
"""
from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from _compartilhado.validador_schema import sha256_texto_normalizado  # noqa: E402
from _compartilhado.verificacoes_estrutura import (  # noqa: E402
    SELO_DE_CONTAGEM,
    _validadores_canonicos,
)

# Os dois formatos de linha final em uso na casa. `departamento-negocios` imprime
# `RESULTADO: 235/235 PASS; 0 FAIL`, os demais `Resultado: 175/175 casos`.
RESULTADO = re.compile(r"(?i)^\s*resultado:\s*(\d+)\s*/\s*(\d+)", re.M)

ABRE = "<!-- SELO-DE-CONTAGEM -->"
FECHA = "<!-- /SELO-DE-CONTAGEM -->"
BLOCO = re.compile(re.escape(ABRE) + r".*?" + re.escape(FECHA) + r"\n?", re.S)

MOLDE = """{abre}
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: {ok}/{total} | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `{sha}` | medido-em: {data}
{fecha}
"""


def medir(pacote: Path) -> tuple[int | None, int | None]:
    saida = subprocess.run(
        [sys.executable, "evals/validate_workflow.py"], cwd=str(pacote),
        capture_output=True, text=True, encoding="utf-8", errors="replace").stdout or ""
    achados = RESULTADO.findall(saida)
    if not achados:
        return None, None
    return int(achados[-1][0]), int(achados[-1][1])


def gravar_selo(placar: Path, ok: int, total: int, sha: str, data: str) -> None:
    bloco = MOLDE.format(abre=ABRE, fecha=FECHA, ok=ok, total=total, sha=sha, data=data)
    texto = placar.read_text(encoding="utf-8")
    if BLOCO.search(texto):
        novo = BLOCO.sub(lambda _: bloco, texto, count=1)
    else:
        # Logo abaixo do título, onde quem abre o documento lê primeiro. O selo
        # precisa vir ANTES dos números antigos, ou o leitor encontra o velho.
        linhas = texto.split("\n")
        corte = next((i for i, l in enumerate(linhas) if l.startswith("# ")), -1) + 1
        while corte < len(linhas) and not linhas[corte].strip():
            corte += 1
        novo = "\n".join(linhas[:corte]) + "\n" + bloco + "\n" + "\n".join(linhas[corte:])
    placar.write_text(novo, encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    conferir = "--conferir" in argv
    hoje = datetime.date.today().isoformat()
    instrumentos = _validadores_canonicos(RAIZ)
    print(f"{len(instrumentos)} pacotes canonicos · {'CONFERINDO' if conferir else 'SELANDO'}")

    pendentes = []
    for instrumento in instrumentos:
        pacote = instrumento.parents[1]
        placar = pacote / "evals" / "PLACAR.md"
        if not placar.is_file():
            print(f"{pacote.name:44} SEM PLACAR.md"); pendentes.append(pacote.name); continue
        sha = sha256_texto_normalizado(instrumento)

        if conferir:
            m = SELO_DE_CONTAGEM.search(placar.read_text(encoding="utf-8"))
            estado = "SEM SELO" if not m else ("ok" if m.group(3) == sha else "SELO DE OUTRA VERSAO")
            if estado != "ok":
                pendentes.append(pacote.name)
            print(f"{pacote.name:44} {estado}")
            continue

        ok, total = medir(pacote)
        if total is None:
            print(f"{pacote.name:44} NAO CONCLUIU"); pendentes.append(pacote.name); continue
        gravar_selo(placar, ok, total, sha, hoje)
        print(f"{pacote.name:44} {ok}/{total}" + ("" if ok == total else "   (vermelho nesta passada)"))
        if ok != total:
            pendentes.append(pacote.name)

    print()
    print(f"PENDENTES: {pendentes if pendentes else 'nenhum'}")
    return 1 if pendentes else 0


TETO_DE_RODADAS = 5


def selar_ate_ponto_fixo() -> int:
    """Repete a varredura até a árvore parar de mudar. Ver o cabeçalho do módulo."""
    for rodada in range(1, TETO_DE_RODADAS + 1):
        print(f"\n===== rodada {rodada} =====")
        if main(["--selar-uma-passada"]) == 0:
            print(f"\nPONTO FIXO na rodada {rodada}: os 16 fecham verdes.")
            return 0
    print(f"\nNAO CONVERGIU em {TETO_DE_RODADAS} rodadas — ha defeito alem do selo.")
    return 1


if __name__ == "__main__":
    argumentos = sys.argv[1:]
    if "--conferir" in argumentos or "--selar-uma-passada" in argumentos:
        raise SystemExit(main(argumentos))
    raise SystemExit(selar_ate_ponto_fixo())
