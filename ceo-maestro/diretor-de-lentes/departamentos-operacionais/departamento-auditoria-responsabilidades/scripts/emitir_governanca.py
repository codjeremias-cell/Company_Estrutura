"""Emissor único do `AUDIT_LEDGER` e do `GOVERNANCE_REPORT`.

**Este arquivo é o fluxo real.** O `GOVERNANCE_REPORT` que o CEO lê na barreira
de saída é produzido aqui, rodando; não é JSON digitado à mão. O protocolo (§4) e
a `SKILL.md` (passo 7) declaram isso obrigatório, e o validador do pacote confere
que as travas continuam sendo chamadas daqui **e que o resultado delas é o que
decide** — por fluxo de dados na AST, não por presença de nome.

A lição que este desenho incorpora
----------------------------------
O julgamento da tarefa 14 encontrou três travas que existiam, ficavam vermelhas
quando mutadas e **não tinham call site sobre o fluxo real** — eram funções puras
chamadas só pelo construtor de casos do eval. Protegiam o eval, não a operação.

O julgamento da tarefa 15, rodada 1, encontrou o nível seguinte do mesmo defeito,
duas vezes:

- o call site era conferido **pelo nome chamado**: manter a chamada e descartar o
  retorno produzia `COMPLIANT` com zero âncoras, e o validador ficava verde;
- a conferência de identidade era **opcional por aridade de argv**, e a única
  invocação publicada era justamente a que a pulava — em silêncio.

Por isso a ordem abaixo é a ordem da decisão, e não uma conferência posterior:

    recibos em disco
        -> conferir_identidade_do_candidato()  <- identidade, SEMPRE, com status
        -> cruzar_identidade_dos_recibos()     <- recibo é DESTE candidato
        -> verificar_inspecao_executada()      <- a trava, ANTES da matriz
        -> consolidar_inspecao()               <- os números são CONTADOS
        -> estados EFETIVOS (rebaixados)       <- nunca os declarados
        -> matriz das dez dimensões
        -> veredito interno
        -> binário COMPLIANT/NONCOMPLIANT
        -> auditar_ledger_contra_evidencia()   <- estados RECONTADOS da evidência
        -> validação contra o próprio schema
        -> escrita em disco

O julgamento da rodada 3 achou o **nível 6**, e é o mais fundo: `anchors_total`
era **lido**. Uma função intermediária devolvendo números fabricados preservava a
cadeia de nomes, o gate de schema `anchors_total >= 10` aceitava o `12`
fabricado, e o emissor gravava `COMPLIANT` sobre recibos com **zero** âncoras. A
correção não acrescenta conferência: **troca a origem do número**. O bloco
`inspection_verification` passa a sair de `consolidar_inspecao`, que **conta** as
âncoras dos recibos e recusa quando a contagem diverge do que a trava reabriu.

O que este encadeamento garante, e o que não garante
----------------------------------------------------
Garante que **neste** emissor o binário desce do valor devolvido pela trava: os
estados efetivos são o retorno de `verificar_inspecao_executada`, o veredito sai
deles e o binário sai do veredito. `validate_call_site`, no validador do pacote,
confere esse encadeamento por **fluxo de dados** — atribuição ligada ao uso — e
uma variante que mantenha a chamada e descarte o retorno fica **vermelha**.

E garante que a identidade do candidato **nunca deixa de ser um campo**: quando a
raiz do candidato não é declarada, a conferência não acontece e isso vai para
`candidate_identity.status = NAO_CONFERIDO`, que o schema **proíbe** de coexistir
com `COMPLIANT`. Ausência de conferência aparece como ausência, e bloqueia.

Não garante impossibilidade universal, e a frase absoluta que estava aqui na
rodada 1 — "não há caminho que produza o binário sem passar pela trava" — foi
retirada por ser desmentida pela medição. Quem editar este arquivo e o validador
na mesma passada derruba as duas coisas. O que se ganha é que a queda deixa de
ser silenciosa: passa a exigir uma segunda edição, no laço principal do
validador, e a prova de mutação a exibe.

Uso
---
    python scripts/emitir_governanca.py <pasta-da-rodada> <raiz-auditada>

`<pasta-da-rodada>` contém `rodada.json` (cabeçalho causal + referências) e
`recibos/*.json` (um `AUDIT_RECEIPT` por capacidade). `<raiz-auditada>` é a raiz
contra a qual toda âncora é reaberta.

**A raiz do candidato sai de `rodada.json::candidate_root`**, relativa à raiz
auditada — não de um argumento opcional. A forma acima, de dois argumentos, é a
forma publicada **e** a que aciona a conferência de identidade. Um terceiro
argumento é aceito apenas como sobreposição explícita, para operação fora de
rodada, e a ausência dele nunca desliga trava nenhuma:

    python scripts/emitir_governanca.py <pasta-da-rodada> <raiz-auditada> <raiz-do-candidato>

Sai com código 0 quando emite — `COMPLIANT` ou `NONCOMPLIANT`, os dois são
emissões legítimas. Sai com 2 quando **não pode emitir**: envelope que não passa
no próprio schema não é envelope, identidade divergente é
`BLOCKED_CANDIDATE_MISMATCH`, recibo de outro candidato é
`BLOCKED_RECEIPT_IDENTITY_MISMATCH`, contagem que não fecha é
`BLOCKED_ANCHOR_COUNT_MISMATCH` e ledger que não bate com os recibos em disco é
`BLOCKED_LEDGER_EVIDENCE_MISMATCH` — em nenhum dos quatro nada é auditado.

Os dois desfechos da rodada SEM `candidate_root`, medidos
--------------------------------------------------------
A frase absoluta que estava aqui — *"sem `candidate_root` a corrida aborta e nada
é gravado"* — é **verdadeira num ramo e falsa no outro**, e os Juízes mediram o
segundo. Quem decide é o **veredito interno**:

- **veredito interno diferente de `REPROVADO`** — o ramo `COMPLIANT` do schema do
  ledger exige `candidate_identity.status == CONFERIDO`. Com `NAO_CONFERIDO` o
  ledger não passa no próprio schema: `[ABORTA]`, **exit 2**, nenhum envelope
  gravado;
- **veredito interno `REPROVADO`** — aquele ramo do schema não se aplica.
  `NAO_CONFERIDO` é registrado no campo e em `pending`, os **dois envelopes são
  gravados** e a corrida sai com **exit 0**, `NONCOMPLIANT`.

Nos dois casos ausência de conferência permanece ausência, e em nenhum ela vira
`COMPLIANT`. O que muda é se existe envelope para ler.

Rodada 5 — o que este emissor passa a DIZER, e o que passa a EXIGIR
--------------------------------------------------------------------
**Diz menos.** `ALEGACAO_DO_COMPLIANT` e `NAO_COBERTO_PELA_ALEGACAO`, importados
de `inspecao_executada`, viajam no ledger **e** no envelope, em campo próprio.
A alegação passou a ser *"nenhum valor digitado divergente da evidência
reaberta"*; deixou de ser *"a evidência não foi forjada"*, que o mecanismo nunca
sustentou e que `OI-04` mediu em 80 linhas e 0,031 s.

**Exige mais.** Duas travas novas, e nenhuma delas é prosa:

- `verificar_origem_independente` — sem evidência de que um TERCEIRO produziu
  casos contra os pontos cegos que o produtor declarou, não há `COMPLIANT`. Há
  `[BLOCKED_INDEPENDENT_ORIGIN]`, exit 2, nenhum envelope. O schema do CEO e o
  do ledger proíbem a combinação, e a recusa acontece antes deles;
- `auditar_ledger_contra_evidencia` passa a receber a **raiz** e a RECONTAR
  `conformity_matrix.dimensions[].state`, o campo de onde o veredito desce.
  Antes ela recomputava o veredito **a partir** desse campo — conferia o
  artefato consigo mesmo. `OI-01` mediu: matriz mentirosa, `[REBAIXA]` no
  console, `COMPLIANT` no envelope, exit 0.

**Reduzir alegação não é reduzir verificação.** Nenhuma trava saiu; três
entraram.
Rodada 8 — O QUE ESTE EMISSOR PAROU DE AFIRMAR
----------------------------------------------
Sete rodadas mostraram, com números, que **acumular conferência não fecha**.
Cada rodada acrescentou uma trava; para toda trava houve uma mentira que ela não
cobria. A rodada 8 inverte o método: quando um campo não pode ser derivado, o
conserto é **retirar o campo**.

Saem do envelope e do ledger, cada um com motivo nomeado em
`137-RETIRADO-NA-R8-COM-MOTIVO-E-PROVA.md`:

- **origem independente** (`independent_origin`, `independent_origin_status`,
  `independent_origin_produced_by`, `independent_origin_coverage`) — o emissor
  não tem como derivar que um terceiro produziu os casos: o que ele lia era um
  campo `produced_by` digitado por quem depositou a rodada;
- **contagem de pontos cegos** (`blind_spots_total`, `blind_spots_covered`) — o
  denominador era escolhido por quem era medido, e `OI5-01` fechou `1/1`;
- **rodada e alvo da origem** (`independent_origin_round`,
  `independent_origin_target`) — carimbo que o próprio emissor copiava do
  cabeçalho que estava conferindo;
- **produtor do candidato** (`candidate_producer`) — nome que o emissor não pode
  derivar de nada que ele leia;
- **`declared_limits`** — os sete limites do objetivo B, que saiu desta tarefa
  por decisão de Jeremias em 2026-08-02. Continuam declarados, em **prosa do
  pacote** (`LIMITES-DECLARADOS-EM-PROSA.md`), que é o lugar de quem declara sem
  poder derivar.

**O que NÃO saiu, e é o que a tarefa 15 existe para entregar:** o objetivo A.
`AVAILABLE_AS_METHOD` do ADR-017, `MISSING` nomeando contrato ausente, e as dez
dimensões recebendo estado DERIVADO de recibo cuja âncora reabre. A ordem da
decisão continua sendo a ordem do código, e `auditar_ledger_contra_evidencia`
continua recontando a matriz a partir dos recibos em disco.

**O que ENTROU, e entrou porque protege algo que o pacote AINDA afirma:** a
conferência de que o manifesto do candidato descreve **o próprio** candidato. O
pacote afirma sua identidade — `candidate_digest` recomputado sobre a árvore —, e
`C07` da rodada 7 mediu que a árvore reproduz **com o manifesto mentiroso dentro
dela**. Digest de árvore não detecta isso, e por isso a trava é própria.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PACOTE = Path(__file__).resolve().parents[1]
OPERACIONAIS = PACOTE.parent
DIRETOR = OPERACIONAIS.parent
CEO = DIRETOR.parent
ESTRUTURA = CEO.parent

SCHEMA_PATH = PACOTE / "schemas" / "departamento-auditoria-responsabilidades.schema.json"
CEO_SCHEMA_PATH = CEO / "schemas" / "ceo-maestro.schema.json"
REGRAS_PATH = ESTRUTURA / "regras-de-ouro" / "REGRAS-DE-OURO.md"

sys.path.insert(0, str(ESTRUTURA))
sys.path.insert(0, str(PACOTE / "scripts"))

from _compartilhado.validador_schema import sha256_file, validate_schema  # noqa: E402
from _compartilhado.verificacoes_pacote import (  # noqa: E402
    candidate_digest_de_arvore,
    conferir_manifesto_do_candidato,
    conferir_candidate_digest,
)
from inspecao_executada import (  # noqa: E402
    ALEGACAO_DO_COMPLIANT,
    ESTADOS_BLOQUEANTES,
    EVIDENCE_REF_NAO_RESOLVE,
    NAO_COBERTO_PELA_ALEGACAO,
    auditar_ledger_contra_evidencia,
    consolidar_inspecao,
    cruzar_identidade_dos_recibos,
    decidir_veredito,
    derivar_binario,
    resolver_evidence_refs,
    verificar_inspecao_executada,
)

DEPARTAMENTO = "departamento-auditoria-responsabilidades"

RECEITA_DO_DIGEST = "_compartilhado/verificacoes_pacote.py::digest_de_arvore"

DIMENSOES = (
    "INTENT",
    "AUTH",
    "ESCOPO",
    "PENDING",
    "RACI",
    "RI_RO",
    "SURPRESAS_BYPASS",
    "EVIDENCIA",
    "ARTEFATOS_TWINS",
    "RASTREABILIDADE",
)
DONA = {
    "INTENT": "contrato-e-autoridade",
    "AUTH": "contrato-e-autoridade",
    "ESCOPO": "contrato-e-autoridade",
    "PENDING": "contrato-e-autoridade",
    "RACI": "governanca-e-responsabilidades",
    "RI_RO": "governanca-e-responsabilidades",
    "SURPRESAS_BYPASS": "governanca-e-responsabilidades",
    "EVIDENCIA": "evidencias-e-artefatos",
    "ARTEFATOS_TWINS": "evidencias-e-artefatos",
    "RASTREABILIDADE": "evidencias-e-artefatos",
}
SEGUNDA = {
    "PENDING": "governanca-e-responsabilidades",
    "SURPRESAS_BYPASS": "contrato-e-autoridade",
}

# REESCRITO NA RODADA 5, POR MEDIÇÃO QUE DESMENTIU O ADVÉRBIO.
#
# O texto anterior terminava em "a âncora encarece a fabricação sem impedi-la".
# `OI-04`, produzido por origem independente, mediu o encarecimento: 80 linhas,
# 0,031 s, 1 tentativa. "Encarece" sem número deixava o consumidor calibrar
# confiança por uma estimativa que a medição não sustenta. O número entra e o
# advérbio sai — é a mesma correção que a rodada 4 aplicou à alegação do ADR-018.
TEXTO_R6 = (
    "R6 — a existência do painel auditor não é verificável pelo runtime; sob"
    " porta única a inspeção é executada em papel pela gerente. A âncora NÃO"
    " impede a fabricação, e o custo dela está medido: recibos íntegros que"
    " reabrem foram forjados em 80 linhas e 0,031 s, com 1 tentativa"
    " (OI-04, 2026-08-02)."
)

# RENUMERADO NA RODADA 3, POR COLISÃO ACUSADA PELOS JUÍZES.
#
# Este limite viajava como `R8`, e `R8` já era, na seção 7 do protocolo deste
# mesmo pacote, "bypass para fora". Quem lesse a pendência iria procurar o risco
# errado na tabela. O identificador do limite de pertinência passa a ser `R9`;
# `R8` continua sendo bypass para fora, onde sempre esteve.
TEXTO_R9 = (
    "R9 — a âncora prova que UM arquivo da raiz auditada foi reaberto na versão"
    " declarada; ela NÃO liga a dimensão ao artefato que deveria sustentá-la."
    " Pertinência de evidência é mérito, e mérito é dos Juízes (R5)."
    " (Este limite viajava como R8 até a rodada 3, e colidia com o R8 do §7,"
    " bypass para fora.)"
)

# LIMITE QUE PASSA A VIAJAR NO ENVELOPE, POR EXIGÊNCIA DOS JUÍZES.
#
# A sonda `S14-ENVELOPE-EDITADO` mediu o seguinte: o emissor grava
# `NONCOMPLIANT`, o arquivo é editado em disco depois, e o consumidor lê
# `COMPLIANT`. Nada assina o envelope, e nenhum campo dele prova que foi o
# emissor que o escreveu — nem o emissor nem o validador enxergam a edição.
#
# Até a rodada 2 esse limite existia só no relatório de campanha. Quem lesse o
# envelope na barreira do CEO precisava LEMBRAR dele de fora do artefato, e
# lembrança não é evidência. Agora ele sai em `pending` em toda emissão, ao lado
# de R6 e R9, e viaja com o envelope como o limite de pertinência já viajava.
TEXTO_R10 = (
    "R10 — nada assina este envelope. Edição do arquivo posterior à gravação é"
    " invisível ao emissor E ao validador, e o consumidor pode ler um veredito"
    " que o emissor não produziu. A defesa correspondente é o CONSUMIDOR"
    " recomputar o envelope a partir do ledger e do candidato, e ela mora fora"
    " deste pacote. Medido pela sonda S14-ENVELOPE-EDITADO."
)

# O TETO. RODADA 5.
#
# `R6`, `R9` e `R10` são limites de ALCANCE de travas que existem. `R11` é outra
# coisa: é o limite do MÉTODO INTEIRO, e a razão de a alegação ter sido reduzida
# nesta rodada. Ele viaja no `pending` como os outros, e a alegação viaja em
# campo próprio — quem decide na barreira lê os dois sem reabrir nada.
#
# Ele não é acabamento e nenhuma rodada adicional o fecha dentro deste runtime.
TEXTO_R11 = (
    "R11 — TETO DO MÉTODO: forjar a evidência é chamar as mesmas funções que "
    "a verificam. Derivar da evidência protege contra valor DIGITADO; não "
    "protege contra quem CHAMA o derivador, porque atacante e verificador "
    "compartilham o código, o processo e a árvore. Medido por origem "
    "independente em 2026-08-02 (OI-04): 80 linhas, 0,031 s, 1 tentativa, 4 "
    "arquivos lidos, zero conhecimento do conteúdo auditado. Fechar isto "
    "exige âncora externa ao pacote — runtime separado, assinatura fora da "
    "árvore ou terceiro que não compartilhe o processo — e não cabe no "
    "runtime atual. Este envelope NÃO carrega defesa contra isto e não obriga "
    "nenhuma: a origem independente dos casos foi retirada do envelope na "
    "rodada 8, e o limite permanece ABERTO."
)

# Endereço da alegação, publicado no envelope. Quem quiser conferir que o texto
# do campo é o texto do módulo abre este endereço — a alegação deixa de ser
# string digitada no envelope e passa a ter origem única e conferível, que é
# a regra desta frente desde a rodada 4.
RECEITA_DA_ALEGACAO = "scripts/inspecao_executada.py::ALEGACAO_DO_COMPLIANT"







# ---------------------------------------------------------------------------
# RODADA 9 — A CLÁUSULA DO RECIBO VAI AO CAMINHO DA EMISSÃO
# ---------------------------------------------------------------------------
#
# `C04` da rodada 8: *"o emissor nunca aplica `$defs.auditReceipt` aos recibos em
# disco, e o recibo mudo — contexto sujo declarado sem medição nenhuma —
# atravessa e sai COMPLIANT. Cláusula fora do caminho da emissão é trava sem
# call site."* A cláusula estava certa e vivia só na fixture do validador.
#
# Aqui ela é LIDA DO SCHEMA e aplicada. Não há regra duplicada neste arquivo: a
# fonte continua sendo o schema em disco, e mudança lá é seguida aqui sem edição
# nenhuma. Duplicar a regra seria criar a segunda verdade que esta frente passou
# oito rodadas medindo.
SCHEMA_DO_DEPARTAMENTO = (
    "ceo-maestro/diretor-de-lentes/departamentos-operacionais/"
    "departamento-auditoria-responsabilidades/schemas/"
    "departamento-auditoria-responsabilidades.schema.json"
)
RECIBO_VIOLA_CLAUSULA = "RECIBO_VIOLA_CLAUSULA_DA_CADEIA_DE_REVISAO"
CLAUSULA_NAO_LIDA = "CLAUSULA_DA_CADEIA_DE_REVISAO_NAO_LIDA"


def aplicar_clausula_da_cadeia_de_revisao(
    recibos: list[dict[str, Any]], raiz_auditada: Path
) -> list[str]:
    """Aplica, AOS RECIBOS EM DISCO, a cláusula condicional que o schema declara.

    Percorre `$defs.auditReceipt.properties.review_chain.allOf` e, para cada
    ramo da forma `if {campo: const V} then {required: [N]}`, exige `N` no recibo
    que declara `campo == V`.

    Ausência do schema não vira silêncio: vira erro nomeado. Ausência de
    conferência permanece ausência — é a regra da casa desde a rodada 1.
    """
    caminho = raiz_auditada / SCHEMA_DO_DEPARTAMENTO
    if not caminho.is_file():
        return [f"{CLAUSULA_NAO_LIDA}: schema ausente em {SCHEMA_DO_DEPARTAMENTO}"]
    try:
        schema = json.loads(caminho.read_text(encoding="utf-8"))
        cadeia = schema["$defs"]["auditReceipt"]["properties"]["review_chain"]
    except (OSError, ValueError, KeyError) as erro:
        return [f"{CLAUSULA_NAO_LIDA}: {erro}"]

    ramos = []
    for ramo in cadeia.get("allOf", []):
        gatilho = (ramo.get("if") or {}).get("properties") or {}
        exigidos = (ramo.get("then") or {}).get("required") or []
        for campo, condicao in gatilho.items():
            if "const" in condicao and exigidos:
                ramos.append((campo, condicao["const"], list(exigidos)))
    if not ramos:
        return [
            f"{CLAUSULA_NAO_LIDA}: o schema não declara nenhuma cláusula"
            " condicional em review_chain — não há o que aplicar, e isso é um"
            " defeito do schema, não uma conformidade deste emissor"
        ]

    erros: list[str] = []
    for recibo in recibos:
        auditor = recibo.get("auditor_id", "<sem auditor_id>")
        chain = recibo.get("review_chain")
        if not isinstance(chain, dict):
            erros.append(f"{RECIBO_VIOLA_CLAUSULA}: {auditor} sem review_chain")
            continue
        for campo, valor, exigidos in ramos:
            if chain.get(campo) != valor:
                continue
            for exigido in exigidos:
                if exigido not in chain:
                    erros.append(
                        f"{RECIBO_VIOLA_CLAUSULA}: {auditor} declara"
                        f" {campo}={valor!r} e NÃO traz {exigido!r}. A"
                        " declaração sem a medição ao lado é o recibo MUDO, e"
                        " ele não atravessa a emissão."
                    )
    return erros


def carregar(pasta: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rodada = json.loads((pasta / "rodada.json").read_text(encoding="utf-8"))
    recibos = [
        json.loads(caminho.read_text(encoding="utf-8"))
        for caminho in sorted((pasta / "recibos").glob("*.json"))
    ]
    if not recibos:
        raise SystemExit(f"[ABORTA] nenhum recibo em {pasta / 'recibos'}")
    return rodada, recibos


def resolver_raiz_do_candidato(
    argv: list[str],
    rodada: dict[str, Any],
    raiz_auditada: Path,
) -> tuple[Path | None, str]:
    """Onde está o candidato — **a rodada declara**, o argv apenas sobrepõe.

    Na rodada 1 desta frente a raiz do candidato existia só como quarto argumento
    de `argv`, e a única invocação publicada tinha dois. A trava de identidade
    ficava atrás de `if raiz_do_candidato is not None`, e o caminho documentado
    passava por fora dela **sem dizer nada**. É o achado `A1` do julgamento.

    Aqui a fonte primária é `rodada.json::candidate_root`, que faz parte do
    envelope que a gerente já grava: a forma de dois argumentos passa a acionar a
    conferência. O terceiro argumento continua aceito como sobreposição, e a
    ausência dele **não desliga nada** — quando não há raiz por nenhuma das duas
    vias, o resultado é `NAO_CONFERIDO`, que é um estado com nome, registrado no
    envelope e proibido de coexistir com `COMPLIANT`.

    Devolve `(raiz, origem)`. `origem` é sempre um dos três valores do enum do
    schema, e vai para o envelope: quem lê sabe por onde a raiz chegou.
    """
    if len(argv) == 4:
        return Path(argv[3]).resolve(), "argv[3]"
    declarada = rodada.get("candidate_root")
    if isinstance(declarada, str) and declarada.strip():
        return (raiz_auditada / declarada).resolve(), "rodada.json::candidate_root"
    return None, "ausente"


def conferir_identidade_do_candidato(
    raiz_do_candidato: Path | None,
    origem: str,
    declarado: Any,
    momento: str,
    manifesto: dict[str, Any],
) -> dict[str, Any]:
    """Recomputa o `candidate_digest` sobre a árvore aberta — e **sempre** relata.

    Três resultados, todos nomeados, nenhum silencioso:

    - `CONFERIDO` — recomputou pela receita oficial e bateu;
    - `DIVERGENTE` — recomputou e não bateu: `BLOCKED_CANDIDATE_MISMATCH`, nada é
      auditado, o emissor sai com 2 e não grava envelope nenhum;
    - `NAO_CONFERIDO` — não havia raiz declarada sobre a qual recomputar. O campo
      diz isso, com o motivo, e o schema proíbe `COMPLIANT` neste estado.

    O terceiro é a correção do `A1`: antes, a mesma situação produzia um envelope
    **indistinguível** do conferido, com o digest declarado copiado para dentro do
    relatório como se tivesse sido verificado.
    """
    if raiz_do_candidato is None:
        return {
            "status": "NAO_CONFERIDO",
            "candidate_root_ref": "n/a",
            "source": origem,
            "recipe": RECEITA_DO_DIGEST,
            "recomputed_digest": "n/a",
            "reason": (
                "identidade NAO conferida: a rodada não declara candidate_root e"
                " nenhuma raiz do candidato foi passada; nada foi recomputado"
            ),
            "checked_at": momento,
            "manifest_status": manifesto["status"],
            "manifest_reason": manifesto["reason"],
            "errors": [],
        }

    erros = conferir_candidate_digest(raiz_do_candidato, declarado)
    # O digest RECOMPUTADO passa a ser um campo, e não um valor que só existe
    # dentro da comparação. Sem ele, o que viaja ao CEO é sempre o **declarado**,
    # e "conferido" fica sendo uma palavra sobre um número que ninguém publicou.
    # Com ele, o consumidor tem o que repetir.
    recomputado = (
        candidate_digest_de_arvore(raiz_do_candidato)
        if raiz_do_candidato.is_dir()
        else "n/a"
    )
    if erros:
        return {
            "status": "DIVERGENTE",
            "candidate_root_ref": str(raiz_do_candidato),
            "source": origem,
            "recipe": RECEITA_DO_DIGEST,
            "recomputed_digest": recomputado,
            "reason": "identidade divergente: " + "; ".join(erros),
            "checked_at": momento,
            "manifest_status": manifesto["status"],
            "manifest_reason": manifesto["reason"],
            "errors": erros,
        }
    return {
        "status": "CONFERIDO",
        "candidate_root_ref": str(raiz_do_candidato),
        "source": origem,
        "recipe": RECEITA_DO_DIGEST,
        "recomputed_digest": recomputado,
        "reason": (
            "identidade conferida: candidate_digest recomputado sobre a árvore"
            f" aberta pela receita {RECEITA_DO_DIGEST} e idêntico ao declarado"
        ),
        "checked_at": momento,
        "manifest_status": manifesto["status"],
        "manifest_reason": manifesto["reason"],
        "errors": [],
    }


def montar_matriz(
    rodada: dict[str, Any],
    estados: dict[str, str],
    recibos: list[dict[str, Any]],
) -> dict[str, Any]:
    """A matriz é montada a partir dos estados EFETIVOS, nunca dos declarados."""
    refs = sorted({recibo["task_id"] for recibo in recibos})
    linhas = []
    for dimensao in DIMENSOES:
        estado = estados.get(dimensao, "NAO_PROVADO")
        ancoras: list[str] = []
        for recibo in recibos:
            for linha in recibo.get("dimension_states", []):
                if linha.get("dimension") != dimensao:
                    continue
                for ancora in linha.get("evidence_anchors", []):
                    if ancora["evidence_ref"] not in ancoras:
                        ancoras.append(ancora["evidence_ref"])
        linhas.append(
            {
                "dimension": dimensao,
                "state": estado,
                "owner_capability": DONA[dimensao],
                "secondary_capability": SEGUNDA.get(dimensao, "n/a"),
                "receipt_refs": refs,
                "reason": (
                    f"Estado efetivo de {dimensao} após reabertura das âncoras."
                    if estado != "NAO_PROVADO"
                    else f"{dimensao} sem inspeção executada que reabra."
                ),
                "evidence_refs": ancoras,
            }
        )
    return {
        "artifact_type": "CONFORMITY_MATRIX",
        "conformity_matrix_id": rodada["conformity_matrix_id"],
        "causal": rodada["causal"],
        "department_mission_ref": rodada["department_mission_ref"],
        "dimensions": linhas,
        "divergences": rodada.get("divergences", []),
        "created_at": rodada["recorded_at"],
    }


def montar_alegacao() -> dict[str, Any]:
    """A alegação, montada das CONSTANTES do módulo da trava — nunca digitada.

    `certifies` e `does_not_certify` são `const` no schema do CEO e no do
    departamento. Alargar a alegação passa a exigir **duas edições, em dois
    arquivos**: a constante aqui e o `const` lá. Uma só derruba a emissão.
    """
    return {
        "certifies": ALEGACAO_DO_COMPLIANT,
        "does_not_certify": NAO_COBERTO_PELA_ALEGACAO,
        "ceiling_ref": "R11",
        "source": RECEITA_DA_ALEGACAO,
    }


def montar_ledger(
    rodada: dict[str, Any],
    recibos: list[dict[str, Any]],
    relatorio: dict[str, Any],
    identidade: dict[str, Any],
    verificacao: dict[str, Any],
    refs_resolvidos: list[str],
) -> dict[str, Any]:
    # ---- A ORDEM É A DA DECISÃO -------------------------------------------
    # Os estados vêm de `relatorio["effective_states"]`, que é a saída da trava.
    # Nenhum ramo deste emissor lê `dimension_states[].state` para decidir.
    #
    # `validate_call_site` confere isto por FLUXO DE DADOS: os parâmetros
    # `relatorio` e `identidade` são as sementes, e `governance_verdict`,
    # `candidate_identity` e cada número de `inspection_verification` têm de
    # descender delas. Manter o subscrito e decidir por outra coisa fica
    # vermelho — foi o que a variante inerte de `M10` explorou na rodada 1.
    estados = {
        dimensao: relatorio["effective_states"].get(dimensao, "NAO_PROVADO")
        for dimensao in DIMENSOES
    }
    veredito = decidir_veredito(estados)
    binario = derivar_binario(veredito)

    violacoes = [
        f"{dimensao}: {estados[dimensao]} — dimensão bloqueada, dono "
        f"{DONA[dimensao]}."
        for dimensao in DIMENSOES
        if estados[dimensao] in ESTADOS_BLOQUEANTES
    ]
    ressalvas = [
        {
            "dimension": dimensao,
            "owner_role": rodada.get("ressalva_owner", "diretor-de-lentes"),
            "impact": f"Achado não bloqueante registrado em {dimensao}.",
            "closing_condition": rodada.get(
                "ressalva_closing", "Fechar o achado e reexecutar a inspeção."
            ),
        }
        for dimensao in DIMENSOES
        if estados[dimensao] == "RESSALVA"
    ]

    achados = [
        achado for recibo in recibos for achado in recibo.get("findings", [])
    ]

    painel = [
        {
            "auditor_id": recibo["auditor_id"],
            "capability": recibo["capability"],
            "status": recibo["status"],
            # RODADA 8 — o contexto do revisor deixa de ser `const true` no
            # schema e passa a ser MEDIDO. O painel transporta o que o recibo
            # declarou, para que contexto sujo seja legível na barreira em vez
            # de empurrar o inspetor honesto para fora do formato.
            "context_clean": bool(recibo["review_chain"]["context_clean"]),
            # RODADA 9 — a independência MEDIDA viaja junto. Enquanto era
            # `const true`, o campo era garantia de FORMA e de nada mais: nenhum
            # recibo podia dizer o contrário, então o valor `true` no envelope
            # não informava coisa alguma. Agora informa.
            "independent": bool(recibo["review_chain"]["independent"]),
            "substrate": rodada.get("substrate", "desconhecido"),
            "tier": rodada.get("tier", "desconhecido"),
        }
        for recibo in recibos
    ]
    execucoes = [
        {
            "task_id": recibo["task_id"],
            "auditor_id": recibo["auditor_id"],
            "capability": recibo["capability"],
            "execution_mode": recibo["method"]["execution_mode"],
            "agent_contract_ref": recibo["method"]["agent_contract_ref"],
            "agent_contract_digest": recibo["method"]["agent_contract_digest"],
            "executed_at": recibo["review_chain"]["reviewed_at"],
            "destination": f"recibos/{recibo['task_id']}.json",
        }
        for recibo in recibos
    ]
    # `method_executions` **descende dos recibos**, e é isso que o validador
    # confere. O `agent_contract_digest` que sai daqui é o declarado no recibo —
    # e ele não é aceito por declaração: `conferir_metodo` reabriu o contrato do
    # agente em disco e recomputou o SHA-256 antes de qualquer estado sobreviver.
    # Divergência já rebaixou a dimensão para `NAO_PROVADO` e contou em
    # `methods_failed`. O campo aqui é transporte do que a trava já validou, não
    # uma segunda afirmação — e é por isso que ele fica.
    atribuicoes = [
        {
            "task_id": execucao["task_id"],
            "auditor_id": execucao["auditor_id"],
            "capability": execucao["capability"],
            "issued_at": execucao["executed_at"],
            "destination": execucao["destination"],
        }
        for execucao in execucoes
    ]

    identidade_no_ledger = {
        "status": identidade["status"],
        "candidate_root_ref": identidade["candidate_root_ref"],
        "source": identidade["source"],
        "recipe": identidade["recipe"],
        "recomputed_digest": identidade["recomputed_digest"],
        "reason": identidade["reason"],
        "checked_at": identidade["checked_at"],
        "manifest_status": identidade["manifest_status"],
        "manifest_reason": identidade["manifest_reason"],
    }

    pendencias = [TEXTO_R6, TEXTO_R9, TEXTO_R10, TEXTO_R11] + [
        f"Ressalva em {item['dimension']}: {item['closing_condition']}"
        for item in ressalvas
    ]
    # A ausência de conferência de identidade é PENDÊNCIA nomeada, além de campo
    # próprio: o schema já bloqueia o `COMPLIANT`, e quem lê o `pending` vê a
    # razão sem precisar cruzar dois documentos.
    if identidade_no_ledger["status"] != "CONFERIDO":
        pendencias.append(
            "Identidade do candidato "
            f"{identidade_no_ledger['status']}: {identidade_no_ledger['reason']}"
        )
    for rebaixamento in relatorio["downgrades"]:
        # O `auditor_id` entra no texto porque `PENDING` e `SURPRESAS_BYPASS`
        # têm dois inspetores: sem ele as duas linhas ficariam idênticas, o
        # schema recusaria por `uniqueItems` — e, pior, o registro esconderia
        # qual das duas inspeções não foi executada.
        pendencias.append(
            f"Rebaixada {rebaixamento['dimension']} de {rebaixamento['declarado']}"
            f" para {rebaixamento['efetivo']} no papel de"
            f" {rebaixamento['auditor_id']}: {rebaixamento['motivo']}."
        )
    # Rede de segurança: pendência repetida não acrescenta informação e o schema
    # a recusa. Deduplicar preservando a ordem nunca apaga conteúdo distinto.
    pendencias = list(dict.fromkeys(pendencias))

    return {
        "artifact_type": "AUDIT_LEDGER",
        "audit_ledger_id": rodada["audit_ledger_id"],
        "causal": rodada["causal"],
        "department_mission_ref": rodada["department_mission_ref"],
        "dossier_missing": rodada.get("dossier_missing", []),
        "assignments": atribuicoes,
        "method_executions": execucoes,
        "candidate_identity": identidade_no_ledger,
        # A ALEGAÇÃO VIAJA COM O ARTEFATO. Rodada 5, frente A.
        "compliance_claim": montar_alegacao(),
        # OS NÚMEROS SÃO CONTADOS, NÃO LIDOS.
        #
        # Cada subcampo desce de `verificacao`, que é o retorno de
        # `consolidar_inspecao` — e lá `anchors_total` e `methods_total` saem de
        # `contar_ancoras_declaradas` sobre os recibos em disco. Nenhum deles é
        # subscrito de `relatorio`. Foi o subscrito de `relatorio` que a lavagem
        # interprocedural da rodada 3 imitou para gravar `anchors_total: 12`
        # sobre zero âncoras.
        "inspection_verification": {
            "all_anchors_reverified": verificacao["all_anchors_reverified"],
            "anchors_total": verificacao["anchors_total"],
            "anchors_failed": verificacao["anchors_failed"],
            "methods_total": verificacao["methods_total"],
            "methods_failed": verificacao["methods_failed"],
            "counted_by": verificacao["counted_by"],
            "counted_limit": verificacao["counted_limit"],
            "verified_by": "scripts/inspecao_executada.py::verificar_inspecao_executada",
            "verified_at": rodada["recorded_at"],
        },
        "panel": painel,
        "conformity_matrix": montar_matriz(rodada, estados, recibos),
        "findings": achados,
        "internal_verdict": veredito,
        "governance_verdict": binario,
        "violations": violacoes,
        "ressalvas": ressalvas,
        "capability_gaps": rodada.get("capability_gaps", []),
        # RODADA 6: o que viaja é a lista RESOLVIDA, saída de
        # `resolver_evidence_refs` sobre a raiz auditada — não o subscrito de
        # `rodada`. Enquanto o valor era lido daqui, `OI5-04` fazia uma lista
        # digitada apontando para arquivo inexistente chegar ao envelope do CEO.
        "evidence_refs": refs_resolvidos,
        "executive_decisions_required": rodada.get("executive_decisions_required", []),
        "pending": pendencias,
        "return_to": "diretor-de-lentes",
        "recorded_at": rodada["recorded_at"],
    }


def derivar_independencia_do_painel(painel: list[dict[str, Any]]) -> str:
    """`INDEPENDENTE` só quando TODO inspetor do painel foi medido independente.

    T71. O painel não atravessa a fronteira — `governanceReport` não o carrega e
    `additionalProperties: false` o proíbe —, então o que viaja é este escalar, e
    ele é **derivado do painel**, nunca digitado. Digitar aqui seria a segunda
    fonte que diverge da primeira em silêncio, defeito que a rodada 4 já corrigiu
    no `pending` e a rodada 5 no `compliance_claim`.

    O `if` do painel vazio não é defensivo, é a armadilha: `all([])` é **True**,
    e sem ele um ledger sem inspetor nenhum sairia `INDEPENDENTE`. Ausência de
    inspetor não é independência — ausência de evidência permanece ausência.
    """
    if not painel:
        return "NAO_INDEPENDENTE"
    return (
        "INDEPENDENTE"
        if all(bool(inspetor.get("independent")) for inspetor in painel)
        else "NAO_INDEPENDENTE"
    )


def derivar_relatorio_de_governanca(
    ledger: dict[str, Any],
    rodada: dict[str, Any],
) -> dict[str, Any]:
    """O envelope que o CEO lê na barreira — **derivado do ledger, sempre**.

    Duas correções da rodada 4, as duas da mesma família:

    1. **`candidate_digest` deixa de ser o declarado.** Quando a identidade foi
       conferida, o que viaja é o digest **recomputado** sobre a árvore aberta —
       o mesmo número, por construção, e essa é a questão: se algum dia não for o
       mesmo, o emissor já terá recusado. Quando não foi conferida, viaja o
       declarado, porque não há outro, e o `candidate_identity_status` ao lado diz
       exatamente isso. Antes, os dois casos escreviam a mesma coisa.
    2. **`pending` passa a existir neste envelope.** Os Juízes acusaram, em duas
       óticas independentes, que a `SKILL.md` afirmava que quem lê na barreira lê
       os três limites *no próprio artefato* — e o artefato lido é este, que não
       tinha `pending`, e cujo schema o proibia (`additionalProperties: false`).
       Ou o limite alcança o envelope, ou a frase sai. Escolhemos o limite.
    """
    identidade = ledger["candidate_identity"]
    conferido = identidade["status"] == "CONFERIDO"
    return {
        "report_id": rodada["report_id"],
        "auditor_ref": DEPARTAMENTO,
        "auditor_digest": sha256_file(PACOTE / "SKILL.md"),
        "candidate_digest": (
            identidade["recomputed_digest"]
            if conferido
            else ledger["causal"]["candidate_digest"]
        ),
        # O CEO lê o binário na barreira. Se a identidade do candidato não foi
        # conferida, ele precisa ver isso **no mesmo envelope**, e não deduzir de
        # um silêncio. O schema do CEO exige CONFERIDO para COMPLIANT.
        "candidate_identity_status": identidade["status"],
        # RODADA 8 — o estado do manifesto viaja ao lado do da identidade.
        # Sem ele, quem decide na barreira não distingue um pacote que se
        # identifica de um que carrega o manifesto de outro candidato.
        "candidate_manifest_status": identidade["manifest_status"],
        # T71 — a independência do painel também. O contrato promete recibo
        # INDEPENDENTE como condição de veredito positivo, e até aqui nenhuma
        # cláusula do COMPLIANT lia `panel[].independent`: o campo era preenchido
        # e jamais lido, então recibo não independente fechava COMPLIANT do mesmo
        # jeito. O painel fica no ledger; o que atravessa é o escalar DERIVADO
        # dele, e o schema do CEO exige INDEPENDENTE para COMPLIANT.
        "panel_independence_status": derivar_independencia_do_painel(ledger["panel"]),
        "candidate_digest_source": (
            "RECOMPUTADO" if conferido else "DECLARADO_NAO_CONFERIDO"
        ),
        "contract_digest": ledger["causal"]["contract_digest"],
        "rules_digest": sha256_file(REGRAS_PATH),
        "verdict": ledger["governance_verdict"],
        "violations": ledger["violations"],
        "evidence_refs": ledger["evidence_refs"],
        # ------------------------------------------------------------------
        # O LIMITE VIAJA. Rodada 5, e é a exigência central da missão.
        # ------------------------------------------------------------------
        # `R6`, `R9` e `R10` chegaram ao envelope na rodada 4, e chegaram por
        # `pending` — uma lista de strings que quem decide precisa ler inteira
        # para achar o que importa. O TETO do método é outra coisa: ele governa
        # o que o binário ao lado significa, e por isso sai em campo próprio,
        # com `certifies` e `does_not_certify` lado a lado.
        #
        # Os dois textos descem de `ledger["compliance_claim"]`, que desce das
        # constantes do módulo da trava. Digitar a alegação aqui seria uma
        # segunda fonte que poderia divergir da primeira em silêncio — foi
        # exatamente esse o defeito que a rodada 4 corrigiu no `pending`.
        "compliance_claim": ledger["compliance_claim"],
        # Os limites viajam COM o envelope, e são os do ledger — não uma segunda
        # lista digitada aqui, que poderia divergir dele em silêncio.
        "pending": ledger["pending"],
        "issued_at": ledger["recorded_at"],
    }


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 4):
        print(__doc__)
        return 2
    pasta = Path(argv[1]).resolve()
    raiz_auditada = Path(argv[2]).resolve()

    rodada, recibos = carregar(pasta)

    # ---------------------------------------------------------------------
    # CALL SITE DA RECEITA DE DIGEST — lado do CONSUMIDOR, SEM CONDIÇÃO.
    # ---------------------------------------------------------------------
    # As duas chamadas abaixo estão no corpo de `main`, fora de qualquer `if`.
    # É de propósito, e o validador confere: `validate_identidade_nao_opcional`
    # reprova qualquer aninhamento delas sob condição que fale de `argv`.
    #
    # Foi a ausência desta conferência que deixou dois digests em disputa
    # atravessarem a tarefa 14 inteira; e foi a **opcionalidade** dela que, na
    # rodada 1 da tarefa 15, deixou o caminho documentado gravar `sha256:ffff…`
    # como se fosse identidade conferida.
    raiz_do_candidato, origem_da_raiz = resolver_raiz_do_candidato(
        argv, rodada, raiz_auditada
    )
    # ---------------------------------------------------------------------
    # RODADA 8 — O MANIFESTO DESCREVE O PRÓPRIO CANDIDATO, OU NADA É AUDITADO.
    # ---------------------------------------------------------------------
    # `C07` da rodada 7: a árvore do candidato entregue REPRODUZIA e o manifesto
    # dentro dela declarava outro candidato, com 8 de 13 hashes de outro overlay.
    # `conferir_identidade_do_candidato`, logo acima, é cega para isso por
    # construção: ela confere o conjunto de bytes, e a declaração falsa É um dos
    # bytes. A conferência é aqui, fora de qualquer `if`, e antes de o ledger
    # existir.
    manifesto = conferir_manifesto_do_candidato(raiz_do_candidato)
    if manifesto["status"] == "DIVERGENTE":
        print("[BLOCKED_MANIFESTO_NAO_DESCREVE_O_PROPRIO_CANDIDATO] nada é auditado:")
        for erro in manifesto["errors"]:
            print(f"         {erro}")
        return 2
    if manifesto["status"] == "SEM_MANIFESTO":
        print(f"[MANIFESTO_NAO_CONFERIDO] {manifesto['reason']}")

    identidade = conferir_identidade_do_candidato(
        raiz_do_candidato,
        origem_da_raiz,
        rodada["causal"]["candidate_digest"],
        rodada["recorded_at"],
        manifesto,
    )
    if identidade["status"] == "DIVERGENTE":
        print("[BLOCKED_CANDIDATE_MISMATCH] nada é auditado:")
        for erro in identidade["errors"]:
            print(f"         {erro}")
        return 2
    if identidade["status"] == "NAO_CONFERIDO":
        print(f"[IDENTIDADE_NAO_CONFERIDA] {identidade['reason']}")

    # ---------------------------------------------------------------------
    # CRUZAMENTO DE IDENTIDADE DOS RECIBOS — sem condição, antes da trava.
    # ---------------------------------------------------------------------
    # O recibo declara sobre qual candidato e sob qual contrato inspecionou, e
    # até a rodada 3 ninguém comparava com a rodada. Recibo de outro candidato
    # entrava na matriz calado. É a mesma classe do ledger que declarou o digest
    # do `cand-B` enquanto o julgado era o `cand-C`.
    erros_de_recibo = cruzar_identidade_dos_recibos(
        recibos,
        rodada["causal"]["candidate_digest"],
        rodada["causal"]["contract_digest"],
    )
    if erros_de_recibo:
        print("[BLOCKED_RECEIPT_IDENTITY_MISMATCH] nada é auditado:")
        for erro in erros_de_recibo:
            print(f"         {erro}")
        return 2

    # ---------------------------------------------------------------------
    # RODADA 6, OI5-04 — CADA evidence_ref RESOLVE, OU NADA É AUDITADO.
    # ---------------------------------------------------------------------
    # `rodada["evidence_refs"]` era transportado para o `AUDIT_LEDGER` e para o
    # `GOVERNANCE_REPORT` sem que nada o confrontasse. O caso `OI5-04` apontou a
    # lista para um arquivo inexistente e ela atravessou num `COMPLIANT` exit 0,
    # com a alegação da rodada impressa ao lado — 15 de 15 ataques passaram.
    #
    # A conferência é aqui, fora de qualquer `if`, e ANTES de o ledger existir:
    # referência que não resolve não vira ressalva nem pendência, ela BLOQUEIA.
    # A raiz é a auditada, que é contra o que a âncora já era reaberta — a mesma
    # régua, aplicada a um campo que escapava dela.
    refs_resolvidos, erros_de_referencia = resolver_evidence_refs(
        rodada.get("evidence_refs"), raiz_auditada
    )
    if erros_de_referencia:
        print(f"[BLOCKED_{EVIDENCE_REF_NAO_RESOLVE}] nada é auditado:")
        for erro in erros_de_referencia:
            print(f"         {erro}")
        return 2

    # ---------------------------------------------------------------------
    # RODADA 9 — A CLÁUSULA DO RECIBO, NO CAMINHO DA EMISSÃO, SEM CONDIÇÃO.
    # ---------------------------------------------------------------------
    # Fora de qualquer `if`, e antes de o ledger existir. O recibo mudo bloqueia
    # aqui, e não só na fixture de um validador que ninguém roda na emissão.
    #
    # A POSIÇÃO É DELIBERADA, e a primeira tentativa a errou. Esta conferência
    # entra DEPOIS das travas de identidade — digest, manifesto, identidade do
    # candidato, identidade dos recibos e `evidence_refs`. Colocada antes delas,
    # ela roubava o bloqueio: o caso `o caminho documentado, executado, barra
    # digest falso` passou a bloquear pelo motivo ERRADO e a bateria acusou.
    # Bloquear cedo não é bloquear melhor — o motivo publicado tem de ser o
    # motivo verdadeiro.
    erros_de_cadeia = aplicar_clausula_da_cadeia_de_revisao(recibos, raiz_auditada)
    if erros_de_cadeia:
        print(f"[BLOCKED_{RECIBO_VIOLA_CLAUSULA}] nada é auditado:")
        for erro in erros_de_cadeia:
            print(f"         {erro}")
        return 2


    # ---------------------------------------------------------------------
    # CALL SITE DA TRAVA — aqui, antes de qualquer estado ser consolidado.
    # ---------------------------------------------------------------------
    relatorio = verificar_inspecao_executada(recibos, raiz_auditada)

    for falha in relatorio["failures"]:
        print(f"[INSPECAO] {falha}")
    for rebaixamento in relatorio["downgrades"]:
        print(
            f"[REBAIXA] {rebaixamento['dimension']}: "
            f"{rebaixamento['declarado']} -> {rebaixamento['efetivo']}"
            f" ({rebaixamento['motivo']})"
        )

    # ---------------------------------------------------------------------
    # CONTAGEM — o número vai ao envelope CONTADO, e as duas medidas se cruzam.
    # ---------------------------------------------------------------------
    verificacao, divergencias_da_contagem = consolidar_inspecao(recibos, relatorio)
    if divergencias_da_contagem:
        print("[BLOCKED_ANCHOR_COUNT_MISMATCH] nada é auditado:")
        for divergencia in divergencias_da_contagem:
            print(f"         {divergencia}")
        return 2

    ledger = montar_ledger(
        rodada, recibos, relatorio, identidade, verificacao, refs_resolvidos
    )

    # ---------------------------------------------------------------------
    # AUDITORIA DO ARTEFATO CONTRA A EVIDÊNCIA — a trava de CLASSE.
    # ---------------------------------------------------------------------
    # As travas anteriores vigiam o caminho: quem chamou quem, e se o valor
    # desceu de onde deveria. Caminho sempre admite mais uma função no meio que
    # preserva a cadeia de nomes e troca o valor — foi assim no nível 2 e no
    # nível 6. Esta aqui não vigia caminho: pega o ledger PRONTO e refaz a conta
    # a partir dos recibos em disco. Lavagem em qualquer ponto produz artefato
    # que não bate com a evidência que ele afirma resumir.
    # A RAIZ É PASSADA, e é obrigatória. Sem ela não há reabertura, e sem
    # reabertura os estados da matriz voltariam a ser conferidos contra si
    # mesmos — que é o `OI-01`. Raiz opcional seria a opcionalidade por aridade
    # do achado `A1`, na função que existe justamente para não repetir a classe.
    divergencias_do_artefato = auditar_ledger_contra_evidencia(
        ledger, recibos, raiz_auditada
    )
    if divergencias_do_artefato:
        print("[BLOCKED_LEDGER_EVIDENCE_MISMATCH] nada é auditado:")
        for divergencia in divergencias_do_artefato:
            print(f"         {divergencia}")
        return 2

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    # Valida contra o `$defs` NOMEADO, nunca contra o `oneOf` da raiz. O `oneOf`
    # só sabe dizer "não casou com nenhuma alternativa", e foi assim que o
    # baseline vermelho-verde da tarefa 14 registrou o mesmo erro opaco nos cinco
    # casos, escondendo que duas sondas eram a mesma. Achado 5.2b daquela
    # auditoria, aplicado aqui.
    erros = validate_schema(ledger, schema["$defs"]["auditLedger"], schema)
    if erros:
        print("[ABORTA] o AUDIT_LEDGER não passa no próprio schema:")
        for erro in erros:
            print(f"         {erro}")
        return 2

    relatorio_governanca = derivar_relatorio_de_governanca(ledger, rodada)
    ceo_schema = json.loads(CEO_SCHEMA_PATH.read_text(encoding="utf-8"))
    erros = validate_schema(
        relatorio_governanca, ceo_schema["$defs"]["governanceReport"], ceo_schema
    )
    if erros:
        print("[ABORTA] o GOVERNANCE_REPORT não passa no schema do CEO:")
        for erro in erros:
            print(f"         {erro}")
        return 2

    # Grava ANTES de devolver texto. Artefato primeiro, relato depois.
    (pasta / "AUDIT-LEDGER.json").write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (pasta / "GOVERNANCE-REPORT.json").write_text(
        json.dumps(relatorio_governanca, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # O sumário imprime o que FOI GRAVADO, não uma segunda leitura da trava.
    # Imprimir `relatorio[...]` aqui era divergir do envelope sem avisar: era
    # exatamente o console dizendo `âncoras 0/0` enquanto o ledger gravava
    # `anchors_total: 12`, na lavagem que os Juízes plantaram. O número exibido
    # passa a ser o do envelope, e vem rotulado com a origem.
    gravado = ledger["inspection_verification"]
    print(
        f"\nveredito interno: {ledger['internal_verdict']}"
        f" | binário: {ledger['governance_verdict']}"
        f" | identidade: {ledger['candidate_identity']['status']}"
        f" ({ledger['candidate_identity']['source']})"
        f" | âncoras {gravado['anchors_total'] - gravado['anchors_failed']}"
        f"/{gravado['anchors_total']} reabertas (contadas por"
        f" {gravado['counted_by']})"
        f" | métodos {gravado['methods_total'] - gravado['methods_failed']}"
        f"/{gravado['methods_total']} conferidos"
    )
    # A ALEGAÇÃO IMPRESSA É A DO ENVELOPE, e é a do envelope porque desce dele.
    # Quem rodou o comando lê na tela exatamente o que o CEO lê na barreira —
    # console e envelope não podem divergir, nem no veredito nem no que ele
    # significa.
    alegacao = relatorio_governanca["compliance_claim"]
    print(f"\n  certifica:     {alegacao['certifies']}")
    print(f"  NÃO certifica: {alegacao['does_not_certify']}")
    print(f"  teto:          {alegacao['ceiling_ref']} (ver pending do envelope)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
