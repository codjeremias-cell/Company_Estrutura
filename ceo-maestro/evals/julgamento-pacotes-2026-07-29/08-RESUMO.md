# Resultado consolidado — julgamento dos 14 pacotes restantes

> **Correção de 2026-07-31 — o achado crítico contra C06 era falso.**
> Este registro classificou como *evidência normativa fabricada* a atribuição do teto de 1000
> linhas à RO-W8, e isso derrubou `CRIT-05` de C06 para **0** com falha crítica. A classificação
> estava errada. No snapshot julgado (`f938386`), a linha 96 de
> [`regras-de-ouro/REGRAS-DE-OURO.md`](../../../regras-de-ouro/REGRAS-DE-OURO.md) **já terminava**
> com *"Consulta sem limite corta em 1000 linhas no Supabase — sinalizar o teto ao usuário."*
> A frase entrou pelo commit `36027a2`, ancestral do snapshot (conferido com
> `git merge-base --is-ancestor`). A ótica leu o título da regra — *"Erro e data honestos"* — e
> concluiu que ela não tratava de limite de linhas, sem ler até o fim da própria linha citada.
>
> As notas abaixo **não foram alteradas**: são o que o painel de fato emitiu, e apagá-las
> esconderia o erro em vez de corrigi-lo. O que muda é a leitura de C06 — o `0` e a falha crítica
> não têm defeito por trás. A rodada 2 remediu C06 em **6**, sem falha crítica.
>
> As tarefas 7 e 13 permanecem concluídas e não são invalidadas: a 7 não tocou a fonte normativa,
> e entregou o gate `validate_forward_provenance` (âncora obrigatoriamente dentro da linha da regra
> citada, mais quatro mutações que precisam ficar vermelhas) — que vale por si, independentemente
> do motivo que o originou. A exceção da 13 (`EXAUTH-T13-R6-R3`) foi concedida sob **R6**, não sob
> este achado. Verificação completa em
> [`../rejulgamento-rodada2-2026-07-31/09-CONFERENCIA-DO-CEO.md`](../rejulgamento-rodada2-2026-07-31/09-CONFERENCIA-DO-CEO.md).

- **Missão:** `msn-2026-07-29-t3-julgamento-14`
- **Snapshot julgado:** `f938386eb3a7c0eeafa3a97797f8f13afdbd5715`
- **Nível exigido:** `INTERNO`
- **Rubrica:** `rubrica-corte-v2`
- **Resultado:** 7 `ACEITO_USO_INTERNO`, 7 `REPROVED`, 0 `VALIDATED`.
- **C05:** painel externo; não há autojulgamento nem `JUDGE_REPORT` emitido pelo candidato.

## Scorecard consolidado

A nota de cada critério é o menor valor entre as óticas aplicáveis. O `minimum_score` é o menor dos oito critérios; falha crítica também força `REPROVED`.

