# Placar — Departamento de QA e Usabilidade

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 126/126 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:9bac723b796f45c10ee4b8ce6f7236b186626cbf37a458cd0cd7bfeb6ef87980` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **117/117 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

**Data:** 2026-07-26  
**Alvo desta captura:** pacote isolado anterior à promoção canônica  
**Regra:** somente resultados realmente executados; sucesso simulado é
proibido.

## Baterias

| Bateria | Resultado |
|---|---|
| Inicialização pelo `skill-creator` | PASS — gerente + 3 agentes criados |
| `quick_validate.py` nas 4 skills | **PASS — 4/4 `Skill is valid!`**, executado em 2026-07-26. O bloqueio anterior (`ModuleNotFoundError: yaml`) caiu: PyYAML 6.0.3 está instalado. Rodar com `PYTHONUTF8=1`, senão o script lê os arquivos em cp1252 e quebra na primeira aspa tipográfica |
| Estrutura, metadata, links, schema, contratos e fixtures locais | PASS — incluídos no validador do Departamento |
| Gate composto QA→Diretor | PASS — schema externo + digest autenticado + reconciliação fonte→envelope |
| Manifesto SHA-256 do legado | PASS — 87/87 caminhos, bytes e hashes intactos |
| Validador do Departamento | **117/117 PASS** |
| Motor compartilhado | **55/55 PASS** |
| Departamento de Auditoria | **64/64 PASS** |
| Departamento de Juízes | **61/61 PASS** |
| Diretor de Lentes | **49/49 PASS** |
| CEO Maestro | **32/32 PASS** |
| Cadeia integrada desta execução | **377/377 PASS** |
| Forward test comportamental independente | **29/29 assertions PASS** em 4 casos |
| Auditoria adversarial final A | **9/9 ataques bloqueados**; suíte 116/116 |
| Auditoria adversarial final B | **10/10 ataques bloqueados**; suíte 116/116 |
| Validação após promoção no caminho canônico | **PASS — 377/377**, com os mesmos totais da cadeia acima |

O validador local executa verificações equivalentes de frontmatter e metadata
sem depender de PyYAML. Isso não transforma a execução bloqueada de
`quick_validate.py` em PASS; a limitação ambiental permanece declarada.

## Evidências

- [Forward test](FORWARD-TEST.md)
- [Auditoria adversarial](ADVERSARIAL-AUDIT.md)
- `validate_workflow.py`
- `references/origem-migracao.md`

## O que ainda não foi provado

### Dono e condição de fechamento, item a item

> Exigido pelos achados `CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03. Este pacote não estava entre os sete reprovados, e mesmo assim tinha as três pendências sem dono: o defeito é de forma, e a forma estava na casa inteira.

| item | dono | fecha quando |
|---:|---|---|
| 1 | o próprio Departamento | houver missão real com dispositivo físico, carga e inspeção visual de PDF, e o resultado voltar como evidência — são capacidades por missão, e este placar mede a migração |
| 2 | `diretor-de-lentes` | houver evidência de eficácia continuada dos três agentes em missões reais; qualquer expansão do time depende dela e de ADR, e ADR é ato do Diretor |
| 3 | o próprio Departamento | o `quick_validate.py` rodar com PyYAML disponível, ou a dependência for removida do caminho obrigatório |


- Dispositivo físico, carga pesada, produção e inspeção visual real de PDF em
  projeto real; são capacidades por missão, não testes desta migração.
- Eficácia continuada dos três agentes em missões reais; qualquer expansão do
  time depende dessa evidência e de ADR.
- `quick_validate.py` com sua dependência PyYAML disponível.

## Regra de fechamento

Mecânica verde não equivale a eficácia em produto real. Estado positivo exige
evidência da missão; `SKIP`, `UNVERIFIED`, `MISSING` e pendência nunca viram
aprovação.
