# Placar — Departamento de QA e Usabilidade

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **117/117 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. A cadeia canônica hoje soma **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
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

- Dispositivo físico, carga pesada, produção e inspeção visual real de PDF em
  projeto real; são capacidades por missão, não testes desta migração.
- Eficácia continuada dos três agentes em missões reais; qualquer expansão do
  time depende dessa evidência e de ADR.
- `quick_validate.py` com sua dependência PyYAML disponível.

## Regra de fechamento

Mecânica verde não equivale a eficácia em produto real. Estado positivo exige
evidência da missão; `SKIP`, `UNVERIFIED`, `MISSING` e pendência nunca viram
aprovação.
