# JUDGE_OPINION — CRIT-06 · ótica `robustez-e-evidencia` (instância própria)

- `data`: **2026-07-28**
- `criterion_id`: **CRIT-06**
- `owner_lens`: `agente-julgar-robustez-e-evidencia`
- `candidate_tree_sha256`: `bbcae76833d7d54d051af903b7949e478272c720743cd176c1a0c1acc3fd4f58`
  (25 arquivos, manifesto 2649 bytes) · `evals/PLACAR.md` =
  `b4d60fe694a4e83b03a2f64c16fc96e2143129ca97d40c3ea3960dc6160f1bf8`
- `candidato`: `.claude/skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-inovacao-melhoria`
  (cópia de runtime; digest recebido do topo, não recalculado aqui)
- `rodada_anterior`: rodada 3, mesma ótica, CRIT-06 = **6**, `paragraph_12_ruling: EVASION`
- `return_to`: `departamento-juizes` · escala inteira 0–10 · sem veredito, sem consolidação

## Nota — **8** · banda `ACEITO_USO_INTERNO` (ADR-014)

`r9_fecha_a_lacuna`: **sim** · `evasao_reincidente`: **false**

---

## 1. As duas afirmações da rodada, conferidas uma a uma

### Afirmação 1 — "o item voltou para a seção de limites e cita R9, risco novo do §12"

**Confirmada, com um defeito de forma.**

O item voltou, com o identificador colado no título
(`evals/PLACAR.md:93`):

> `1. **Acionamento espontâneo — `SKIP` (**R9**).** Nenhuma bateria provou que **este pacote** dispara sozinho a partir do gatilho.`

E o `R9` existe no §12 do protocolo
(`references/protocolo-inovacao-melhoria.md:444`), com as quatro colunas da tabela
preenchidas:

> `| **R9** acionamento espontâneo não é verificável neste pacote | a Estrutura instala **uma porta única**: … `departamento=0 ; agente=0`. Este Departamento é um dos 15 | nenhuma bateria prova que a skill dispara sozinha … | declarar o `SKIP` em vez de simulá-lo, e nomear delegação como delegação nos forward tests | fecha só se a instalação mudar — decisão de runtime, fora do alcance deste protocolo |`

O `**Concluído quando:**` da seção foi ajustado junto (`:453-456`): *"nomeia pelo
identificador cada um dos demais limites de que a rodada dependa (R1–R4, **R6–R9**)"*.
A varredura do pacote confirma que a seção de riscos residuais continua existindo em
**um único arquivo** (`references/protocolo-inovacao-melhoria.md:427`) — nenhum outro
`.md` do candidato traz o cabeçalho.

**Defeito de forma:** a linha 443 do protocolo está **vazia**. Em Markdown, isso encerra
a tabela iniciada em `:433`; o `R9` de `:444` renderiza como **parágrafo solto de texto com
barras verticais**, fora da tabela onde R1–R8 moram. O `protocol_errors` não percebe,
porque varre linha a linha (`validate_workflow.py:1605-1609`, `line.startswith("| **R")`)
e não conhece a semântica de tabela. O risco que fecha a lacuna é, no documento renderizado,
o único que não está na tabela do §12.

### Afirmação 2 — "a ligação item↔`R` é conferida em código, com o conjunto de `R` lido do próprio §12"

**Confirmada.** A função existe, é chamada e não é uma lista fixa.

- `evals/validate_workflow.py:1638` — `placar_errors()` passou a chamar
  `errors.extend(limites_ligados_a_risco_errors(text))`; o `check(...)` correspondente está
  em `:1919-1920`.
- `:1667` — o conjunto válido é derivado do protocolo, não escrito no validador:
  `declarados = set(re.findall(r"\*\*(R\d+)\*\*", protocolo[match.end():]))`.
- `:1680-1694` — cada item enumerado da seção é percorrido; item sem `R` gera
  `"placar: item de não-provado sem identificador de risco — …"`, e `R` que o protocolo
  não declara gera `"placar: item cita risco não declarado no protocolo …"`.

Aplicada ao texto atual, a checagem cobre os **8** itens (`PLACAR.md:93-117`), que citam
`R9, R4, R4, R7, R2, R3, R5, R6` — todos resolvem no §12. A cláusula, que na rodada 3
fechava para sete de oito, **fecha para oito de oito**.

