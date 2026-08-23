"""Inspeção **executada** sob porta única — a trava, em código.

Fonte única do que separa *auditar* de *dizer que auditou*. Consumida pelo
emissor real (`emitir_governanca.py`, que produz o `GOVERNANCE_REPORT` que o CEO
lê) e pelo validador de regressão do pacote. Não há terceira cópia.

Por que este arquivo existe
---------------------------
A Estrutura foi implantada como **porta única**: só `ceo-maestro` registra como
skill invocável. Medido em 2026-08-01: 58 skills em profundidade ≤2, 81
`SKILL.md` aninhados, e **0** `agente-*` que resolvem. Os três agentes inspetores
da Auditoria existem em disco como contrato e não são alcançáveis.

O protocolo antigo lia isso como `MISSING` → sem `AUDIT_TASK` → `SEM_RETORNO` →
`AUDIT_CAPABILITY_GAP` → dez dimensões `NAO_PROVADO` → `REPROVADO` →
`NONCOMPLIANT`. A barreira do CEO exige `governance_report COMPLIANT`. Logo
**nenhum candidato jamais fechava** — o gate era insatisfazível por construção,
e as duas attempts da tarefa 11 e a tarefa 14 mediram isso três vezes.

O que muda, e o que **não** muda
--------------------------------
Muda a **unidade de inspeção**: sob porta única, "agente" é o *papel* que a
gerente desempenha lendo o contrato do agente. O
`CONTRATO-DE-COMPROMISSO.md` do agente deixa de ser o endereço de uma capacidade
e passa a ser o **método** da inspeção. O contrato do agente **não é alterado** —
o método é o mesmo; muda quem o executa.

Não muda a recusa. `NAO_PROVADO` continua bloqueando, e continua sendo o destino
de toda dimensão sem inspeção executada. O que este módulo **proíbe** é a única
saída fácil que a redefinição abriria: `COMPLIANT` por afirmação da gerente.

A régua é mecânica e mais dura que a anterior
---------------------------------------------
O recibo antigo pedia `evidence_refs` — identificadores opacos (`"evidence-01"`)
que **nada** reabria. O recibo novo pede **âncora**: arquivo, linha, citação
literal e digest do arquivo. Um terceiro reabre o arquivo, vai à linha e compara
a citação. Âncora que não reabre não sustenta estado.

Por isso `COMPLIANT` ficou alcançável **sem afrouxar**: ele parou de depender de
um recurso de runtime que não existe e passou a depender de trabalho verificável.
A barra subiu — antes bastava um identificador; agora é preciso citar o byte.

Limite declarado — reduzido em 2026-08-01 ao que a medição sustenta
-------------------------------------------------------------------
A rodada 1 desta correção afirmava que a âncora prova inspeção "sobre o artefato
**certo**". Os Juízes mostraram que isso excede o que o código confere: a sonda
`P2` fechou `COMPLIANT` com `INTENT` ancorada num arquivo real **sem relação
nenhuma** com a dimensão. A alegação correta, e é a que vale aqui:

> A âncora prova que **um arquivo da raiz auditada foi reaberto na versão
> declarada**, e que a citação está mesmo naquela linha.

Ela **não** liga a dimensão ao artefato que deveria sustentá-la. Pertinência da
evidência é mérito, e mérito é dos Juízes (R5 do protocolo). Este limite é
nomeado em `pending` como `R9`, em toda emissão, exatamente como `R6`. (Viajava
como `R8` até a rodada 3, e colidia com o `R8` do §7 do protocolo, que é *bypass
para fora*; esta linha ainda dizia `R8` no candidato da rodada 3 e é corrigida
aqui.)

E `R6` segue valendo por inteiro: tudo é escrito pela própria gerente. A frase
que estava aqui — *"a âncora encarece **muito** a fabricação"* — foi **retirada
na rodada 5**, porque a medição a desmentiu: `OI-04` fabricou recibos íntegros,
que reabrem, em 80 linhas e 0,031 s, com uma tentativa. O que a âncora custa está
medido, e o número substitui o advérbio.

Rodada 4 — contar, nunca ler
----------------------------
O julgamento da rodada 3 achou o nível 6 do mesmo defeito de sempre: **o valor é
declarado onde deveria ser derivado**. `anchors_total` era **lido** de um
dicionário que atravessava o emissor; uma função intermediária que devolvesse
números fabricados mantinha a cadeia de nomes intacta, e o emissor gravava
`COMPLIANT` com `anchors_total: 12` sobre recibos com **zero âncoras**. Medido
pelos Juízes, reproduzido em `prova-r4/40-RC14-REPRODUZIDO.json`.

A correção não é uma conferência a mais: é **trocar a origem do número**.
`consolidar_inspecao` monta o bloco `inspection_verification` **contando** as
âncoras dos recibos em disco — `contar_ancoras_declaradas` —, nunca lendo o campo
homônimo do relatório. O relatório da trava continua sendo a única fonte do que
**falhou**, porque falha só se sabe reabrindo; e as duas medidas são
**confrontadas**: divergirem é `BLOCKED_ANCHOR_COUNT_MISMATCH`, e nada é emitido.

Duas fontes independentes, uma contada e outra reaberta, com recusa na
divergência. Fabricar uma passa a exigir fabricar a outra **e** os recibos em
disco de onde a primeira sai.

Rodada 5 — a alegação passa a caber no mecanismo
------------------------------------------------
As quatro primeiras rodadas perseguiram defeitos, e cada correção fechou a
instância anterior enquanto o mesmo padrão reaparecia um nível abaixo. A quinta
não persegue: **aceita um teto e o declara**.

O teto foi medido por origem independente, em `OI-04`, e a medida está aqui
porque medida sem número é opinião: **forjar a evidência é chamar as mesmas
funções que a verificam** — 80 linhas de código, 0,031 s, 1 tentativa, 4
arquivos lidos, zero conhecimento do conteúdo auditado. Derivar da evidência
protege contra valor **digitado**; não protege contra quem **chama o
derivador**, porque o atacante e o verificador compartilham o código, o
processo e a árvore.

Daí a mudança desta rodada, e ela é de **alegação**, não de verificação:

- `ALEGACAO_DO_COMPLIANT` diz, em uma frase, o que o binário certifica;
- `NAO_COBERTO_PELA_ALEGACAO` diz, na frase seguinte, o que ele **não**
  certifica, com a medida;
- as duas viajam no `AUDIT_LEDGER` **e** no `GOVERNANCE_REPORT`, porque quem
  decide na barreira não reabre nada, e limite que mora em documentação não
  chega lá — foi assim que `R6`, `R9` e `R10` falharam até a rodada 3.

**Nada foi afrouxado.** Toda trava das rodadas 1 a 4 continua no lugar, com os
mesmos casos negativos, e esta rodada acrescenta três: a recontagem dos estados
da matriz (`OI-01`), a exigência de origem independente e o cruzamento de
identidade contra fonte externa à linha (`OI-03`, em
`_compartilhado/verificacoes_pacote.py`).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

__all__ = [
    "ESTADOS",
    "ESTADOS_QUE_EXIGEM_ANCORA",
    "ORDEM_DE_GRAVIDADE",
    "ESTADOS_BLOQUEANTES",
    "MODOS_DE_EXECUCAO",
    "TAMANHO_MINIMO_DA_CITACAO",
    "sha256_de_arquivo",
    "reverificar_ancora",
    "conferir_metodo",
    "contar_itens_do_contrato",
    "estado_efetivo",
    "estado_mais_grave",
    "decidir_veredito",
    "derivar_binario",
    "verificar_inspecao_executada",
    "contar_ancoras_declaradas",
    "consolidar_inspecao",
    "cruzar_identidade_dos_recibos",
    "auditar_ledger_contra_evidencia",
    "verificar_origem_independente",
    # RODADA 7 — a junção que confronta `candidate_producer` com as missões em
    # disco, e os dois estados nomeados que ela produz.
    "conferir_produtor_contra_a_raiz",
    "PRODUTOR_NAO_CONFERE",
    "FONTE_DE_NOMES_AUSENTE",
    "RECEITA_DA_CONTAGEM",
    "ALEGACAO_DO_COMPLIANT",
    "NAO_COBERTO_PELA_ALEGACAO",
    "ORIGEM_INDEPENDENTE_OK",
    "ESTADOS_DA_ORIGEM_INDEPENDENTE",
]

# ---------------------------------------------------------------------------
# A ALEGAÇÃO — rodada 5, frente A
# ---------------------------------------------------------------------------
#
# Estas duas strings são o contrato semântico do binário, e são `const` no
# schema do CEO. Editar uma delas aqui sem editar o schema derruba a emissão:
# **duas edições, em dois arquivos, para alargar a alegação.** Foi essa a lição
# das quatro rodadas anteriores — aviso em prosa não previne erro; trava em
# código, sim.
#
# ANTES (rodadas 1 a 4, texto vigente no `SKILL.md` e no ADR-017):
#   "COMPLIANT significa que a inspeção foi EXECUTADA: cada âncora foi reaberta
#    contra a raiz auditada e a citação conferida no byte."
#
# DEPOIS (esta rodada): o que o mecanismo de fato verifica, e nada além.
ALEGACAO_DO_COMPLIANT = (
    "COMPLIANT certifica exatamente isto: nenhum valor deste envelope foi"
    " aceito como digitado quando divergia da evidência reaberta. Toda âncora"
    " declarada foi reaberta contra a raiz auditada, cada citação foi conferida"
    " no byte, cada total foi recontado dos recibos em disco e cada estado da"
    " matriz foi rederivado dos mesmos recibos."
)

NAO_COBERTO_PELA_ALEGACAO = (
    "COMPLIANT NÃO certifica que a evidência não foi forjada. Forjar a evidência"
    " é chamar as mesmas funções que a verificam: medido por origem"
    " independente em 2026-08-02 (OI-04) a 80 linhas, 0,031 s, 1 tentativa, 4"
    " arquivos lidos e zero conhecimento do conteúdo auditado. Atacante e"
    " verificador compartilham o código, o processo e a árvore; fechar isto"
    " exige âncora externa ao pacote, que não cabe no runtime atual."
)


# Endereço único da contagem, publicado no envelope. Quem recebe o
# `inspection_verification` sabe por qual função o número foi produzido e pode
# repetir a conta — que é a diferença entre número conferível e número afirmado.
RECEITA_DA_CONTAGEM = (
    "scripts/inspecao_executada.py::contar_ancoras_declaradas"
)

ESTADOS = (
    "CONFORME",
    "RESSALVA",
    "NAO_CONFORME",
    "NAO_APLICAVEL",
    "NAO_PROVADO",
)

# `NAO_PROVADO` é o único estado que pode sair sem âncora — é justamente o
# estado que declara "não verifiquei". Todos os outros afirmam alguma coisa
# sobre o candidato, e afirmação sem âncora é relato.
#
# `NAO_APLICAVEL` entra na lista de propósito, e isso é aperto, não folga: o R7
# do protocolo diz que quem julga a aplicabilidade é quem verifica, e a
# justificativa em prosa (`minLength: 20` no schema) nunca teve como ser
# conferida. Agora ela aponta para a linha do candidato que mostra a ausência.
ESTADOS_QUE_EXIGEM_ANCORA = (
    "CONFORME",
    "RESSALVA",
    "NAO_CONFORME",
    "NAO_APLICAVEL",
)

# Ordem total de `references/dimensoes-e-conformidade.md`, §3. Índice maior é
# mais grave. Recalculada aqui porque é decisão de consolidação, e o emissor e o
# validador precisam ler a MESMA ordem — duas cópias divergem em silêncio.
ORDEM_DE_GRAVIDADE = (
    "NAO_APLICAVEL",
    "CONFORME",
    "RESSALVA",
    "NAO_PROVADO",
    "NAO_CONFORME",
)

ESTADOS_BLOQUEANTES = frozenset({"NAO_CONFORME", "NAO_PROVADO"})

# `PAPEL_SOB_PORTA_UNICA` — a gerente executa o método lendo o contrato do
# agente, porque o agente não resolve como skill invocável.
# `CAPACIDADE_INVOCAVEL` — o agente resolveu e devolveu recibo próprio.
# Os dois exigem âncora. O modo descreve **quem executou**, e nunca é desconto
# de prova: um recibo de capacidade invocável sem âncora cai igual.
MODOS_DE_EXECUCAO = ("PAPEL_SOB_PORTA_UNICA", "CAPACIDADE_INVOCAVEL")

# Citação curta demais casa com quase qualquer linha e devolveria à âncora o
# mesmo vazio do `evidence_refs` opaco que ela substitui. Oito caracteres úteis
# é o piso.
TAMANHO_MINIMO_DA_CITACAO = 8


def sha256_de_arquivo(caminho: Path) -> str:
    return "sha256:" + hashlib.sha256(caminho.read_bytes()).hexdigest()


def _resolver_dentro(raiz: Path, referencia: str) -> tuple[Path | None, str | None]:
    """Resolve `referencia` sob `raiz`, recusando fuga do diretório.

    Âncora que aponta para fora da raiz auditada não é evidência do candidato:
    é outro artefato com o nome dele.
    """
    if not referencia or not isinstance(referencia, str):
        return None, "artifact_ref vazio"
    bruto = Path(referencia)
    if bruto.is_absolute():
        return None, f"artifact_ref absoluto não é aceito: {referencia}"
    alvo = (raiz / bruto).resolve()
    try:
        alvo.relative_to(raiz.resolve())
    except ValueError:
        return None, f"artifact_ref escapa da raiz auditada: {referencia}"
    return alvo, None


# ---------------------------------------------------------------------------
# RODADA 6 — AUSÊNCIA VIRA ESTADO NOMEADO
# ---------------------------------------------------------------------------
#
# Duas travas, e as duas fecham achados CRÍTICOS de origem independente da
# rodada 5. A família é a mesma, e é a lição de cinco rodadas: **campo cuja
# omissão libera passagem não é campo opcional, é porta**.
#
# `OI5-02` — `candidate_producer` era lido por `rodada.get()`, não era exigido
# por linha de código nenhuma e não aparecia em schema nenhum. Apagar UMA linha
# de `rodada.json` fazia o produtor do candidato assinar os casos que julgam o
# próprio candidato, com `COMPLIANT` gravado e exit 0. O agravante estava no
# comentário do emissor, que afirmava por escrito que o campo era "obrigatório"
# — diagnóstico exato, sem nenhuma linha que o impusesse. Aviso em prosa não
# previne erro; é a quinta repetição desta casa, e ela termina aqui.
#
# `OI5-04` — `evidence_refs` era transportado de `rodada.json` para o
# `AUDIT_LEDGER` e para o `GOVERNANCE_REPORT` sem que nada o confrontasse.
# Apontando para arquivo inexistente, viajava num `COMPLIANT` exit 0 com a
# alegação da rodada impressa ao lado.
#
# Os dois estados abaixo são NOMEADOS de propósito: bloqueio anônimo é bloqueio
# que ninguém consegue endereçar, e o consumidor precisa distinguir "não resolve"
# de "não foi declarado".

EVIDENCE_REF_NAO_RESOLVE = "EVIDENCE_REF_NAO_RESOLVE"









def resolver_evidence_refs(refs: Any, raiz: Path) -> tuple[list[str], list[str]]:
    """Cada `evidence_ref` da rodada é RESOLVIDO contra a raiz auditada.

    Devolve `(resolvidos, erros)`. Referência que não resolve bloqueia — não vira
    ressalva, não vira pendência e não viaja no envelope.

    O que esta função fecha, medido em `OI5-04`: uma lista DIGITADA em
    `rodada.json`, apontando para arquivo que não existe na árvore, chegava ao
    `AUDIT_LEDGER` e ao `GOVERNANCE_REPORT` que o CEO lê na barreira, dentro de um
    `COMPLIANT` exit 0, com interseção VAZIA em relação ao que a corrida havia
    de fato reaberto.

    O que ela NÃO fecha, e é declarado: resolver prova que o arquivo EXISTE na
    versão da árvore auditada. Não prova que ele sustenta a dimensão que o cita —
    pertinência é mérito, e mérito é dos Juízes (R9). Uma referência para um
    arquivo real e irrelevante continua atravessando esta trava, e uma referência
    para arquivo que o próprio produtor acabou de criar dentro da raiz auditada
    também. O que a trava tira do atacante é o custo zero: o alvo deixa de poder
    ser um nome inventado e passa a ter de existir em disco, na árvore que o
    `candidate_digest` cobre.
    """
    erros: list[str] = []
    if not isinstance(refs, list):
        return [], [f"evidence_refs não é lista: {type(refs).__name__}"]
    if not refs:
        return [], ["evidence_refs vazio: o envelope não aponta para evidência alguma"]

    resolvidos: list[str] = []
    for indice, referencia in enumerate(refs):
        if not isinstance(referencia, str) or not referencia.strip():
            erros.append(f"evidence_refs[{indice}] não é caminho textual: {referencia!r}")
            continue
        alvo, erro = _resolver_dentro(raiz, referencia)
        if erro:
            erros.append(f"evidence_refs[{indice}] {erro}")
            continue
        assert alvo is not None
        if not alvo.is_file():
            erros.append(
                f"evidence_refs[{indice}] não resolve contra a raiz auditada:"
                f" {referencia} não existe em disco"
            )
            continue
        resolvidos.append(referencia)
    return resolvidos, erros


def reverificar_ancora(ancora: dict[str, Any], raiz: Path) -> list[str]:
    """Reabre o arquivo na linha declarada e confere a citação e o digest.

    É esta função que distingue inspeção executada de inspeção afirmada. Ela não
    acredita em nada do recibo: abre o byte.

    Devolve lista vazia quando a âncora reabre; uma linha por defeito quando não.
    """
    erros: list[str] = []
    if not isinstance(ancora, dict):
        return ["âncora não é objeto"]

    faltando = [
        campo
        for campo in ("artifact_ref", "line", "quote", "file_digest")
        if campo not in ancora
    ]
    if faltando:
        return [f"âncora incompleta, faltam {faltando}"]

    alvo, erro = _resolver_dentro(raiz, ancora["artifact_ref"])
    if erro:
        return [erro]
    assert alvo is not None
    if not alvo.is_file():
        return [f"âncora não reabre: {ancora['artifact_ref']} não existe sob {raiz}"]

    digest_real = sha256_de_arquivo(alvo)
    if ancora["file_digest"] != digest_real:
        erros.append(
            f"âncora sobre versão errada de {ancora['artifact_ref']}: "
            f"declarado {ancora['file_digest']}, real {digest_real}"
        )

    linhas = alvo.read_text(encoding="utf-8", errors="replace").splitlines()
    numero = ancora["line"]
    if not isinstance(numero, int) or isinstance(numero, bool) or numero < 1:
        erros.append(f"line inválida: {numero!r}")
        return erros
    if numero > len(linhas):
        erros.append(
            f"line {numero} além do fim de {ancora['artifact_ref']} "
            f"({len(linhas)} linhas)"
        )
        return erros

    citacao = ancora["quote"]
    if not isinstance(citacao, str) or len(citacao.strip()) < TAMANHO_MINIMO_DA_CITACAO:
        erros.append(
            f"quote curta demais para ancorar ({TAMANHO_MINIMO_DA_CITACAO} "
            f"caracteres úteis exigidos): {citacao!r}"
        )
        return erros

    if citacao.strip() not in linhas[numero - 1]:
        erros.append(
            f"quote não está na linha {numero} de {ancora['artifact_ref']}: "
            f"citado {citacao.strip()!r}, lido {linhas[numero - 1].strip()!r}"
        )
    return erros


_ITEM_NUMERADO = re.compile(r"^\s*\d+\.\s+\S")
_ITEM_MARCADOR = re.compile(r"^\s*[-*]\s+\S")


def contar_itens_do_contrato(texto: str, secao: str) -> int:
    """Conta os itens de uma seção do contrato do agente.

    A contagem é a prova barata de que o contrato foi **aberto**: quem não o leu
    não sabe quantas obrigações ele tem. Não prova leitura atenta — prova
    leitura, que é o degrau que faltava.
    """
    linhas = texto.splitlines()
    dentro = False
    itens = 0
    for linha in linhas:
        if linha.startswith("## "):
            dentro = linha[3:].strip().casefold() == secao.casefold()
            continue
        if not dentro:
            continue
        if _ITEM_NUMERADO.match(linha) or _ITEM_MARCADOR.match(linha):
            itens += 1
    return itens


# RODADA 9 — OS DOIS ESTADOS NOMEADOS DO MÉTODO
#
# `C01`, rodada 8: *"o método é conferido como DOCUMENTO e não como IDENTIDADE"*.
# Um arquivo qualquer da árvore sem `## Obrigações` satisfazia a prova de leitura
# com `0 == 0`, e o envelope afirmava ao CEO três métodos conferidos. Os dois
# defeitos têm nome próprio a partir daqui, e os dois bloqueiam.
METODO_DENOMINADOR_ZERO = "DENOMINADOR_ZERO"
METODO_NAO_E_CONTRATO_DE_AGENTE = "ALVO_NAO_E_CONTRATO_DE_AGENTE"
METODO_SEM_AMARRA_DE_PAPEL = "METODO_NAO_AMARRADO_AO_role_of"

# A anatomia é a da própria árvore: todo contrato de agente mora em
# `<pacote>/agentes/<nome>/CONTRATO-DE-COMPROMISSO.md`. Nada aqui é convenção
# nova — é a mesma anatomia que `validate_agents_folder` já exige, lida do
# CAMINHO em vez de suposta pelo conteúdo.
NOME_DO_CONTRATO_DE_AGENTE = "CONTRATO-DE-COMPROMISSO.md"
PASTA_DOS_AGENTES = "agentes"


def conferir_identidade_do_contrato_de_agente(
    metodo: dict[str, Any], alvo: Path
) -> list[str]:
    """O alvo é RECONHECIDO como contrato de agente e AMARRADO ao `role_of`.

    Derivado do caminho, não do conteúdo: quem escolhe o conteúdo é quem escreve
    o recibo, e comparar o artefato consigo mesmo é o defeito que a rodada 5
    fechou em `cruzar_identidade_externa`. O caminho, não.
    """
    erros: list[str] = []
    if alvo.name != NOME_DO_CONTRATO_DE_AGENTE:
        erros.append(
            f"{METODO_NAO_E_CONTRATO_DE_AGENTE}: {metodo.get('agent_contract_ref')}"
            f" não é um {NOME_DO_CONTRATO_DE_AGENTE}; é {alvo.name}"
        )
        return erros
    partes = alvo.parts
    if len(partes) < 3 or partes[-3] != PASTA_DOS_AGENTES:
        erros.append(
            f"{METODO_NAO_E_CONTRATO_DE_AGENTE}:"
            f" {metodo.get('agent_contract_ref')} não mora sob"
            f" {PASTA_DOS_AGENTES}/<agente>/ — não é contrato de agente nenhum"
        )
        return erros
    nome_do_agente = partes[-2]
    if metodo.get("role_of") != nome_do_agente:
        erros.append(
            f"{METODO_SEM_AMARRA_DE_PAPEL}: o recibo diz executar o papel de"
            f" {metodo.get('role_of')!r} e abriu o contrato de"
            f" {nome_do_agente!r}"
        )
    return erros


def conferir_metodo(metodo: dict[str, Any], raiz: Path) -> list[str]:
    """O método declarado é o contrato do agente, aberto e conferido.

    Sem contrato em disco, não há método; sem método, a inspeção não tem régua e
    a dimensão cai para `NAO_PROVADO`. É aqui que `MISSING` continua sendo
    `MISSING`: a porta única tirou a *invocabilidade* do agente, não o contrato
    dele. Ausência do contrato permanece ausência.
    """
    erros: list[str] = []
    if not isinstance(metodo, dict):
        return ["method não é objeto"]

    obrigatorios = (
        "role_of",
        "executed_by",
        "execution_mode",
        "agent_contract_ref",
        "agent_contract_digest",
        "obrigacoes_declaradas",
        "barreira_de_saida_declarada",
    )
    faltando = [campo for campo in obrigatorios if campo not in metodo]
    if faltando:
        return [f"method incompleto, faltam {faltando}"]

    if metodo["execution_mode"] not in MODOS_DE_EXECUCAO:
        erros.append(f"execution_mode fora dos dois modos: {metodo['execution_mode']!r}")

    alvo, erro = _resolver_dentro(raiz, metodo["agent_contract_ref"])
    if erro:
        return erros + [erro]
    assert alvo is not None
    if not alvo.is_file():
        return erros + [
            "método MISSING: contrato do agente ausente em "
            f"{metodo['agent_contract_ref']}"
        ]

    digest_real = sha256_de_arquivo(alvo)
    if metodo["agent_contract_digest"] != digest_real:
        erros.append(
            "método sobre versão errada do contrato do agente: declarado "
            f"{metodo['agent_contract_digest']}, real {digest_real}"
        )

    texto = alvo.read_text(encoding="utf-8")

    # RODADA 9 — A IDENTIDADE DO MÉTODO É DERIVADA, NUNCA SUPOSTA.
    erros.extend(conferir_identidade_do_contrato_de_agente(metodo, alvo))

    obrigacoes = contar_itens_do_contrato(texto, "Obrigações")
    barreira = contar_itens_do_contrato(texto, "Barreira de saída")

    # RODADA 9 — COMPARAÇÃO COM DENOMINADOR ZERO É DEFEITO, NÃO ACORDO.
    #
    # `C01` da rodada 8, medido: com `method.agent_contract_ref` apontando para
    # um arquivo que NÃO é contrato de agente — o `ORGANOGRAMA.md` serviu —, a
    # contagem dá zero, o declarado é zero, `0 == 0` fecha, e o envelope viaja
    # ao CEO dizendo *"métodos 3/3 conferidos"*. Três contratos que ninguém
    # abriu. O vácuo passa a ter nome próprio e a bloquear como qualquer falha
    # de método: `metodos_falhos` sobe, `estado_efetivo` rebaixa as dimensões
    # daquele inspetor para `NAO_PROVADO`, e nenhum COMPLIANT sai por cima.
    for rotulo, contadas, declaradas in (
        ("Obrigações", obrigacoes, metodo["obrigacoes_declaradas"]),
        ("Barreira de saída", barreira, metodo["barreira_de_saida_declarada"]),
    ):
        if contadas == 0:
            erros.append(
                f"{METODO_DENOMINADOR_ZERO}: a seção '{rotulo}' de"
                f" {metodo['agent_contract_ref']} tem ZERO itens contados, e"
                f" {declaradas} == {contadas} fecharia no vácuo. Prova de"
                " leitura com denominador zero não prova leitura nenhuma."
            )
    if metodo["obrigacoes_declaradas"] != obrigacoes:
        erros.append(
            "método não foi lido: obrigações declaradas "
            f"{metodo['obrigacoes_declaradas']}, contadas {obrigacoes} em "
            f"{metodo['agent_contract_ref']}"
        )
    if metodo["barreira_de_saida_declarada"] != barreira:
        erros.append(
            "método não foi lido: barreira de saída declarada "
            f"{metodo['barreira_de_saida_declarada']}, contada {barreira} em "
            f"{metodo['agent_contract_ref']}"
        )
    return erros


def estado_efetivo(
    estado_declarado: str,
    *,
    ancoras_validas: int,
    metodo_conferido: bool,
) -> str:
    """O estado que **vale**, depois de conferida a inspeção.

    Regra única, e é o coração da trava:

    - método não conferido → `NAO_PROVADO`, qualquer que seja o declarado;
    - estado que afirma algo, sem âncora que reabra → `NAO_PROVADO`;
    - `NAO_PROVADO` continua `NAO_PROVADO`, e continua bloqueando.

    Nada aqui promove estado. A função só **rebaixa** — nunca converte
    `NAO_PROVADO` em `CONFORME`, e essa direção única é o que impede que
    reclassificar vire conserto.
    """
    if estado_declarado not in ESTADOS:
        return "NAO_PROVADO"
    if not metodo_conferido:
        return "NAO_PROVADO"
    if estado_declarado in ESTADOS_QUE_EXIGEM_ANCORA and ancoras_validas < 1:
        return "NAO_PROVADO"
    return estado_declarado


def estado_mais_grave(estados: list[str]) -> str:
    """Dois inspetores na mesma dimensão: o mais grave vence. Nunca média."""
    return max(estados, key=ORDEM_DE_GRAVIDADE.index)


def decidir_veredito(estados: dict[str, str]) -> str:
    if any(estado in ESTADOS_BLOQUEANTES for estado in estados.values()):
        return "REPROVADO"
    if any(estado == "RESSALVA" for estado in estados.values()):
        return "APROVADO_COM_RESSALVAS"
    return "APROVADO"


def derivar_binario(veredito_interno: str) -> str:
    return "NONCOMPLIANT" if veredito_interno == "REPROVADO" else "COMPLIANT"


def verificar_inspecao_executada(
    recibos: list[dict[str, Any]],
    raiz: Path,
) -> dict[str, Any]:
    """Percorre os recibos, reabre cada âncora e devolve o veredito de execução.

    **Esta função é o portão.** Quem emite `GOVERNANCE_REPORT` a chama antes de
    montar a matriz; quem consome confere que ela foi chamada. O relatório que
    ela devolve entra no `AUDIT_LEDGER` como `inspection_verification`, e o
    schema recusa `COMPLIANT` sem ele.

    Devolve, por dimensão, o estado declarado e o **efetivo**, mais a contagem
    de âncoras reabertas e a lista de defeitos.
    """
    raiz = Path(raiz)
    falhas: list[str] = []
    ancoras_total = 0
    ancoras_falhas = 0
    metodos_total = 0
    metodos_falhos = 0
    rebaixamentos: list[dict[str, str]] = []
    por_dimensao: dict[str, list[str]] = {}

    for recibo in recibos:
        auditor = recibo.get("auditor_id", "<sem auditor_id>")
        metodo = recibo.get("method")
        metodos_total += 1
        if metodo is None:
            metodos_falhos += 1
            erros_metodo = [f"{auditor}: recibo sem bloco method"]
        else:
            erros_metodo = [f"{auditor}: {e}" for e in conferir_metodo(metodo, raiz)]
            if erros_metodo:
                metodos_falhos += 1
        falhas.extend(erros_metodo)
        metodo_ok = not erros_metodo

        for linha in recibo.get("dimension_states", []):
            dimensao = linha.get("dimension", "<sem dimension>")
            declarado = linha.get("state", "<sem state>")
            validas = 0
            for indice, ancora in enumerate(linha.get("evidence_anchors", [])):
                ancoras_total += 1
                erros_ancora = reverificar_ancora(ancora, raiz)
                if erros_ancora:
                    ancoras_falhas += 1
                    falhas.extend(
                        f"{auditor}/{dimensao}/âncora[{indice}]: {e}"
                        for e in erros_ancora
                    )
                else:
                    validas += 1

            efetivo = estado_efetivo(
                declarado,
                ancoras_validas=validas,
                metodo_conferido=metodo_ok,
            )
            if efetivo != declarado:
                rebaixamentos.append(
                    {
                        "dimension": dimensao,
                        "auditor_id": auditor,
                        "declarado": declarado,
                        "efetivo": efetivo,
                        "motivo": (
                            "método não conferido"
                            if not metodo_ok
                            else "nenhuma âncora reabriu"
                        ),
                    }
                )
            por_dimensao.setdefault(dimensao, []).append(efetivo)

    estados_consolidados = {
        dimensao: estado_mais_grave(estados)
        for dimensao, estados in por_dimensao.items()
    }

    # `all_anchors_reverified` é **vacuamente verdadeiro** com zero âncoras, e
    # isso é deliberado: o campo mede se o que existia reabriu, não se existia
    # algo. Quem carrega esse segundo sinal é `anchors_total`, e o schema exige
    # `anchors_total ≥ 10` para `COMPLIANT` — dez dimensões afirmando, uma
    # âncora cada, no mínimo. Sobrecarregar o booleano esconderia a diferença
    # entre "conferi e passou" e "não havia o que conferir".
    return {
        "all_anchors_reverified": ancoras_falhas == 0 and metodos_falhos == 0,
        "anchors_total": ancoras_total,
        "anchors_failed": ancoras_falhas,
        "methods_total": metodos_total,
        "methods_failed": metodos_falhos,
        "downgrades": rebaixamentos,
        "failures": falhas,
        "effective_states": estados_consolidados,
    }


# ---------------------------------------------------------------------------
# RODADA 4 — o número que vai ao envelope é CONTADO, nunca lido
# ---------------------------------------------------------------------------


def contar_ancoras_declaradas(recibos: list[dict[str, Any]]) -> dict[str, int]:
    """Reconta, direto dos recibos em disco, o que existe para ser reaberto.

    **Esta função não reabre nada, e é de propósito.** Ela mede uma coisa só: o
    tamanho da amostra que o recibo apresenta. Quem mede se a amostra reabre é
    `verificar_inspecao_executada`, e as duas medidas têm de bater.

    Por que existe: até a rodada 3 o `anchors_total` que ia ao `AUDIT_LEDGER` era
    **lido** de um dicionário. Bastava uma função intermediária devolvendo
    `{"anchors_total": 12}` para o campo carregar doze sobre **zero** âncoras
    reais, com a cadeia de nomes preservada e o validador verde. Contar aqui
    fecha essa porta pela origem: o número passa a ser o resultado de um `len`
    sobre a lista que veio do disco.
    """
    total = 0
    for recibo in recibos:
        if not isinstance(recibo, dict):
            continue
        for linha in recibo.get("dimension_states", []):
            if isinstance(linha, dict):
                total += len(linha.get("evidence_anchors", []) or [])
    return {"anchors_total": total, "methods_total": len(recibos)}


def consolidar_inspecao(
    recibos: list[dict[str, Any]],
    relatorio: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Deriva `inspection_verification` — contando — e recusa na divergência.

    Regra da rodada 4, em código: **valor que pode ser derivado da evidência não
    é aceito como declarado.**

    - `anchors_total` e `methods_total` saem de `contar_ancoras_declaradas`,
      sobre os recibos em disco. Nenhum ramo desta função lê os campos homônimos
      de `relatorio`, exceto para **confrontá-los**;
    - `all_anchors_reverified` é **derivado** de `anchors_failed == 0 and
      methods_failed == 0`, nunca copiado — booleano copiado é declaração;
    - `anchors_failed` e `methods_failed` vêm da trava, porque falha só se sabe
      reabrindo, e isso é o que a trava faz. São os únicos dois números do bloco
      que têm origem única, e o `limite` publicado no envelope diz isso.

    Devolve `(bloco, divergencias)`. Divergência não é corrigida em silêncio nem
    escolhida por precedência: o emissor recusa e nada é auditado.
    """
    contado = contar_ancoras_declaradas(recibos)
    divergencias: list[str] = []

    if relatorio.get("anchors_total") != contado["anchors_total"]:
        divergencias.append(
            "anchors_total: a trava reabriu"
            f" {relatorio.get('anchors_total')!r} âncoras e a recontagem dos"
            f" recibos em disco achou {contado['anchors_total']} — o número que"
            " iria ao envelope não é o número que existe"
        )
    if relatorio.get("methods_total") != contado["methods_total"]:
        divergencias.append(
            "methods_total: a trava conferiu"
            f" {relatorio.get('methods_total')!r} métodos e há"
            f" {contado['methods_total']} recibos em disco"
        )

    falhas_de_ancora = relatorio.get("anchors_failed")
    falhas_de_metodo = relatorio.get("methods_failed")
    if not isinstance(falhas_de_ancora, int) or isinstance(falhas_de_ancora, bool):
        divergencias.append(f"anchors_failed não é inteiro: {falhas_de_ancora!r}")
        falhas_de_ancora = contado["anchors_total"]
    if not isinstance(falhas_de_metodo, int) or isinstance(falhas_de_metodo, bool):
        divergencias.append(f"methods_failed não é inteiro: {falhas_de_metodo!r}")
        falhas_de_metodo = contado["methods_total"]
    if falhas_de_ancora > contado["anchors_total"]:
        divergencias.append(
            f"anchors_failed {falhas_de_ancora} maior que o total contado"
            f" {contado['anchors_total']}"
        )
    if falhas_de_metodo > contado["methods_total"]:
        divergencias.append(
            f"methods_failed {falhas_de_metodo} maior que o total contado"
            f" {contado['methods_total']}"
        )

    bloco = {
        "all_anchors_reverified": falhas_de_ancora == 0 and falhas_de_metodo == 0,
        "anchors_total": contado["anchors_total"],
        "anchors_failed": falhas_de_ancora,
        "methods_total": contado["methods_total"],
        "methods_failed": falhas_de_metodo,
        "counted_by": RECEITA_DA_CONTAGEM,
        "counted_limit": (
            "anchors_total e methods_total são CONTADOS dos recibos em disco;"
            " anchors_failed e methods_failed vêm da reabertura e têm origem"
            " única — não há segunda medida que os confronte"
        ),
    }
    return bloco, divergencias