| id    | pacote                                   | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | mínimo | veredito             | crítica |
| ----- | ---------------------------------------- | --: | --: | --: | --: | --: | --: | --: | --: | -----: | -------------------- | ------- |
| `C01` | ceo-maestro                              |   9 |   6 |   2 |   1 |   2 |   3 |   7 |   4 |  **1** | `REPROVED`           | sim     |
| `C02` | departamento-evolucao-skills             |  10 |   8 |   8 |   8 |   8 |   7 |   9 |   7 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C03` | departamento-negocios                    |  10 |   7 |   6 |   5 |   5 |   5 |   8 |   5 |  **5** | `REPROVED`           | sim     |
| `C04` | diretor-de-lentes                        |  10 |   4 |   3 |   1 |   4 |   4 |   5 |   4 |  **1** | `REPROVED`           | sim     |
| `C05` | departamento-juizes                      |   9 |   6 |   2 |   2 |   3 |   4 |   9 |   4 |  **2** | `REPROVED`           | sim     |
| `C06` | departamento-arquitetura-dados           |  10 |   9 |   6 |   7 |   0 |   8 |   9 |   8 |  **0** | `REPROVED`           | sim     |
| `C07` | departamento-arquitetura-software        |  10 |   8 |   8 |   8 |   9 |   7 |   9 |   8 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C08` | departamento-auditoria-responsabilidades |  10 |   9 |   8 |   8 |   8 |   7 |   9 |   8 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C09` | departamento-conteudo-marketing          |  10 |   8 |   6 |   8 |   7 |   8 |   6 |   7 |  **6** | `REPROVED`           | não     |
| `C10` | departamento-desenvolvimento             |  10 |   9 |   8 |   8 |   7 |   7 |   9 |   7 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C11` | departamento-design-ux-ui                |  10 |   9 |   9 |   8 |   9 |   7 |   9 |   8 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C12` | departamento-qa-usabilidade              |  10 |   9 |   8 |   7 |   5 |   4 |   9 |   8 |  **4** | `REPROVED`           | sim     |
| `C13` | departamento-registros                   |  10 |   9 |   8 |   8 |   9 |   8 |   9 |   7 |  **7** | `ACEITO_USO_INTERNO` | não     |
| `C14` | departamento-seguranca                   |  10 |   9 |   8 |   8 |   9 |   8 |   9 |   8 |  **8** | `ACEITO_USO_INTERNO` | não     |

## Retrabalho que bloqueia nova rodada

1. **C01, C03, C04 e C05 — migração incompleta do ADR-014.** Propagar `required_level`, remover o corte externo de 9,5, eliminar o canal lateral Negócios → Juízes e reconciliar SKILL, contratos, schemas, protocolo, fixtures e placares.
2. ~~**C06 — evidência normativa fabricada.** O forward atribuiu à RO-W8 uma regra inexistente e manteve o caso positivo. A alegação precisa ser retirada, provada ou rotulada como hipótese não normativa.~~
   **RETIRADO em 2026-07-31 — o achado era falso.** A regra citada existe e a frase estava literal
   na linha 96 da RO-W8 já no snapshot julgado. Ver a correção no topo deste documento. O
   retrabalho da tarefa 7 foi executado assim mesmo e produziu um gate legítimo; o que cai é a
   acusação, não o artefato.
3. **C09 — conformidade sem proveniência.** O PLACAR hospeda `APROVADO_COM_RESSALVAS` sem parecer externo verificável; isso derrubou CRIT-03 e CRIT-07 para 6.
4. **C12 — prova contraditória.** O estado de `quick_validate.py` aparece simultaneamente como PASS e bloqueado/não provado.

Os outros sete pacotes alcançam o nível interno, mas continuam com melhorias obrigatórias antes de uma rodada de produção: provas ponta a ponta, operações reais controladas, rollback e separação mais forte entre declaração e execução.

## Artefatos

- [Contrato e manifesto](00-CONTRATO-E-MANIFESTO.md)
- [Registro de emissão](01-REGISTRO-DE-EMISSAO.md)
- [Opiniões — fidelidade e contrato](02-JUDGE-OPINIONS-FID.ndjson)
- [Opiniões — robustez e evidência](03-JUDGE-OPINIONS-ROB.ndjson)
- [Opiniões — experiência e risco](04-JUDGE-OPINIONS-EXP.ndjson)
- [Relatórios ao Diretor](05-DEPARTMENT_JUDGE_REPORTS.ndjson)
- [Relatórios ao CEO](06-JUDGE_REPORTS.ndjson)
- [Relatório externo de C05](07-EXTERNAL-JUDGE-REPORT-C05.json)
- [Auditoria de responsabilidades](09-AUDITORIA-DE-RESPONSABILIDADES.md)

## Limites do método

- **R2:** substrato e tier das três instâncias não são verificáveis neste runtime.
- **R4:** a anonimização preservou fingerprints do conteúdo; isso foi declarado antes e não afetou as notas.
- **R6:** as óticas julgaram por leitura e não reexecutaram validadores; uma bateria finita não prova ausência de bypass.
- O painel julgou o snapshot congelado. Nenhuma correção foi aplicada aos candidatos durante a rodada.