**Onde a trava é mais estreita do que a própria docstring anuncia.** O comentário de
`:1652-1654` afirma: *"O operador 'consertou' movendo um item para uma gaveta nova em vez
de fechar a lacuna, e nada acusou. … esta função existe para que a próxima tentativa falhe
alto."* Conferido no código, ela falha alto em **duas** das três classes:

1. **Item que fica na seção sem `R`** → pega. **Item que cita `R` inexistente** → pega.
2. **Item retirado da seção** → **não pega.** O recorte é `find("## O que ainda não foi
   provado")` até o próximo `\n## ` (`:1671-1676`); o que for movido para uma seção `##`
   irmã fica invisível. O único anteparo contra isso é a string literal `"pendente de
   execução"` (`:1634`) — que não casa com "prova pendente", "pendências de prova" ou
   qualquer sinônimo. A maneira exata da rodada 3 continua dependendo de juiz humano,
   não de código, se a gaveta nova for um `##` de topo.
3. **`R` mintado em prosa** → não pega. `:1667` aceita qualquer `**Rn**` em **negrito** depois
   do cabeçalho do §12, inclusive dentro do blockquote explicativo (`protocolo:446`). Um
   `R10` citado só numa frase, sem linha de tabela, sem vetor, sem teto, passaria a ser
   identificador "válido". Hoje é latente — o `R9` tem a linha —, mas é a diferença entre
   *ler o §12* e *ler a tabela do §12*.
4. **Último item da seção absorve o rodapé.** `:1686` estende o corpo do último item até o
   fim do recorte, então o parágrafo `**Contagem:**` (`PLACAR.md:119-123`), que nomeia nove
   identificadores, pertence ao item 8. Enquanto esse parágrafo existir, o último item da
   lista **não tem como reprovar**.

---

## 2. A pergunta central — R9 fecha a lacuna, ou é a mesma evasão de outra roupa?

**Fecha.** Aplicando o critério de discernimento, cláusula por cláusula:

| exigência de um risco residual legítimo | R9 (`protocolo:444`) | veredito |
|---|---|---|
| nomeia a **causa** | porta única: `ceo-maestro` registra, "os 15 gerentes e 66 agentes aninhados **não** viram skills invocáveis — medido em sessão nova, `departamento=0 ; agente=0`" | cumpre, e é **medição**, não suposição |
| nomeia o **efeito** | "nenhuma bateria prova que a skill dispara sozinha a partir do gatilho: ela só é alcançada por delegação explícita, que é outra coisa" | cumpre |
| nomeia **o que se faz enquanto existe** | "declarar o `SKIP` em vez de simulá-lo, e nomear delegação como delegação nos forward tests" | cumpre, e é verificável: o `SKIP` está declarado em `PLACAR.md:62-63` e `FORWARD-TEST.md:15-17` |
| nomeia a **condição de fechamento** | "fecha só se a instalação mudar — decisão de runtime, fora do alcance deste protocolo" | cumpre, e **não é vazia nem tautológica** |

A condição de fechamento é **externa, observável e falsificável**: se a Estrutura deixar de
instalar por porta única e este Departamento virar skill registrada, a medição passa a ser
possível e o `R9` cai. Não é "fecha quando decidirmos que fechou". Não é "fecha quando
alguém reler o item". E, decisivo: **o item continua na seção de não-provado, continua
`SKIP`, e a Decisão continua declarando oito limites** (`PLACAR.md:127-128`). Nada foi
convertido em "está tudo bem".

**Por que isto não é a evasão da rodada 3.** A rodada 3 tirou o item da seção e o rebatizou
"prova pendente"; a lacuna mudou de gaveta. Aqui o item **voltou para a gaveta certa** e
quem mudou foi o **§12** — que é exatamente o remédio que o parecer anterior prescreveu ao
escrever que o item *"exigiria abrir um `R9` no §12, já que o §12 proíbe declarar limite
fora dele"* (parecer rodada 3, linhas 60-62). O operador fez a coisa cara em vez da barata.
Registro também que os três defeitos que a rodada 3 apontou na justificativa antiga
sumiram: não há mais citação pela metade da definição do §12, não há mais fechador
inventado ("uma rodada de forward contra o pacote instalado") e não há mais âncora
documental por autocitação — a base factual agora é a medição de
`RESPOSTA-FRENTE-JURIDICA-2026-07-27.md:71-73`, dentro do próprio candidato, **a mesma
medição que a rodada 3 usou para reprovar a reclassificação**. O candidato passou a
concordar com o juiz, não a contorná-lo.