def auditar_ledger_contra_evidencia(
    ledger: dict[str, Any],
    recibos: list[dict[str, Any]],
    raiz: Path,
) -> list[str]:
    """Confronta o ARTEFATO PRONTO com a evidência crua. É a trava de classe.

    Por que esta função existe, e por que ela é diferente de todas as outras
    -----------------------------------------------------------------------
    Três rodadas consertaram *instâncias*: a trava sem call site, o call site por
    nome, a instrução publicada que desviava, a conferência do bloco em vez do
    subcampo, o sumário com constante. A quarta achou o mesmo defeito **dentro**
    do emissor: `anchors_total` declarado, não contado.

    Todas essas correções vigiam o **caminho** — quem chamou quem, e se o valor
    desceu de onde deveria. Vigiar caminho é frágil por natureza: sempre há uma
    função intermediária a mais que preserva a cadeia de nomes e troca o valor.
    Foi assim no nível 2 (descartar o retorno), foi assim no nível 6 (lavagem
    interprocedural), e seria assim de novo.

    Esta função não vigia caminho. Ela pega o **artefato final**, do jeito que vai
    ser gravado, e **refaz a conta a partir dos recibos em disco**. Qualquer
    lavagem, em qualquer ponto do caminho, produz um artefato que não bate com a
    evidência que ele afirma resumir — e é o artefato que é confrontado, não o
    caminho que o produziu.

    O que é refeito, e de onde
    --------------------------
    - `anchors_total` e `methods_total` — recontados dos recibos;
    - `all_anchors_reverified` — recomputado de `anchors_failed`/`methods_failed`;
    - `method_executions` — um por recibo, com os mesmos `task_id`;
    - `assignments` — um por execução, com os mesmos `task_id`;
    - `conformity_matrix.dimensions[].state` — **RECONTADO dos recibos**, com as
      âncoras reabertas contra `raiz`. É a correção do `OI-01`, abaixo;
    - `internal_verdict` — recomputado dos estados RECONTADOS, não dos gravados;
    - `governance_verdict` — recomputado do veredito interno;
    - `violations` — uma por dimensão bloqueada segundo o recontado;
    - `conformity_matrix.dimensions[].evidence_refs` — recolhidas dos recibos;
    - todo rebaixamento que a corrida imprimiu no console tem de aparecer em
      `pending`. Console e envelope não podem divergir.

    `OI-01` — o que estava errado, e é o defeito em forma pura
    ---------------------------------------------------------
    Até a rodada 4 esta função **lia** `conformity_matrix.dimensions[].state` e
    recomputava o veredito **a partir dele**. Ou seja: conferia o artefato
    consigo mesmo e chamava isso de auditar contra a evidência. Uma matriz
    mentirosa — `CONFORME` onde a inspeção rebaixou para `NAO_PROVADO` —
    produzia um `internal_verdict` coerente com ela própria, um binário coerente
    com o veredito, e **zero divergências**. O console imprimia `[REBAIXA]` e o
    envelope gravava `COMPLIANT`. Medido por origem independente em 2026-08-02.

    A correção troca a **origem do estado**, exatamente como a rodada 4 trocou a
    origem do número: os estados são rederivados dos recibos em disco, com as
    âncoras reabertas, e o que a matriz gravou é **confrontado** com eles. Por
    isso `raiz` é parâmetro **obrigatório e posicional**: sem raiz não há
    reabertura, e uma raiz opcional seria a opcionalidade por aridade que o
    achado `A1` já custou uma rodada a esta frente.

    Limite declarado: `anchors_failed` e `methods_failed` **não** têm segunda
    medida independente — saber que uma âncora falhou exige reabri-la, e é o que
    `verificar_inspecao_executada` faz, aqui e lá. O que esta função garante
    sobre eles é coerência com o total contado, e é o que `counted_limit`
    publica no envelope. O teto do conjunto é `NAO_COBERTO_PELA_ALEGACAO`.

    Devolve lista vazia quando o artefato bate com a evidência; uma linha por
    divergência quando não.
    """
    erros: list[str] = []
    contado = contar_ancoras_declaradas(recibos)
    # RECONTAGEM — a evidência crua, reaberta AQUI, e não o que o caminho trouxe.
    recontado = verificar_inspecao_executada(recibos, raiz)
    verificacao = ledger.get("inspection_verification")
    if not isinstance(verificacao, dict):
        return ["ledger sem inspection_verification"]

    if verificacao.get("anchors_total") != contado["anchors_total"]:
        erros.append(
            "LEDGER DIVERGE DA EVIDÊNCIA — inspection_verification.anchors_total"
            f" grava {verificacao.get('anchors_total')!r} e os recibos em disco"
            f" têm {contado['anchors_total']} âncoras"
        )
    if verificacao.get("methods_total") != contado["methods_total"]:
        erros.append(
            "LEDGER DIVERGE DA EVIDÊNCIA — inspection_verification.methods_total"
            f" grava {verificacao.get('methods_total')!r} e há"
            f" {contado['methods_total']} recibos em disco"
        )

    falhas_de_ancora = verificacao.get("anchors_failed")
    falhas_de_metodo = verificacao.get("methods_failed")
    esperado = falhas_de_ancora == 0 and falhas_de_metodo == 0
    if verificacao.get("all_anchors_reverified") != esperado:
        erros.append(
            "LEDGER DIVERGE DA EVIDÊNCIA — all_anchors_reverified grava"
            f" {verificacao.get('all_anchors_reverified')!r} e a derivação de"
            f" anchors_failed={falhas_de_ancora!r} methods_failed="
            f"{falhas_de_metodo!r} dá {esperado!r}"
        )
    if isinstance(falhas_de_ancora, int) and not isinstance(falhas_de_ancora, bool):
        if falhas_de_ancora > contado["anchors_total"]:
            erros.append(
                f"LEDGER INCOERENTE — anchors_failed {falhas_de_ancora} maior que"
                f" o total contado {contado['anchors_total']}"
            )

    identificadores = sorted(
        recibo.get("task_id") for recibo in recibos if isinstance(recibo, dict)
    )
    execucoes = ledger.get("method_executions") or []
    if sorted(item.get("task_id") for item in execucoes) != identificadores:
        erros.append(
            "LEDGER DIVERGE DA EVIDÊNCIA — method_executions grava"
            f" {sorted(item.get('task_id') for item in execucoes)} e os recibos"
            f" em disco são {identificadores}"
        )
    atribuicoes = ledger.get("assignments") or []
    if sorted(item.get("task_id") for item in atribuicoes) != identificadores:
        erros.append(
            "LEDGER DIVERGE DA EVIDÊNCIA — assignments grava"
            f" {sorted(item.get('task_id') for item in atribuicoes)} e os recibos"
            f" em disco são {identificadores}"
        )

    matriz = (ledger.get("conformity_matrix") or {}).get("dimensions") or []
    gravados = {linha.get("dimension"): linha.get("state") for linha in matriz}
    # ---------------------------------------------------------------------
    # OI-01 — O ESTADO DA MATRIZ É RECONTADO, NÃO LIDO.
    # ---------------------------------------------------------------------
    # `esperados` desce de `recontado`, que reabriu as âncoras dos recibos em
    # disco nesta mesma chamada. Nenhum ramo abaixo decide por `gravados`: ele é
    # só o **acusado**. Foi ler `gravados` e recomputar o veredito a partir dele
    # que produziu o COMPLIANT sobre matriz mentirosa.
    esperados = recontado["effective_states"]
    if gravados:
        divergentes = sorted(
            dimensao
            for dimensao in set(gravados) | set(esperados)
            if gravados.get(dimensao) != esperados.get(dimensao, "NAO_PROVADO")
        )
        for dimensao in divergentes:
            erros.append(
                "MATRIZ DIVERGE DA EVIDÊNCIA —"
                f" {dimensao}.state grava {gravados.get(dimensao)!r} e a"
                " reabertura dos recibos em disco deriva"
                f" {esperados.get(dimensao, 'NAO_PROVADO')!r}"
            )
        # O veredito é recomputado do RECONTADO. Se a matriz mentiu, as duas
        # linhas acima já acusaram; esta impede que o veredito desça da mentira.
        veredito = decidir_veredito(esperados)
        if ledger.get("internal_verdict") != veredito:
            erros.append(
                "LEDGER DIVERGE DA EVIDÊNCIA — internal_verdict grava"
                f" {ledger.get('internal_verdict')!r} e os estados rederivados"
                f" dos recibos dão {veredito!r}"
            )
        binario = derivar_binario(veredito)
        if ledger.get("governance_verdict") != binario:
            erros.append(
                "LEDGER DIVERGE DA EVIDÊNCIA — governance_verdict grava"
                f" {ledger.get('governance_verdict')!r} e o veredito rederivado"
                f" {veredito!r} deriva {binario!r}"
            )
        bloqueadas = sum(
            1 for estado in esperados.values() if estado in ESTADOS_BLOQUEANTES
        )
        if len(ledger.get("violations") or []) != bloqueadas:
            erros.append(
                "LEDGER DIVERGE DA EVIDÊNCIA —"
                f" {len(ledger.get('violations') or [])} violações para"
                f" {bloqueadas} dimensões bloqueadas pela evidência"
            )
        # ------------------------------------------------------------------
        # CONSOLE E ENVELOPE NÃO PODEM DIVERGIR.
        # ------------------------------------------------------------------
        # A corrida imprime `[REBAIXA]` por rebaixamento. Até a rodada 4 esse
        # rastro morria com o console: o envelope podia gravar COMPLIANT sem
        # uma linha sobre ele. Aqui todo rebaixamento recontado tem de estar em
        # `pending`, nomeado pela dimensão — o que o operador viu na tela é o
        # que o CEO lê na barreira.
        pendencias = chr(10).join(
            item for item in (ledger.get("pending") or []) if isinstance(item, str)
        )
        for rebaixamento in recontado["downgrades"]:
            marca = f"Rebaixada {rebaixamento['dimension']}"
            if marca not in pendencias:
                erros.append(
                    "CONSOLE DIVERGE DO ENVELOPE — a corrida rebaixou"
                    f" {rebaixamento['dimension']} de"
                    f" {rebaixamento['declarado']} para"
                    f" {rebaixamento['efetivo']} ({rebaixamento['motivo']}) e o"
                    " pending do ledger não registra o rebaixamento"
                )
    else:
        erros.append("LEDGER sem matriz: não há do que recomputar o veredito")

    ancoras_por_dimensao: dict[str, list[str]] = {}
    for recibo in recibos:
        if not isinstance(recibo, dict):
            continue
        for linha in recibo.get("dimension_states", []):
            if not isinstance(linha, dict):
                continue
            destino = ancoras_por_dimensao.setdefault(linha.get("dimension", ""), [])
            for ancora in linha.get("evidence_anchors", []) or []:
                if isinstance(ancora, dict) and ancora.get("evidence_ref") not in destino:
                    destino.append(ancora.get("evidence_ref"))
    for linha in matriz:
        dimensao = linha.get("dimension")
        gravadas = list(linha.get("evidence_refs") or [])
        cruas = ancoras_por_dimensao.get(dimensao, [])
        if gravadas != cruas:
            erros.append(
                f"LEDGER DIVERGE DA EVIDÊNCIA — {dimensao}.evidence_refs grava"
                f" {gravadas} e os recibos em disco trazem {cruas}"
            )
    return erros


