# Contrato e manifesto — julgamento dos 14 pacotes restantes

- **Missão:** `msn-2026-07-29-t3-julgamento-14`
- **Rodada:** 1
- **Data:** 2026-07-29
- **Snapshot da fonte:** commit `f938386eb3a7c0eeafa3a97797f8f13afdbd5715`
- **Nível exigido:** `INTERNO`
- **Rubrica:** `rubrica-corte-v2`
- **Rota:** Jeremias → `ceo-maestro` → `diretor-de-lentes` →
  `departamento-juizes` → três óticas independentes
- **Autoridade:** a instrução corrente de Jeremias, “ok, vamos seguir”, autoriza
  continuar a tarefa 3 do estado canônico. Não autoriza publicação, promoção ou
  correção silenciosa dos candidatos.

## INTENT

Emitir parecer verificável sobre os 14 pacotes ainda sem nota, no mesmo
snapshot, com critérios uniformes, nota inteira por ótica, consolidação pela
menor nota e separação entre julgamento e retrabalho.

## Escopo

**Dentro:** `SKILL.md`, `CONTRATO-DE-COMPROMISSO.md`, metadata, schemas,
referências, agentes, evals e placares que pertencem ao pacote; vínculos
externos citados pelo próprio pacote; ADR-002, ADR-014 e ADR-015 vigentes.

**Fora:** alterar candidato durante a rodada; preencher a planilha; promover
pacote; publicar; aceitar risco; usar média ou arredondamento; executar
correção apontada pelos pareceres.

Para impedir sobreposição, o pacote do `ceo-maestro` exclui as três subárvores
executivas, e o pacote do `diretor-de-lentes` exclui
`departamento-juizes/` e `departamentos-operacionais/`. Nos demais, a árvore
inteira do pacote entra, inclusive `agentes/`.

## DONE

1. os 13 candidatos não reflexivos recebem três `JUDGE_OPINION` independentes;
2. `departamento-juizes` recebe painel externo, porque não pode julgar a si;
3. cada candidato recebe relatório com 8 critérios, cadeia até artefato real,
   menor nota e veredito da rubrica v2;
4. o resumo distingue `VALIDATED`, `ACEITO_USO_INTERNO` e `REPROVED`;
5. defeitos encontrados viram pendência de retrabalho separada — nunca patch
   dentro desta rodada;
6. estado canônico, view derivada e runtimes ficam reconciliados.

## Critérios aplicáveis

Cada texto abaixo já contém “como se observa”. A gerente não pode criar,
remover, reordenar nem reescrever estes critérios depois de abrir o candidato.

| id | texto literal e observabilidade | dona | secundária |
|---|---|---|---|
| `CRIT-01` | **Papel, autoridade e fronteira.** O pacote mantém papel, superior, subordinados e autoridade humana coerentes entre `SKILL.md`, contrato e metadata, sem gerente executar especialidade. Observar por comparação literal desses arquivos e da hierarquia vigente. | fidelidade e contrato | — |
| `CRIT-02` | **Entradas, saídas e handoffs.** Entradas aceitas, saídas obrigatórias, `return_to` e canais proibidos formam uma cadeia única e utilizável. Observar no contrato, protocolo, schema e caminhos realmente resolvidos. | fidelidade e contrato | experiência e risco |
| `CRIT-03` | **Obrigações, proibições e barreira.** O candidato cobre integralmente as obrigações e proibições do próprio contrato e falha fechado quando a barreira não fecha. Observar por matriz literal contrato → skill → schema/evals. | fidelidade e contrato | robustez e evidência |
| `CRIT-04` | **Coerência de schema e contratos consumidores.** Tipos, enums, campos obrigatórios e envelopes positivos/negativos concordam entre schema local, contratos e consumidores. Observar nos schemas, fixtures e resultados determinísticos já registrados. | robustez e evidência | fidelidade e contrato |
| `CRIT-05` | **Rastreabilidade e fonte normativa.** Links resolvem, decisões vigentes estão identificadas, a fonte de Regras de Ouro é referenciada sem cópia divergente e a cadeia alegação → evidência → artefato é abrível. Observar por links, ADRs, digests e referências reais. | robustez e evidência | — |
| `CRIT-06` | **Evals honestos e limites declarados.** O pacote distingue PASS/FAIL/SKIP, não transforma ausência em sucesso e liga cada limite a risco e condição de fechamento. Observar em `evals/`, `PLACAR.md`, corpus e validador, sem executar teste dentro da ótica. | robustez e evidência | experiência e risco |
| `CRIT-07` | **Separação de julgamento e conformidade.** O pacote não se autoaprova, não pontua a própria entrega e encaminha nota aos Juízes e conformidade à Auditoria. Observar no vocabulário, nas proibições, nos handoffs e nas saídas exemplificadas. | fidelidade e contrato | experiência e risco |
| `CRIT-08` | **Operabilidade, manutenção e risco residual.** Um consumidor sem o autor por perto consegue acionar, operar, diagnosticar falha e voltar atrás sem depender de memória implícita. Observar em workflow, mensagens de bloqueio, recovery/rollback, exemplos e riscos declarados. | experiência e risco | robustez e evidência |