`paragraph_12_ruling`: **LEGITIMATE_RESIDUAL_RISK**.

---

## 3. Onde ainda dói — e é por isto que não é 10

**3.1. Um arquivo do próprio `evals/` continua com o enquadramento reprovado.**
`evals/FORWARD-TEST.md:97-98`:

> `- Acionamento espontâneo pela `description` não foi medido em runtime porque a skill ainda estava em staging. Deve ser rechecado após instalação/runtime.`

Isto é a tese "prova pendente, fechável", **contradizendo** o `R9`, que diz que o `SKIP`
*"não tem caminho de fechamento enquanto a instalação for por porta única"*. Pior: a
premissa da frase caducou — o pacote **está** instalado no runtime (é esta cópia, sob
`.claude/skills/…`), logo o "recheque após instalação" já venceu e não aconteceu, porque
não pode acontecer. Dois documentos do mesmo pacote afirmam coisas diferentes sobre o mesmo
fato, e nenhuma checagem olha para esse arquivo: `limites_ligados_a_risco_errors` só lê o
`PLACAR.md`. A cláusula do critério fala do PLACAR e fecha; a **coerência interna**, que é
fronteira desta ótica, não fecha.

**3.2. `R9` fora da tabela** (`protocolo:443` vazia) — §2 desta opinião. A declaração
existe como texto e some como estrutura no documento renderizado.

**3.3. O PLACAR aponta para um parecer que ele mesmo removeu.**
`evals/PLACAR.md:134-135`: *"Esta decisão é do próprio pacote e **não é o veredito do
gate**. O parecer dos Juízes está no topo deste placar."* — mas o topo (`:3-13`) diz o
contrário, que os pareceres vivem **fora** do pacote, em
[`ceo-maestro/evals/FORWARD-TEST-JULGAMENTO.md`](../FORWARD-TEST-JULGAMENTO.md). Sobra de
edição da descontaminação. O alvo do link, esse sim, **existe** no runtime (conferido).
Registro à parte, como crédito: a nota de contaminação que esta ótica levantou na rodada 3
foi atendida — o candidato não carrega mais veredito, `minimum_score` nem caminho de rodada
de julgamento anterior.

**3.4. Restos de datação.** `PLACAR.md:20` ainda diz *"Data do placar: **2026-07-26**,
rodada 3"* num arquivo que carrega ajuste de 2026-07-28 (`:83-91`), e
`FORWARD-TEST.md:93` apresenta *"o validador mecânico passou em **59/59**"* sem marcar que
foi superado pelo `122/122` do placar. Número sem data de medição envelhece calado.