def cruzar_identidade_dos_recibos(
    recibos: list[dict[str, Any]],
    candidate_digest: Any,
    contract_digest: Any,
) -> list[str]:
    """Todo recibo declara sobre QUAL candidato inspecionou. Isso é cruzado.

    Um recibo carrega `candidate_digest` e `contract_digest` próprios, e até a
    rodada 3 **ninguém os comparava** com os da rodada. Recibo de outro candidato
    — ou de outra versão do mesmo — entrava na matriz sem uma linha de aviso, e é
    a mesma classe do `37-EVOLUTION-LEDGER-R3`, que declarou o digest do `cand-B`
    enquanto o julgado era o `cand-C`, e validou com zero erros porque nada
    cruzava.

    Devolve lista vazia quando todos cruzam; uma linha por recibo divergente.
    """
    erros: list[str] = []
    for recibo in recibos:
        if not isinstance(recibo, dict):
            erros.append("recibo não é objeto")
            continue
        identificador = recibo.get("task_id", "<sem task_id>")
        if recibo.get("candidate_digest") != candidate_digest:
            erros.append(
                f"{identificador}: candidate_digest do recibo"
                f" {recibo.get('candidate_digest')!r} difere do da rodada"
                f" {candidate_digest!r} — recibo de outro candidato"
            )
        if recibo.get("contract_digest") != contract_digest:
            erros.append(
                f"{identificador}: contract_digest do recibo"
                f" {recibo.get('contract_digest')!r} difere do da rodada"
                f" {contract_digest!r} — recibo sob outro contrato"
            )
        for linha in recibo.get("dimension_states", []):
            if not isinstance(linha, dict):
                continue
            declaradas = sorted(set(linha.get("evidence_refs", []) or []))
            ancoradas = sorted(
                {
                    ancora.get("evidence_ref")
                    for ancora in linha.get("evidence_anchors", []) or []
                    if isinstance(ancora, dict)
                }
            )
            if linha.get("state") in ESTADOS_QUE_EXIGEM_ANCORA and declaradas != ancoradas:
                erros.append(
                    f"{identificador}/{linha.get('dimension')}: evidence_refs"
                    f" declaradas {declaradas} não são as âncoras entregues"
                    f" {ancoradas} — a lista de evidências é afirmada, não é a"
                    " que foi reaberta"
                )
    return erros


