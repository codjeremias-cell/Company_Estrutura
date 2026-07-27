# ADR-007 — Departamento de Conteúdo e Marketing e time elástico

- **Estado:** aceita
- **Data:** 2026-07-26
- **Decisão humana:** Jeremias solicitou o Departamento e autorizou quantidade de agentes conforme
  a necessidade do domínio.
- **Série global:** sucede o
  [ADR-004 de Evolução](../../../../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md)
  o
  [ADR-005 de Registros](../../departamento-registros/references/adr-005-quatro-agentes-e-relatorios-de-registros.md)
  e o
  [ADR-006 de Arquitetura](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md).

## Contexto

O organograma anterior previa exatamente três agentes por Departamento. O domínio pedido reúne
estratégia, narrativa, imagem, vídeo, publicidade, e-mail, relatoria e conformidade. Reduzi-lo a
três fronteiras produziria agentes genéricos, sobreposição e perda de responsabilidade. Ao mesmo
tempo, `redator-tecnologia-ia` e `email-marketing-html` cobrem apenas duas partes e não devem ser
renomeados como se fossem o Departamento inteiro.

Há outro limite arquitetural: produtores respondem ao Diretor; Negócios é par do Diretor sob o
CEO; Juízes só aceitam pedido do Diretor e não conversam com produtores. A colaboração pedida não
pode virar bypass.

O `departamento-registros` introduziu uma fronteira adicional: produzir um relatório de desempenho
é trabalho analítico deste domínio; decidir seu destino canônico, persistir o registro, manter
índice ou produzir relatório de aprendizagem é trabalho de Registros. Confundir os dois faria
Inteligência de Marketing disputar custódia com um Departamento institucional.

## Decisão

1. Criar `departamento-conteudo-marketing` como décimo Departamento operacional sob
   `diretor-de-lentes`.
2. Adotar **mínimo de três agentes, sem máximo fixo** para todos os Departamentos. A quantidade
   deve ser justificada por cobertura exclusiva, e mudança posterior exige ADR, organograma e
   regressão.
3. Iniciar com oito agentes: estratégia; narrativa; imagem; vídeo; publicidade; e-mail;
   inteligência/relatoria; governança/conformidade.
4. Migrar seletivamente os princípios úteis de `redator-tecnologia-ia` e
   `email-marketing-html`, preservando as origens por hash. Capacidades restantes são criação
   informada por pesquisa oficial.
5. Manter o Diretor como superior e roteador: o Departamento recebe contexto assinado de Negócios
   por meio da matriz do Diretor e vai aos Juízes por `JUDGMENT_REQUEST` emitida pelo Diretor.
6. Separar `PRODUCTION_ONLY` de `AUTHORIZED_ACTIVATION`. O primeiro é padrão. Efeito externo exige
   autorização delimitada no contrato, referência no assignment e recibo; ausência rebaixa ao
   modo de produção.
7. Tornar obrigatórios oito gates: alinhamento de negócio, alegações, marca, acessibilidade,
   direitos/proveniência, privacidade/consentimento, política do canal e mensuração.
8. Manter `agente-inteligencia-relatoria-marketing` como produtor de planos de mensuração,
   análises e relatórios de desempenho. Qualquer persistência durável ou transformação em registro
   institucional é solicitada ao Diretor, que abre missão separada para `departamento-registros`.
   Não existe escrita direta em pasta de Registros nem handoff lateral entre agentes.

## Consequências

- O schema e o validador do Diretor passam de nove para dez Departamentos.
- A regra de “exatamente três” no guia e no organograma é substituída por piso três e time
  justificado.
- O Departamento pode crescer sem fundir competências incompatíveis, mas cada expansão aumenta
  custo de coordenação e precisa provar fronteira nova.
- Negócios e Juízes participam do fluxo sem ganhar ou perder autoridade.
- Relatoria de marketing passa a ter fronteira explícita com Registros: o relatório permanece
  artefato causal do candidato; a custódia institucional é outra missão, outro dono e outro aceite.
- Renderização de vídeo, publicação, disparo e compra de mídia continuam lacunas quando o runtime
  não oferecer ferramenta e autorização; o pacote não finge execução.

## Alternativas consideradas

| Alternativa | Motivo do descarte |
|---|---|
| Manter três agentes generalistas | Sobrepõe formatos e esconde conformidade dentro de produção. |
| Criar um Departamento por canal | Fragmenta a narrativa e multiplica gerentes antes de haver escala. |
| Subordinar o Departamento a Negócios | Viola o organograma executivo; Negócios é par matricial do Diretor. |
| Permitir contato direto com Juízes | Viola cegueira, anti-bypass e protocolo de julgamento. |
| Só renomear as duas skills legadas | Não cobre imagem, vídeo, publicidade, estratégia, mensuração ou governança. |
| Autorizar ativação por padrão | Mistura produção reversível com efeitos externos, dados, contas e orçamento. |

## Critério de revisão

Revisar quando uma fronteira gerar fila recorrente que não caiba em seu contrato, quando duas
fronteiras disputarem o mesmo ativo ou quando o runtime oferecer canal autenticado para
comunicação e autorização. Até lá, oito é composição inicial, não teto permanente.
