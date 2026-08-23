# Origem da governança

**Promovida em:** 2026-07-26  
**Decisor da estrutura:** Jeremias  

> **Os dois valores abaixo NÃO estão em vigor.** Ficam como registro do que foi
> declarado em 2026-07-26 e nunca conferido. O valor vigente é o da seção
> «Digest normativo vigente», e só ele é lido por código.

`HISTORICO-NAO-VIGENTE:` SHA-256 inicial — `06341DB894EF2CCCA12315B902CC5D09A76D1421ADE01898C0DC2BB514CA0E73`

`HISTORICO-NAO-VIGENTE:` SHA-256 após adaptação organizacional — `197736D2E7FBEFB730C56A8385E6E5E28B1FDD54D6BDB67055930415E328D48E`

> **A marca e o valor moram na MESMA linha, e isso é regra e não estilo.** A
> conferência é por linha; quebrar a linha entre o marcador e o valor devolve o
> valor à condição de órfão, e a trava acusa — como acusou na primeira tentativa
> desta própria correção, em 2026-08-05.

`REGRAS-DE-OURO.md` foi semeado byte a byte a partir de
`Catalogo-Skills-Unificado/REGRAS-DE-OURO.md`. Em seguida, referências organizacionais foram
adaptadas de lentes/comitê para CEO, Diretor, Departamentos, Agentes, Auditoria e Juízes,
sem reduzir nenhuma obrigação. A partir desta migração, ele é a fonte normativa única para
`Estrutura Final de Skills/`.

O catálogo anterior permanece intacto para os pacotes legados e para rollback. Mudanças
futuras na nova arquitetura devem editar somente esta fonte local e registrar decisão;
skills subordinadas apenas apontam para ela.

## Propagação de 2026-08-19 — as duas cópias voltam a 62 RI/RO

**Decisor:** Jeremias (T23 do ledger do Catálogo). **Executor:** a frente do Catálogo, com a
fronteira levantada por ele para este ato — normalmente ela **não** escreve aqui.

A divergência estava aberta desde **2026-08-08** e não era só a G2, como se supunha a princípio:
mediu-se **62 RI/RO no Catálogo contra 59 aqui**, de mão única — nada existia só nesta cópia.
Enquanto durou, **quem operava no regime empresa operava sob um conjunto menor sem saber**.

Entraram cinco itens, todos com o texto **byte a byte** do Catálogo, conferidos por SHA-256 de
bloco contra `estado/artefatos/propagacao-regras-de-ouro-t23.md`:

| Item | Onde | SHA-256 do bloco (16) |
|---|---|---|
| ❌ Nunca vender prova parcial como completa | bloco de conduta | `68bc10abaf071294` |
| RO-16 — pergunta pede instrução | Padrões universais | `21d5675184e1a767` |
| RO-17 — parar no limite da tarefa | Padrões universais | `2b4429afa40bd6c9` |
| RO-18 — nunca comando interativo em automação | Padrões universais | `2b8dc7d80090b3f6` |
| RO-15 — substituída pela versão com os três modos de encerramento | Padrões universais | `814ba68245b209f5` |

**Nenhuma adaptação organizacional foi necessária:** os cinco textos não citam lente nem comitê,
então a única diferença legítima entre as cópias não se aplicava a eles.

Versão: **v2.8 → v2.10**, alinhada ao Catálogo. O `DIGEST-NORMATIVO` abaixo foi recalculado
**pela função de produção** (`_compartilhado/validador_schema.py::sha256_texto_normalizado`), não
por reimplementação — e é ele que os validadores conferem a cada execução.

## Digest normativo vigente — valor DECLARADO, conferido a cada execução

```
DIGEST-NORMATIVO: sha256:6429c988e640dcc3c9ce0557e05a6a629e224af97c4c3cba27abd08d4b45bf3d
```

- **Receita:** `sha256` sobre os bytes UTF-8 de `REGRAS-DE-OURO.md`, BOM removido e `CRLF`
  trocado por `LF` — `_compartilhado/validador_schema.py::sha256_texto_normalizado`.
- **Critério:** mede **conteúdo**, não bytes de checkout. O mesmo arquivo em CRLF e em LF dá
  dois valores diferentes com `sha256_file`; com esta receita dá um só, e ele coincide com o
  do blob que o git guarda. Um caractere a mais no arquivo muda o valor — que é a única
  propriedade que interessa aqui.
- **Quem confere:** `conferir_digest_das_regras()`, chamado pelos validadores de pacote. A
  divergência é caso **vermelho**, com declarado, recomputado e receita na mensagem.
- **Quem atualiza:** quem alterar `REGRAS-DE-OURO.md` atualiza esta linha **no mesmo commit**,
  e a alteração da norma é decisão de Jeremias. Sem isso, todo pacote reprova.

> **Por que este arquivo, e não o contrato de cada pacote.** A fonte normativa é **uma**, e
> compartilhada pelos **quinze** pacotes gerentes — os dez que a rodada 1 alcançou e os cinco
> que ficavam de fora porque nunca tinham tido checagem nenhuma (`ceo-maestro`,
> `conteudo-marketing`, `inovacao-melhoria`, `negocios` e `qa-usabilidade`).
> Declarar a identidade dela dentro de cada contrato criaria quinze
> declarações do mesmo objeto, sem árbitro para a primeira divergência, e faria cada pacote
> autenticar contra a própria cópia a norma que ele deve obedecer — a forma que o próprio
> validador do `ceo-maestro` já rejeita como dado, no caso *«digest de regras autoafirmado é
> rejeitado»*. Um artefato, uma identidade, um lugar.

### O que esta seção corrige, medido em 2026-08-04

O valor marcado no topo como `HISTORICO-NAO-VIGENTE: SHA-256
após adaptação organizacional` **não corresponde a
nenhuma versão do arquivo** — nem em LF, nem em CRLF, nem com BOM, em nenhum dos dois commits
que tocaram `REGRAS-DE-OURO.md` (`36027a2` e `0fe4a64`), nem na cópia de trabalho. Ele foi
declarado uma vez e nunca conferido, porque nenhum código o lia: a checagem publicada era
`sha256_file(RULES_PATH).startswith("sha256:")`, verdadeira por construção. O valor de cima
fica onde está, como **registro histórico do que foi declarado**; o valor vigente é o desta
seção, e este é lido por código. Receita, raiz e critério da medição em
`ceo-maestro/evals/digest-que-nao-reprova-2026-08-04/saida-crua/01-inventario-sitios.txt`.


### A marcação é obrigatória, e é mecânica

Todo valor com forma de SHA-256 dentro deste arquivo declara se está em vigor:
`DIGEST-NORMATIVO:` para o vigente — **exatamente um** —, `HISTORICO-NAO-VIGENTE:`
para o que já não vale. Quem escrever um terceiro valor sem marca reprova os
quinze pacotes com `DIGEST_SEM_MARCACAO`, e a mensagem diz qual linha e quais são
os dois marcadores. A conferência é `conferir_marcacao_da_proveniencia()`, chamada
de dentro de `conferir_digest_das_regras()` — não há como conferir a fonte
normativa sem passar por ela.

Isto existe porque a rodada 1 deixou um valor órfão em MAIÚSCULAS na posição de
autoridade do arquivo, fora do alcance da própria trava de ambiguidade que ela
criou: `_RE_DIGEST_DECLARADO` só casa 64 hex minúsculos precedidos do marcador. A
regra passou a ser sobre a **forma** do valor, não sobre o marcador — porque o
defeito estava exatamente no valor que não tinha marcador nenhum.
