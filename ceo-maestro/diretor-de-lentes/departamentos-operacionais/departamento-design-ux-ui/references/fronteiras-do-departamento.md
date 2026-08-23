# Fronteiras — onde Design começa e onde termina

## A navalha

> **Decidir e especificar a experiência é daqui.**
> **Materializar o artefato — código, tokens gerados, imagem, protótipo executável — é do
> `departamento-desenvolvimento`.**
> **Caçar defeito no que já existe, com execução e evidência, é do `departamento-qa-usabilidade`.**
> **Comparar alternativas e dar nota é do `departamento-juizes`.**

É a Lei de Ferro do legado — *orquestre, não produza* — com endereço para cada metade.

## Tabela de desempate

| A pergunta é… | Dono | Por quê |
|---|---|---|
| "que experiência esta tela deve entregar?" | **Design** | é a decisão de produto visual |
| "qual o fluxo antes da tela?" | **Design** | fluxo é desenho, não implementação |
| "quais estados esta superfície precisa ter?" | **Design** | estado faltante é defeito de desenho |
| "que cor, tipografia, espaço e motion?" | **Design** | é a linguagem visual |
| "qual token semântico representa isso?" | **Design** | tokens são o contrato design↔código |
| "o contraste real dá 4.5:1?" | **Design** | é a11y medida na especificação |
| "que gráfico serve a esta intenção?" | **Design** | escolha de data-viz é decisão de leitura |
| "como escrevo esse componente?" | **Desenvolvimento** | é implementação |
| "gera o JSON de tokens e o CSS" | **Desenvolvimento** | aqui se decide o valor, lá se materializa |
| "cria essa imagem/ícone" | **Desenvolvimento** | é produção de ativo |
| "esta tela pronta tem defeito de usabilidade?" | **QA e Usabilidade** | é caça a defeito com execução |
| "qual destas três alternativas é melhor?" | **Juízes** | é julgamento comparativo |
| "isso muda a viabilidade da arquitetura?" | **Arquitetura de Software** | é estrutura |
| "esse fluxo expõe dado sensível?" | **Segurança** | é modelagem de ameaça |

## Regra V — risco alto exige segurança antes do aceite visual

Herdada do legado: em fluxo financeiro, autenticação, pagamento, permissão, privacidade ou dado
sensível, a dependência para o `departamento-seguranca` sai **antes** de o `DESIGN_GATE` fechar.
Aprovar a estética de um fluxo de pagamento sem esse passo é aprovar risco por omissão.

## Regra W — o que precisa ser produzido sai como dependência

Precisou de código, arquivo de tokens, imagem, protótipo executável ou teste executado? Sai como
`delegated_dependency` ao Departamento dono, **com o que já está decidido aqui anexado**: fluxo,
estados, tokens semânticos com valor, critérios de a11y com o valor medido, primitivas do stack.
Dependência sem esse anexo entrega ao vizinho um problema em branco.

E ela **não sai enquanto o `DESIGN_GATE` estiver `PENDING`** — mockup-first não é conselho.

## O que este Departamento nunca entrega

- código de tela (HTML, CSS, FXML, JSX), arquivo de tokens gerado, imagem ou protótipo executável;
- resultado de teste executado — `pass` e `fail` daqui são `0` por `const`;
- nota, ranking ou veredito comparativo entre alternativas;
- decisão de arquitetura, dados, segurança ou negócio.

## Zona cinzenta declarada

**Tokens** aparecem em dois lugares: **decidir** o nome semântico e o valor é daqui; **gerar** o
JSON DTCG e o CSS é do Desenvolvimento (no catálogo, `design-tokens-gen`). O contrato é a fronteira.

**Usabilidade** também: definir o critério e o valor esperado é daqui; **executar** o teste com
usuário e produzir `PASS/FAIL` é do `departamento-qa-usabilidade`. Este Departamento marca
`UNVERIFIED` e delega — nunca declara aprovado o que não mediu.
