# Origem da Síntese

## 1. Objetivo

Este pacote foi criado por síntese controlada de cinco skills do catálogo canônico. Elas forneceram conhecimento de domínio para autoria; não são dependências de runtime.

## 2. Fontes e hashes

| Skill-fonte | SHA-256 do `SKILL.md` | Capacidade incorporada |
|---|---|---|
| `consultor-negocios-apps` | `9583975439755aa90dddd1598ba137eaf0e23619bccf0da14666bbb6e8e756d8` | valor, concorrência, GTM, preço, monetização e métricas |
| `requisitos-descoberta` | `3ff5b7d68fbe18e8287d7fc929d34d8cbdaafb3e7e49830febf1ee4606150dea` | problema, público, MVP, aceite, premissas e descoberta |
| `conselheiro-financeiro` | `f4c0725b6a3636b07ba184d076d37b1b0747819d4ad648e3fdd4576365ac6d39` | rigor de fórmula, fonte, divergência e limite regulatório |
| `plano-riqueza` | `9914b1726af75577247f1460aa17639f00bf1230c50120e777f374f03d2d7756` | diagnóstico, fases, metas, sequência e atualização por diferença |
| `conteudo-riqueza` | `3e99ae5f8ba40e6f4f512beb6dce68b0f190fd0780705dac6fb3103c712b72a1` | integridade de alegações, público, fonte e proibição de promessa |

## 3. Distribuição

### Estratégia de Produto

- problema e proposta de valor;
- MVP/Depois/Fora;
- requisitos e aceites;
- posicionamento, roadmap e experimentos;
- plano em fases com métricas.

### Mercado e Cliente

- segmentos, tarefas e dores;
- pesquisa e saturação;
- concorrentes e alternativas;
- canais, aquisição, ativação e retenção;
- integridade das alegações externas.

### Viabilidade e Monetização

- preço e modelo de receita;
- custos e cenários;
- CAC, LTV, churn e payback quando aplicáveis;
- fórmulas e premissas reproduzíveis;
- riscos comerciais, financeiros e regulatórios.

## 4. Conteúdo deliberadamente excluído

Não foram importados:

- aconselhamento financeiro pessoal;
- plano individual de dívidas, reserva ou aposentadoria;
- recomendação individual de investimento;
- coaching de riqueza;
- produção de conteúdo sobre enriquecimento;
- autoridade para escolher arquitetura;
- autoridade para aprovar escopo, orçamento ou risco;
- nota final autoatribuída pelas fontes.

## 5. Lacunas declaradas

As fontes não cobrem, com autoridade autônoma:

- contabilidade societária;
- tributação;
- parecer jurídico;
- compliance regulatório especializado fora dos guardrails básicos.

Quando aplicáveis, esses temas geram `BUSINESS_CAPABILITY_GAP` e retornam ao CEO. Não são preenchidos com finanças pessoais.

## 6. Pesquisa externa

Não foi necessária pesquisa na internet para a primeira versão. As cinco fontes cobrem estratégia, descoberta, mercado, monetização e integridade; a única lacuna encontrada exige especialista de outro domínio, não mais conteúdo genérico de consultoria.

## 7. Política de runtime

O pacote é autocontido. Se um agente novo estiver ausente, bloqueie. Nunca invoque as cinco fontes acima como fallback silencioso.