# ---------------------------------------------------------------------------
# RODADA 5 — ORIGEM INDEPENDENTE VIRA PARTE DO GATE
# ---------------------------------------------------------------------------
#
# Por que esta função existe, e por que ela é a única defesa nova que não é
# mais uma trava sobre o próprio código
# --------------------------------------------------------------------------
# Quatro rodadas mediram a mesma curva: cada correção fecha a instância anterior
# e o padrão reaparece um nível dentro de si. `OI-01` é a forma pura — a
# auditoria conferia o artefato **consigo mesmo**. Nenhuma trava escrita pelo
# produtor sai desse laço, porque o produtor escreve a trava e escreve o caso
# que a exercita, e o caso é o que ele imaginou.
#
# A única prática desta frente com taxa de acerto perfeita em duas rodadas
# seguidas é outra: **um terceiro escreve os casos contra os pontos cegos que o
# produtor declarou**. Rodada 3, um caso decisivo; rodada 4, sete de sete, e a
# lista do produtor mostrou-se honesta nos dois sentidos — dois dos suspeitos
# que ele apontou deram `NAO_ACHOU`, e ele não inflou o mea-culpa.
#
# Isso deixa de ser boa prática e vira **exigência do gate**. Sem evidência de
# que um terceiro produziu casos contra a lista declarada, não há `COMPLIANT`.
#
# O que é conferido, e nada é aceito por declaração
# -------------------------------------------------
# 1. os dois artefatos EXISTEM sob a pasta da rodada, sem fuga de diretório;
# 2. os dois digests declarados são RECOMPUTADOS sobre os bytes em disco;
# 3. quem produziu os casos NÃO é quem produziu o candidato;
# 4. cada caso aponta para um ponto cego que EXISTE na lista declarada — caso
#    órfão é caso sobre outra coisa;
# 5. cada ponto cego declarado tem ao menos um caso — cobertura é contada, não
#    afirmada. Declarar dez pontos cegos e atacar um não é origem independente.
#
# Limite declarado: isto prova **origem**, não **acerto**. Um terceiro pode
# escrever casos fracos. O que a exigência garante é que a lista de ataque não
# saiu da mesma cabeça que escreveu a defesa — e é exatamente o que faltava.


# ---------------------------------------------------------------------------
# RODADA 8 — O QUE ESTE MÓDULO PAROU DE AFIRMAR, E POR QUÊ
# ---------------------------------------------------------------------------
#
# Saíram daqui, com motivo nomeado em `137-RETIRADO-NA-R8-COM-MOTIVO-E-PROVA.md`:
# os estados e as funções da ORIGEM INDEPENDENTE e do PRODUTOR DO CANDIDATO.
#
# Não saíram por serem frouxos. Saíram porque **defendiam alegações que este
# emissor não precisa fazer**, e sete rodadas mediram a consequência: para toda
# conferência acrescentada havia uma mentira que ela não cobria — `round`
# carimbado, lista trocada por dois campos de texto, nome substituído (2 de 2 e
# 80 de 80), confissão com `medidos = 0`.
#
# O que fica é o objetivo A, e ele não dependia de nenhuma delas: a prova por
# execução pareada de `138-PROVA-DE-A-R8.md` derruba os contratos de agente e
# mede dez `NAO_PROVADO`; com a árvore intacta, mede dez estados DERIVADOS de
# recibo cuja âncora reabre. Nenhuma das funções retiradas aparece no caminho
# entre a âncora e o estado.
