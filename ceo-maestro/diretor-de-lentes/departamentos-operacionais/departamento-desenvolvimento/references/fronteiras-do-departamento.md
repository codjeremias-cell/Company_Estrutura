# Fronteiras — onde Desenvolvimento começa e onde termina

## A navalha

> **Implementar é daqui — e provar que roda também.**
> **Decidir a estrutura macro é do `departamento-arquitetura-software`.**
> **Decidir o modelo e a evolução do dado é do `departamento-arquitetura-dados`.**
> **Decidir a experiência é do `departamento-design-ux-ui`.**
> **Caçar defeito de usabilidade e a11y no que já roda é do `departamento-qa-usabilidade`.**
> **Endurecer contra adversário é do `departamento-seguranca`.**
> **Pontuar é do `departamento-juizes`.**

Este Departamento **implementa dentro das decisões dos outros**. Discordar de uma decisão aceita não
autoriza contorná-la: volta ao Diretor.

## Tabela de desempate

| A pergunta é… | Dono | Por quê |
|---|---|---|
| "como escrevo isso?" | **Desenvolvimento** | é microdesign e implementação |
| "esse código está claro?" | **Desenvolvimento** | Clean Code é daqui |
| "por que *esta* query está lenta?" | **Desenvolvimento** | tuning pontual, com plano lido |
| "qual índice criar, na prática?" | **Desenvolvimento** implementa | quem **justifica** o índice é Dados |
| "escreve a migração no Flyway" | **Desenvolvimento** | executar a migração é implementar |
| "esse teste quebra por quê?" | **Desenvolvimento** | depuração |
| "qual o Big-O disso?" | **Desenvolvimento** | fundamento de implementação |
| "separo em dois serviços?" | **Arquitetura** | é limite de módulo |
| "API ou evento entre eles?" | **Arquitetura** | é contrato de integração |
| "o que uma linha desta tabela representa?" | **Dados** | é o grão |
| "como o schema evolui sem downtime?" | **Dados** | expand/contract é desenho |
| "que cor e espaçamento?" | **Design** | é linguagem visual |
| "qual token semântico?" | **Design** decide | aqui se **materializa** |
| "essa tela pronta confunde o usuário?" | **QA e Usabilidade** | é caça a defeito com execução |
| "esse endpoint resiste a um atacante?" | **Segurança** | é modelagem de ameaça |
| "essa entrega merece nota?" | **Juízes** | é julgamento |

## As três zonas cinzentas, declaradas

**Índice.** Dados **justifica** o índice contra um padrão de acesso nomeado; Desenvolvimento
**cria** e mede. Se a medição contradiz a justificativa, isso volta a Dados — não se resolve aqui
mudando o modelo.

**Tokens.** Design **decide** nome semântico e valor; Desenvolvimento **gera** o JSON DTCG e o CSS,
via `design-tokens-gen`. Valor solto no componente é achado de Design; arquivo de token é entrega
daqui.

**Teste.** Escrever e rodar a bateria do código é **daqui** — teste é código. Caçar defeito de
usabilidade e a11y no que já roda é do **QA**. Bateria completa com evidência formal, quando o
projeto a exigir, é do `testador-real`.

## Regra E — o spike é código descartável

A Arquitetura desenha o spike; este Departamento o **executa**. O veredito volta ao ADR dela, e o
código do spike **nunca promove a produção**. Spike que virou feature é decisão de arquitetura
tomada por acidente.

## Regra F — dependência nova não é degrau

Adicionar biblioteca ao projeto é decisão de arquitetura. A escada de decisão para em "dependência
**já instalada**". Precisa de uma nova? Sai como `delegated_dependency` ao
`departamento-arquitetura-software`, com o problema e o que já se tentou.

## O que este Departamento nunca entrega

- decisão de módulo, ownership, topologia ou modo de integração;
- grão, chave, estratégia de histórico ou plano de expand/contract;
- escolha de cor, tipografia, espaçamento ou token semântico;
- veredito de usabilidade, parecer de segurança ou nota;
- afirmação de que algo passou sem a bateria ter rodado contra o candidato entregue.
