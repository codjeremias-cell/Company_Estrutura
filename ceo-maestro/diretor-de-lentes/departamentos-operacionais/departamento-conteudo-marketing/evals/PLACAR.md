# Placar — Departamento de Conteúdo e Marketing

<!-- SELO-DE-CONTAGEM -->
> **Contagem vigente, ligada ao instrumento que a produziu.** Regenerada por
> `_compartilhado/selar_contagem.py` e conferida pela trava
> `validate_contagem_ligada_ao_instrumento`, que fica **vermelha** se o validador
> mudar e o selo não for refeito. Qualquer outro número deste documento é
> registro da data em que foi medido — não estado de agora.

CONTAGEM-VIGENTE: 50/50 | instrumento: `evals/validate_workflow.py` | sha256-normalizado: `sha256:c03ff43a6699f00533ea0eeb260a336b0dd3ceba43f3c78a5ef593fa84b459c7` | medido-em: 2026-08-22
<!-- /SELO-DE-CONTAGEM -->

## Passagem pelo gate

Este pacote foi submetido ao gate em 2026-07-29. Opiniões, notas, veredito e
histórico vivem fora do candidato, no
[resultado consolidado](../../../../evals/julgamento-pacotes-2026-07-29/08-RESUMO.md),
para não contaminar uma rodada futura com o próprio julgamento.

> **Reconciliação de 2026-07-26.** O número **próprio** deste pacote foi remedido nesta data e vale **39/39 PASS**. Os valores de **vizinho** e os **totais de cadeia** que aparecem abaixo são o **retrato da cascata que produziu este placar** e foram deixados como estavam: são registro histórico, não alegação corrente. Naquela medição, a cadeia canônica somava **1531/1531 PASS** (motor compartilhado 61 + os 15 validadores de pacote), reconciliada em [`ORGANOGRAMA.md`](../../../../../ORGANOGRAMA.md).
>
> Regra que passou a valer no `GUIA-DE-EXPANSAO-E-MIGRACAO.md`, passo 10.5: **número de vizinho carrega a data da medição, ou não entra.** Onze de quinze placares declaravam para si um número menor que o real em 2026-07-26, porque cada frente congelava o vizinho e o vizinho crescia depois.

- Data: 2026-07-26
- Escopo: consolidação híbrida e criação do Departamento
- Fontes: `redator-tecnologia-ia` + `email-marketing-html` + pesquisa oficial

## Resultado mecânico

| Prova | Executado? | Resultado |
|---|---|---|
| Baseline compartilhado anterior à mudança | sim | 55/55 PASS |
| Baseline Auditoria anterior à mudança | sim | 64/64 PASS |
| Baseline Juízes anterior à mudança | sim | 61/61 PASS |
| Baseline Diretor anterior à mudança | sim | 48/48 PASS |
| Baseline CEO anterior à mudança | sim | 32/32 PASS |
| Motor de schema compartilhado | sim | 55/55 PASS |
| Validador deste Departamento | sim | 39/39 PASS — 17 positivos e 22 negativos |
| Regressão da Auditoria | sim | 64/64 PASS |
| Regressão dos Juízes | sim | 61/61 PASS |
| Regressão do Diretor com dez Departamentos | sim | 49/49 PASS |
| Regressão do CEO no caminho canônico | sim | 32/32 PASS |
| Núcleo integrado, incluindo motor compartilhado | sim | **299/299 PASS** |
| Regressão do Departamento de Negócios | sim | 169/169 PASS |
| Regressão do Departamento de Evolução de Skills | sim | 56/56 PASS |
| Lint do `template-base.html` não preenchido | sim | negativo esperado: 1 FAIL por 12 placeholders; envio bloqueado |

## O que o validador cobre

- pacote gerente + oito agentes, metadata e links;
- fontes legadas intactas e lint/template copiados byte a byte;
- seis envelopes internos e pares exclusivos agente/capacidade;
- oito gates, recálculo de prontidão e ações externas;
- casos negativos de bypass, AUTH, direitos, evidência e autoaceite;
- `DEPARTMENT_RETURN` validado contra o schema do Diretor.

O lint do template bruto **não** é contabilizado como PASS: ele demonstrou que o artefato não
preenchido não pode ser entregue como e-mail final. Isso preserva a regra de falha fechada sem
alterar o template copiado byte a byte da fonte.

## O que não foi provado

| Item | Estado | Motivo |
|---|---|---|
| Forward test comportamental com modelo | SKIP | Não executado nesta sessão; não há resposta a inventar. |
| Renderização real de imagem | SKIP | Nenhuma campanha/briefing visual foi contratada para execução. |
| Renderização real de vídeo | SKIP | Nenhum renderizador e candidato de vídeo foram contratados. |
| Envio real de e-mail | SKIP | Proibido sem lista, domínio, consentimento e autorização. |
| Publicação/compra de mídia | SKIP | Proibida sem conta, orçamento e autorização delimitada. |
| Resultado comercial | SKIP | Depende de campanha futura e dados observados. |
| Parecer formal dos Juízes sobre candidato de campanha | SKIP | O pacote está sendo materializado; ainda não há campanha em missão executiva. |

SKIP não é PASS. Este placar será atualizado somente com saída realmente executada.

## Veredito da auditoria de materialização

**APROVADO_COM_RESSALVAS.** O pacote, a autoridade, a hierarquia, a proveniência das duas fontes,
os contratos de fronteira com Negócios, Juízes e Registros, os oito gates e as regressões
mecânicas estão conformes. A aprovação
vale para **materializar a skill**, não para publicar campanha, comprar mídia, enviar e-mail ou
declarar resultado comercial. As ressalvas são os SKIPs acima: forward comportamental e julgamento
de uma campanha real dependem de missão futura, candidato identificável e evidência de execução.