**3.5. `§12` proíbe declarar o limite fora dele, "apenas referenciado"** (`:456`).
`PLACAR.md:93-97` e `:130-132` não só referenciam o `R9`: repetem vetor
("a Estrutura instala porta única, e os 15 gerentes não viram skills invocáveis") e
condição de fechamento ("Fecha se a instalação mudar — decisão de runtime, fora do alcance
deste pacote"). É redeclaração parcial, e nenhuma checagem cobre duplicação de **conteúdo**
— `protocol_errors:1615-1621` confere apenas unicidade de **cabeçalho**.

---

## 4. As demais cláusulas do critério

| cláusula | estado | prova |
|---|---|---|
| `evals.json` ≥ 12 casos | **fecha** — 16 casos | `evals/evals.json:5-181`, ids `inovacao-001`…`-016`, contados um a um |
| ≥ 1 de origem real | **fecha** — exatamente 1 | `evals/evals.json:8` (`"origem": "real"`, caso `inovacao-001`); os outros 15 são `sintetica` |
| validador determinístico | **fecha** (por leitura) | constantes fixas em `validate_workflow.py:99-105`; nenhuma ocorrência de `random`, `datetime.now`, `uuid`, `socket`, `urllib`/`requests`. Os três `rglob` sem `sorted` (`:1760`, `:1779`, `:1792`) alimentam conjunto, mapa de hash e soma — resultado independente de ordem. Dependência declarada de ambiente: `SKILL_STRUCTURE_ROOT` e `INNOVATION_LEGACY_ROOT` (`:53-78`), documentada no cabeçalho (`:25-26`) |
| importa o motor de `_compartilhado/`, não copia | **fecha** | `:80-95` — `sys.path.insert(0, str(STRUCTURE_ROOT))` e `from _compartilhado.validador_schema import …` / `from _compartilhado.verificacoes_pacote import …`, com `ModuleNotFoundError → print("[FAIL] motor compartilhado ausente …") ; raise SystemExit(1)` e **sem fallback local**. Listagem completa das 25 entradas do pacote: **nenhum** `validador_schema.py`, **nenhum** `verificacoes_pacote.py` dentro da árvore |
| PLACAR com marcação de executado | **fecha** | coluna `Executado?` nas duas tabelas (`PLACAR.md:38-50` e `:60-63`), travada em código (`:1630-1631`) |
| seção que nomeia o não-provado, cada limite ligado a um `R` | **fecha, 8/8** | `PLACAR.md:77`, itens `:93-117`, contagem `:119-123`; trava em `:1642-1700` |

Crédito ao que ficou mecanizado além do texto: `eval_errors():1802-1805` põe as duas
cláusulas numéricas do critério **dentro do validador** (`len(cases) < 12` e
`any(origem == "real")`), de modo que a contagem deixou de ser alegação de placar.

---

## 5. O que não foi executado (SKIP declarado)

Python está **negado nesta sessão**. Portanto:

1. **Não executei `evals/validate_workflow.py`.** Não afirmo que ele passa. Tudo o que
   digo sobre ele é leitura de código, não observação de saída.
2. **Não confirmei o `122/122 PASS; 0 FAIL`** de `PLACAR.md:52`. Observo apenas que
   `limites_ligados_a_risco_errors` foi acoplada a um `check()` já existente
   (`:1919-1920`), o que é **consistente** com o total não ter mudado — consistência não é
   execução.
3. **Não confirmei que `limites_ligados_a_risco_errors` retorna vazio** no texto atual.
   Simulei a varredura à mão sobre `PLACAR.md:77-123` e os oito itens casam o padrão
   `^(?:\d+\.|-)\s+\*\*` e citam `R` declarado — mas isso é derivação, não execução.
4. **Não executei `evals/corpus_adversarial.py`** (`45/45`, `PLACAR.md:46`).
5. **Não recalculei o digest da árvore** — usei o fornecido pelo topo, como instruído.

Falha declarada vence falha silenciosa: se algum desses pontos for insumo de decisão do
gate, ele precisa de uma rodada com Python habilitado.

---

## 6. Fecho

- `score`: **8** · banda `ACEITO_USO_INTERNO`
- `confidence`: **alta** para as quatro cláusulas conferidas em texto e código;
  **média** para tudo que dependeria de execução (§5)
- `residual_risk`:
  1. `evals/FORWARD-TEST.md:97-98` mantém, dentro do pacote, a tese que o `R9` nega, e
     nenhuma checagem lê aquele arquivo;
  2. a trava nova cobre "item sem `R`" e "`R` inexistente", mas **não** cobre item movido
     para seção `##` irmã, `R` mintado em prosa, nem o último item da lista
     (§2, itens 2-4) — a cláusula continua parcialmente auto-neutralizável, agora num
     perímetro bem menor;
  3. `R9` está fora da tabela do §12 no documento renderizado (`protocolo:443`), e o
     validador não distingue linha de tabela de parágrafo com barras;
  4. o `122/122` permanece não re-derivável nesta sessão (Python negado) e depende de
     `STRUCTURE_ROOT` inferido e de `INNOVATION_LEGACY_ROOT` apontando para fora do pacote.

> Esta opinião cobre **somente** o CRIT-06. Nota e veredito consolidados são do
> `departamento-juizes`; conformidade é da Auditoria.