Assim, cada pacote produz 14 linhas de scorecard: 5 de fidelidade, 5 de
robustez e 4 de experiência.

## Candidatos e identidade congelada

O `candidate_digest` usa
`_compartilhado/verificacoes_pacote.py::digest_de_arvore`: bytes crus, caminho
POSIX relativo, ordem ordinal, dois espaços no manifesto, UTF-8 e `\n`
terminal. O `contract_digest` é o SHA-256 dos bytes crus do contrato.

| id | candidato | arquivos | `candidate_digest` | `contract_digest` |
|---|---|---:|---|---|
| `C01` | `ceo-maestro` | 95 | `sha256:7d56e90717f48c0f92dce690673b10ad1755bd58bc0d0f3ea9bca8c8282b134d` | `sha256:989935eabb4d03499b729122bf7e7055985a4eeaee67d96d2f54395ce5279ff5` |
| `C02` | `departamento-evolucao-skills` | 27 | `sha256:10989982d7ac3dbcb7d630dc9b8cdd36ac885a9c5c200b3df55f967311d968b0` | `sha256:b07d06d393d908c7285b95e4fbeb42a950d803c657cac09b9c1d483c58705574` |
| `C03` | `departamento-negocios` | 24 | `sha256:349ef96ee1ee00ff6aa2642e0c4b359d8cc4c408060a04846f5664c5dea160d9` | `sha256:7fd9f9100c6d3613eba8dec288e8a1430ed73079ad55d10790b5db5f388c8baf` |
| `C04` | `diretor-de-lentes` | 15 | `sha256:693b3796894faad8f981bffb9778a7dd1ca2a870b1e3fa5c9daeb88ed69f7936` | `sha256:290b6608f1902003ea572234ac7332e2ba3d3ff9373c309158f9d75f498f6b67` |
| `C05` | `departamento-juizes` | 23 | `sha256:53dbc6347b5361684e722490f7aaef333f940bf753991f5fae3ba216b1cc6361` | `sha256:b7ab8b49d800fe46a2d21b4b8a546f52d467d834e8e2ac6dd335b1c4d36ad431` |
| `C06` | `departamento-arquitetura-dados` | 31 | `sha256:8295474f0664cbe659ad00bbb9f6d7d6fb9b54346cbd88d7c503b7b4cd2b53ca` | `sha256:184387fa1584c4711f0b485df65b4c1aaad45485da83910768f7f05c3f9ada02` |
| `C07` | `departamento-arquitetura-software` | 32 | `sha256:a9de34000a74ea194b116b1c29df675513dc8d35c7abdac3aa9d534951675131` | `sha256:db8d294f9f7ac294197e8f20155b8d08842032053da04b7d37f5adbde645b29f` |
| `C08` | `departamento-auditoria-responsabilidades` | 21 | `sha256:8e6b6c7a665d01a3e16ab648534aef09aa6a47b0f267b8ec8874107b70eb2bda` | `sha256:4735de547bb063ac95e0d2fff7c007541006a2f235a136ebb4909be20e271f28` |
| `C09` | `departamento-conteudo-marketing` | 37 | `sha256:6089d7fb58fe48e5520d9cc3070a6b3235a5103f878957451c7dcd8ce729d423` | `sha256:4fe107b4edeb06fb10c6bb2b374ba17579459ae480a7764d3751cc7e4196ebff` |
| `C10` | `departamento-desenvolvimento` | 37 | `sha256:fd41c323aef4f3c17db6cca0c0c8dbcd4600c29aeb480ef3717a0f26cc5bfd1f` | `sha256:1ca3dc1fc2cce28d8fc91622aa0f2e5f23cb550a83d818311796faf3d5131649` |
| `C11` | `departamento-design-ux-ui` | 34 | `sha256:065524fb1d1aeef5ced1dc30cc905763715f25bba73dd8aebc8b43c3d1e5fc42` | `sha256:77e7835172803e350c31bd24ff23f6ce2b160180766050f292d72b10a40ded36` |
| `C12` | `departamento-qa-usabilidade` | 24 | `sha256:6ca7ea12acf6200cb46dd72dd9b8dec13f44201dc3239f3795c2b23c259e7175` | `sha256:fd90cf6fdf319836af201974b68d93268c843a58d8c4acca1af006f27cabc50a` |
| `C13` | `departamento-registros` | 23 | `sha256:a8ff6fcc8b2ab2a967bf1693e6ffb4daab2d7b2aa387f1c9e0c50fab385d4148` | `sha256:f282c2277c5bf218783c25c10b7ae83f31a178f0518b152e02bc2756116c90b0` |
| `C14` | `departamento-seguranca` | 35 | `sha256:e3bea5605d3b876586e1b5de2dbcde056b2448d289ce95ec66b03ad08508e15e` | `sha256:6fc128c66230ef786e610588cda7447474bb988734ae3e85838afd955c3903ac` |

