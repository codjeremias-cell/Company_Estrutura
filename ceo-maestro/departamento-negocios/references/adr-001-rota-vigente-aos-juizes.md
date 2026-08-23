# ADR-001 — Rota vigente de Negócios aos Juízes

- **Status:** aceito; emendado em 2026-07-29 pelo ADR-014
- **Data:** 2026-07-26
- **Escopo:** `departamento-negocios`

## Contexto

O organograma declara comunicação de entrega e veredito entre `departamento-juizes` e todos os Departamentos, inclusive Negócios. Porém, a implementação materializada dos Juízes aceita `JUDGMENT_REQUEST` exclusivamente do `diretor-de-lentes` e devolve o resultado exclusivamente a ele. O schema do Diretor também fixa o Diretor como produtor e destinatário desse contrato.

Negócios responde diretamente ao CEO e só pode falar com o Diretor quando a `EXECUTIVE_MISSION` autoriza a matriz.

## Decisão

Enquanto o contrato materializado dos Juízes não for alterado de forma coordenada:

1. Negócios prepara `BUSINESS_JUDGMENT_PACKAGE`;
2. com matriz autorizada, envia ao Diretor `MATRIX_EXCHANGE_MESSAGE` pedindo a abertura do julgamento;
3. o Diretor produz o `JUDGMENT_REQUEST`;
4. os Juízes devolvem o veredito ao Diretor;
5. o Diretor devolve o resultado a Negócios pela matriz;
6. sem matriz autorizada, Negócios bloqueia e pede ao CEO missão revisada.

O canal de julgamento não é usado para tratar problema técnico; a mesma matriz transporta dois tópicos distintos e explicitamente autorizados.

## Emenda ADR-014 — nível exigido e veredito

A rota exclusiva pelo Diretor permanece inalterada. A partir do
[ADR-014](../../diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md):

1. a `EXECUTIVE_MISSION` declara `required_level: PRODUCAO|INTERNO`;
2. Negócios o copia sem alteração para `BUSINESS_JUDGMENT_PACKAGE`,
   `MATRIX_EXCHANGE_MESSAGE` e `BUSINESS_RETURN`;
3. o Diretor é o único produtor de `JUDGMENT_REQUEST` e o único receptor direto de
   `JUDGE_REPORT`;
4. Negócios consome o retorno por `verdict + required_level`: produção exige `VALIDATED`;
   uso interno admite `VALIDATED` ou `ACEITO_USO_INTERNO`;
5. a nota externa é inteira (`10`, `7–9`, `0–6`); o corte decimal `9,5` continua apenas na
   avaliação interna de Negócios.

## Consequências

- O pacote de Negócios funciona com os schemas vigentes sem editar a frente paralela.
- Nenhuma rota direta é inventada.
- Proposta puramente comercial ainda depende de o CEO incluir o Diretor para atravessar o gate.
- O organograma e a skill dos Juízes permanecem semanticamente divergentes até uma migração coordenada.

## Alternativas rejeitadas

### Negócios chamar os Juízes diretamente

Alinha-se ao organograma, mas viola skill, contrato e schema já materializados dos Juízes. Só pode ser adotada junto com a atualização e regressão daquela frente.

### CEO como broker operacional

Evita a matriz, porém empurra coordenação operacional ao CEO e dilui sua fronteira executiva.

### Negócios produzir o próprio veredito

Viola independência, confunde score interno com julgamento e elimina o gate.

### Pular Juízes enquanto a frente não estiver pronta

Viola o organograma e as Regras de Ouro.

## Critério para revisão

Reabrir este ADR apenas quando a frente de Juízes:

- aceitar remetentes departamentais autenticados;
- devolver veredito ao produtor e manter o Diretor informado;
- atualizar schema, contrato, testes e regressões;
- preservar a independência do painel.

Até lá, o contrato materializado mais restritivo prevalece.
