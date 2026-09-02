<!-- conselho-da-empresa/LEIA-ME.md -->
# Conselho da Empresa

Gaveta. Não é capacidade: não tem `SKILL.md`. Os quatro pacotes moram em
`agentes/`, o mesmo ninho que a Estrutura já usa para quem não é gerente —
sem isso, cada `SKILL.md` aqui seria lido como pacote gerente e o validador
do CEO cobraria contrato de doze seções e `evals/`.

Apontar "montar da árvore" para `ceo-maestro` **não** puxa os conselheiros —
e é isso que se quer: o quadro funcional continua com um topo só. Conselheiro
não é funcionário e não responde ao CEO.

## Os quatro que deliberam

| pasta | assento | o que a mesa pergunta |
|---|---|---|
| `conselho-negocios` | negócios | vale a pena? quem paga? |
| `conselho-tecnologia` | tecnologia | dá para construir e manter? |
| `conselho-planejamento` | planejamento | quanto custa, quanto demora, quem faz? |
| `conselho-seguranca` | segurança | como isso é abusado, e o que se perde? |

Cada um é **agente** (`SKILL.md` + `CONTRATO-DE-COMPROMISSO.md`) com
`papel: conselheiro` no frontmatter.

> **Correção de 2026-08-18.** A versão anterior dizia que sem `papel:
> conselheiro` "a tela Conselho da GradUP não o oferece como cadeira". **Isso
> nunca foi verdade**: não existe coluna `papel` em `cargos`, nem filtro na
> tela — ela oferece **todos** os cargos do organograma e o dono escolhe quais
> sentam. A chave continua útil como documentação do pacote; ela não é lida
> pela GradUP.

## O quinto, que preside

| pasta | assento | o que ele faz |
|---|---|---|
| `conselho-presidente` | presidência | onde a mesa está: converge no quê, diverge em quê, o que falta |

Ele **não delibera**: não dá parecer sobre a pauta, não escolhe lado, não vota
e não desempata. A fala dele é a **síntese** — o mapa da conversa, não uma
opinião a mais.

Presidir é **papel na sessão, não atributo do cargo**: na GradUP quem preside é
marcado na abertura da sessão (`sessao_cadeiras.preside`, migração `033`), e o
mesmo cargo pode presidir uma e deliberar em outra.

## O que não entra

`conselho-decisor` (rascunho em `Sala de Conselheiros/`) **não é conselheiro**.
Um quinto agente que "decide e assina" colide com "a decisão final é do CEO ou
do proprietário".

**Essa recusa continua de pé**, e o `conselho-presidente` acima **não a
contraria**: ele não decide e não assina. O que ele faz é organizar, e a
deliberação segue sendo proposta até o dono ratificar.

O rascunho original permanece na Sala, para histórico. Não importe.

### O que mudou na outra metade do argumento, e por que

O texto de 2026-08 também dizia que consolidar parecer "já é o fluxo da tela
Conselho + o gate do Jeremias + o CEO". **A medição derrubou isso.**

Na sessão de 4 cadeiras de 2026-08-17 (Empresa GradUP, tarefa 120), a mesa
convergiu na rodada 3 — três concordâncias e uma revisão de posição — e
**ninguém consolidou**. O dono ficou com doze falas e a tarefa de lê-las; uma
cadeira deixou pergunta de governança sem resposta e nada no registro dizia o
que a mesa tinha acordado. A tela **mostra** a deliberação; ela não a organiza.
O "gate do Jeremias" era o Jeremias fazendo o trabalho à mão.

Com o assento, a síntese de uma sessão real abriu com **"Nenhuma"** em pontos
de concordância — recusando fabricar consenso — e nomeou uma divergência que
**nenhuma fala continha**: duas cadeiras estavam respondendo perguntas
diferentes sem perceber. Isso é produto de ler as falas juntas, e nenhuma
cadeira faz sozinha.

## Planejamento: a skill já existe

Não copie `especialista-planejador`. O conselheiro de planejamento **carrega**
essa skill. No acervo da GradUP ela já entra como **skill** (Catálogo). Depois
de importar o agente `conselho-planejamento` e vinculá-lo a um cargo, ligue a
skill ao mesmo cargo (`cargo_skills`) — são os três passos de sempre:
importar, reapontar, política.

Não reimporte `planejador-estrutura` da Estrutura como agente: lá ele tem
contrato, no acervo ele é skill, e a espécie não troca.

> **O nome mudou em 2026-09-02, e é por isso que esta frase distingue os dois.** O pacote da
> Estrutura chamava-se `especialista-planejador` — o mesmo nome da skill do Catálogo que este
> conselheiro carrega. Enquanto a homonímia existiu, quem invocava o nome recebia **sempre** a do
> Catálogo, que é o que este arquivo pede: o comportamento aqui não muda. O que muda é que agora
> os dois nomes são distintos, e a advertência acima deixou de depender de o leitor saber qual das
> duas o runtime entregaria.

## Como importar na GradUP

1. Acervo → apontar **cada pasta** em `agentes/` (`conselho-negocios`, …,
   `conselho-presidente`), não esta gaveta.
2. Organograma → criar um cargo por conselheiro e vincular o agente.
3. No cargo de planejamento, vincular também a skill `especialista-planejador`.
4. Política: o `allowed-tools` do frontmatter já declara leitura + `Skill`.
   A empresa não aplica sozinha sobre lista declarada — confira na tela.
5. Tela Conselho → ao abrir a sessão, marque as cadeiras e escolha no campo
   **"Quem preside"** o cargo do `conselho-presidente`. Sem isso a sessão nasce
   sem presidente e o botão "Pedir síntese" não aparece — a mesa delibera, e
   ninguém consolida.

Corrida de conselheiro é de **leitura**. Escrita, shell e rede ficam fora
até o dono declarar o contrário, cargo a cargo.