As cópias anônimas vivem somente em área temporária e não são artefato
versionado. Os relatórios citam os caminhos da fonte no commit fixado.

## Capacidades conferidas

| capacidade | SHA-256 de `SKILL.md` |
|---|---|
| `ceo-maestro` | `sha256:ff853efa968519d8ee3d0245be69eb00b9eb5acb1805ee8d0516a390cd3f0b96` |
| `diretor-de-lentes` | `sha256:b82d38507e373372b8bfa6db5601bce76a6103fcfccae2cf4fe9d8417f5dded3` |
| `departamento-juizes` | `sha256:d266b0898092440591dfcc7d6fe01f34bb98432b868fa3e3f2ffeebc0cf7316d` |
| fidelidade e contrato | `sha256:8b87459c0f50c0c34481f4a7b3510caec5e607d8448f92bfc7a95dea6f672647` |
| robustez e evidência | `sha256:7f3eb150ab2e68c813fea6049140d92490ea5d5dc3e6182ca4e14a08f03f084e` |
| experiência e risco | `sha256:3d7d68ec75706976ae08ee61fe1168c1e87a1b5a091d07c9fc8e7d187410d808` |
| `rubrica-corte-v2` | `sha256:dc417dcf59cd1d2f8dd37b6f37d2aa95a4ce08aaa1a0ce0416aa74549b92fec7` |

## Evidência disponível aos pareceres

1. os arquivos versionados do candidato no commit fixado;
2. o contrato integral, tratado como `contract_excerpt` literal;
3. os artefatos de `evals/` e `PLACAR.md` de cada pacote;
4. a cadeia mecânica fresca de 2026-07-29: **1531/1531 PASS**, zero FAIL e
   zero quebrado, registrada em `RETOMADA-2026-07-29.md`;
5. ADR-014 aceito e ADR-015 aprovado por Jeremias.

As óticas não executam build, lint nem testes. Ausência de prova executada no
próprio candidato reduz a nota de robustez; não autoriza inventar execução.

## Exceção reflexiva — `C05`

`departamento-juizes` proíbe expressamente julgar a si próprio. `C05` não entra
na consolidação da própria gerente: três revisores externos e independentes
aplicam a mesma matriz e a mesma rubrica, e um `EXTERNAL_JUDGE_REPORT`
preserva essa proveniência. O resultado não será rotulado como
`JUDGE_REPORT` emitido pelo candidato.

## Pendências e conflitos conhecidos antes da abertura

- **Conflito normativo observado:** o ADR-014 aceito e
  `rubrica-corte-v2` definem 10 → `VALIDATED`, 7–9 →
  `ACEITO_USO_INTERNO`, ≤6 → `REPROVED`; `AGENTS.md` e trechos antigos de
  `departamento-juizes/SKILL.md` e do protocolo ainda descrevem a regra
  anterior de 9,5 e apenas dois vereditos. O ADR aceito prevalece nesta
  rodada; a divergência permanece evidência a ser pontuada, não é corrigida
  durante o julgamento.
- **R2:** o runtime não expõe substrato/tier verificável por instância; registrar
  `desconhecido` e não alegar independência de substrato.
- **R4:** nomes e vocabulário próprios sobrevivem na cópia, pois removê-los
  exigiria reescrever o candidato; a cegueira é parcial e isso fica em
  `pending`.
- **R6:** todo relatório deve declarar que o registro de emissão torna a
  execução auditável, mas não tecnicamente impossível de fabricar.
