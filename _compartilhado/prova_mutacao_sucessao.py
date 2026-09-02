# -*- coding: utf-8 -*-
"""Prova de mutacao da isencao por supersessao (NC-R4-04).

Mesma disciplina de `prova_mutacao_dono.py` e `prova_mutacao_selo.py`: cada
mutante desfaz UMA garantia do codigo de PRODUCAO e a bateria da testemunha tem
de ficar VERMELHA.

Por que esta prova existe, e por que ela e diferente da que roda na campanha:
o `19-provar-sucessao-e-ganha.py` da rodada do C13 muta os DADOS -- alegacoes
forjadas contra a arvore real. Isto aqui muta o CODIGO. As duas medem coisas
diferentes, e so a segunda responde "a condicao que eu escrevi tem efeito?".
Mutante que sobrevive aqui e uma condicao que ninguem cobra.

SOBREVIVENTE DECLARADO, no molde do `prova_mutacao_dono.py`: o
`relative_to(root)` dentro de `_envelope_em` NAO e morto por mutacao, e isso
esta dito aqui em vez de escondido. Ele so teria efeito se existisse um
envelope de governanca de VERDADE fora da arvore, e criar um durante a prova
mexeria na arvore medida. Ele e a ultima rede atras da regra de forma -- essa
sim exercitada, com um caminho que existe. Redundancia deliberada nao e
cobertura alegada.

HISTORICO QUE FICA: a primeira rodada desta prova matou 4 de 7. Os tres
sobreviventes -- `report_id`, ordem do `issued_at` e caminho -- nao revelaram
buraco na trava: revelaram buraco NO MEU AUTOTESTE. Cada caso casava DUAS
condicoes ao mesmo tempo e morria pela vizinha, entao a condicao que ele dizia
testar nunca era a que decidia. As fixtures `mesmo-report-id.json` e
`sucessor-limpo-antigo.json` existem para isolar uma condicao cada.

    PYTHONIOENCODING=utf-8 python _compartilhado/prova_mutacao_sucessao.py
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
MODULO = RAIZ / "_compartilhado" / "verificacoes_estrutura.py"
TESTEMUNHA = RAIZ / "ceo-maestro"
RESULTADO = re.compile(r"(?i)^\s*resultado:\s*(\d+)\s*/\s*(\d+)", re.M)

# Cada mutante: (nome, trecho a substituir, substituto, o que soltaria).
# Um trecho que nao case e ERRO, nao mutante morto -- mutante que nunca foi
# aplicado nao prova nada, e e a armadilha que faz uma bateria inteira parecer
# verde por engano.
MUTANTES: list[tuple[str, str, str, str]] = [
    (
        "isencao sem conferencia alguma",
        '    if not isinstance(alegacao, dict):\n'
        '        return ["SUCESSAO_INVALIDA: %s - entrada que nao e objeto" % origem]',
        "    return []\n"
        '    if not isinstance(alegacao, dict):\n'
        '        return ["SUCESSAO_INVALIDA: %s - entrada que nao e objeto" % origem]',
        "qualquer alegacao isentaria qualquer envelope",
    ),
    (
        "campos que ligam deixam de ser conferidos",
        "    for campo in _CAMPOS_QUE_LIGAM_A_SUCESSAO:\n"
        "        if superado.get(campo) != sucessor.get(campo):",
        "    for campo in ():\n"
        "        if superado.get(campo) != sucessor.get(campo):",
        "qualquer envelope limpo da arvore viraria alibi de qualquer sujo",
    ),
    (
        "report_id igual deixa de ser conferido",
        '    if superado.get("report_id") == sucessor.get("report_id"):',
        '    if False and superado.get("report_id") == sucessor.get("report_id"):',
        "um envelope sujo sucederia a si mesmo e sairia limpo",
    ),
    (
        "ordem do issued_at deixa de ser conferida",
        "    if not (isinstance(velho, str) and isinstance(novo, str) and novo > velho):",
        "    if False:",
        "sucessao andaria para tras: o limpo seria superado pelo sujo",
    ),
    (
        "sucessor SUJO deixa de ser conferido",
        '    sujo = achar_limite_sem_dono(sucessor.get("pending"), "%s (sucessor)" % origem)',
        "    sujo = []",
        "a obrigacao desapareceria em vez de mudar de envelope",
    ),
    (
        "regra de forma do caminho deixa de valer",
        "    if not _caminho_de_sucessao_e_bem_formado(relativo):\n"
        "        return None",
        "    if False:\n"
        "        return None",
        "a alegacao escolheria por onde andar: `..` e caminho absoluto",
    ),
    (
        "a trava deixa de consultar o registro de sucessao",
        "        if origem in isentos:",
        "        if False and origem in isentos:",
        "nada -- este mutante prova o CONTRARIO: a consulta tem efeito, porque"
        " sem ela o envelope superado volta a ser cobrado",
    ),
]


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def roda_testemunha() -> tuple[int, int, int]:
    """(passaram, total, returncode) da bateria do ceo-maestro."""
    saida = subprocess.run(
        [sys.executable, "evals/validate_workflow.py"],
        cwd=str(TESTEMUNHA),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
    )
    casado = RESULTADO.search(saida.stdout or "")
    if not casado:
        return (-1, -1, saida.returncode)
    return (int(casado.group(1)), int(casado.group(2)), saida.returncode)


def main() -> int:
    original = MODULO.read_text(encoding="utf-8")
    digest_antes = sha(MODULO)
    falhas: list[str] = []

    print("=" * 78)
    print("PROVA DE MUTACAO -- isencao por supersessao (NC-R4-04)")
    print("=" * 78)
    base_p, base_t, base_rc = roda_testemunha()
    print("BASE (sem mutacao): %s/%s  exit=%s" % (base_p, base_t, base_rc))
    if base_p != base_t or base_rc != 0:
        print("  BASE JA ESTA VERMELHA -- mutacao sobre casa suja nao prova nada.")
        return 1

    mortos = 0
    try:
        for nome, de, para, solta in MUTANTES:
            if original.count(de) != 1:
                falhas.append(
                    "MUTANTE NAO APLICADO: %s -- o trecho aparece %d vez(es), nao 1."
                    " Mutante que nunca rodou nao e mutante morto" % (nome, original.count(de))
                )
                print("  [NAO APLICADO] %s" % nome)
                continue
            MODULO.write_text(original.replace(de, para, 1), encoding="utf-8", newline="\n")
            p, t, rc = roda_testemunha()
            MODULO.write_text(original, encoding="utf-8", newline="\n")
            vermelho = (p != t) or (rc != 0) or p < 0
            if vermelho:
                mortos += 1
                print("  [MORTO]      %-52s %s/%s" % (nome, p, t))
            else:
                falhas.append("MUTANTE SOBREVIVEU: %s -- soltaria: %s" % (nome, solta))
                print("  [SOBREVIVEU] %-52s %s/%s  <<<<" % (nome, p, t))
    finally:
        MODULO.write_text(original, encoding="utf-8", newline="\n")

    if sha(MODULO) != digest_antes:
        falhas.append(
            "RESTAURACAO FALHOU: o modulo nao voltou byte a byte ao original."
            " Prova que altera a arvore medida e pior que prova nenhuma"
        )
    else:
        print("\nmodulo restaurado byte a byte (sha256:%s)" % digest_antes[:16])

    p, t, rc = roda_testemunha()
    print("BASE apos restaurar: %s/%s  exit=%s" % (p, t, rc))
    if (p, t, rc) != (base_p, base_t, base_rc):
        falhas.append("a bateria nao voltou ao placar da base")

    print()
    print("MUTACAO: %d de %d mortos" % (mortos, len(MUTANTES)))
    if falhas:
        print("VEREDITO: NAO PROVADO")
        for f in falhas:
            print("  -", f)
        return 1
    print("VEREDITO: toda condicao da isencao tem efeito medido na cadeia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
