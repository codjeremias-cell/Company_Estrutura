# ADR-012 — Desenvolvimento é o Departamento que executa, com oito agentes por track

- **Data:** 2026-07-26
- **Status:** aceito por decisão de Jeremias
- **Decisores:** Jeremias
- **Contexto normativo:** [ADR-002 Juízes](../../../departamento-juizes/references/adr-002-nota-absoluta-e-modo-duplo.md) ·
  [ADR-006 Arquitetura](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md) ·
  [ADR-008 Dados](../../departamento-arquitetura-dados/references/adr-008-dados-skill-nova-e-seis-agentes.md) ·
  [ADR-009 Design](../../departamento-design-ux-ui/references/adr-009-design-sem-painel-cego-e-com-time-fixo.md)

## Contexto

A `lente-dev-senior` é o destino de três Departamentos já migrados: Arquitetura, Dados e Design
todos emitem `delegated_dependency` para cá. Até hoje elas apontavam para o vazio — o forward
comportamental de 2026-07-26 detectou isso de três formas independentes.

Este Departamento também tem a base de apoio mais rica do acervo: **31 das 57 skills do catálogo são
geradores de desenvolvimento**, organizados em cinco tracks. A canônica `dev-senior` já fixa a
relação com eles: *"quando existir gerador para a tarefa, ele conduz e esta lente revisa"*.

## Decisão

**1. Este Departamento EXECUTA — e é o primeiro da estrutura que executa.** Arquitetura, Dados,
Design, Auditoria, Juízes e Evolução têm `test_summary` travado em `0/0/0` por `const`. Aqui **não**:
o `test_summary` do `DEPARTMENT_RETURN` carrega números reais, porque os agentes compilam, rodam a
bateria e produzem evidência. Um Departamento que produz código e não roda o teste entrega
"parece pronto", que a canônica nomeia como não-entrega.

A gerente continua não executando — ela decide, delega e consolida. Quem executa são os agentes.

**2. O modo `JULGAR` não migra.** O legado avalia entrega técnica em escala absoluta 0–10 com corte
9,5. Isso é o `departamento-juizes` (ADR-002). Terceira vez que essa decisão se repete — Arquitetura
e Design já a tomaram. Aqui ela é ainda mais necessária: julgar o próprio código é o conflito de
interesse mais óbvio que existe.

**3. O time é fixo; a descoberta dinâmica de capacidade não migra — mas o gerador conduz.** O legado
monta time por inspeção de runtime a cada missão. A estrutura define time declarado e travado por
`enum`. O que a descoberta dava de útil volta pela regra canônica: **quando existe gerador de track
para a tarefa, o agente o invoca e revisa a saída; quando não existe, implementa direto.** O retorno
declara qual gerador conduziu, ou por que nenhum se aplicava.

**4. Oito agentes — cinco por track, três transversais.**

| Agente | Track / função | Geradores que conduz |
|---|---|---|
| `agente-java-e-spring` | Java puro e Spring Boot | `java-project-bootstrap`, `java-db-foundation`, `java-jdbc-dao`, `java-service-usecase`, `java-logging-log4j2`, `springboot-entity`, `springboot-repository-service`, `springboot-controller-thymeleaf` |
| `agente-javafx-desktop` | JavaFX desktop | `javafx-app-shell`, `javafx-screen-fxml`, `javafx-dashboard`, `javafx-theme-tokens`, `java-javafx-entity`, `java-package-desktop` |
| `agente-web-frontend` | HTML, CSS, JS/TS, PWA | `web-component`, `web-vanilla-supabase-pwa`, `design-tokens-gen`, `frontend-stack-decisor`, `web-data-layer` |
| `agente-tauri-desktop` | Tauri (Rust + web) | `desktop-tauri-scaffold`, `desktop-feature-crud`, `desktop-packaging` |
| `agente-mobile-flutter` | Flutter e Dart | `mobile-flutter-scaffold`, `mobile-flutter-feature`, `mobile-flutter-firebase` |
| `agente-persistencia-e-sql` | SQL e acesso a dado, em qualquer track | — implementa o modelo que `departamento-arquitetura-dados` desenhou |
| `agente-revisao-e-refatoracao` | code review, refatoração, dívida | — |
| `agente-testes-e-depuracao` | testes, bateria executada, depuração | — |

Cinco tracks porque **é o que o catálogo tem**, não porque cinco é um número bonito. Track novo
entra por ADR, com os geradores correspondentes nomeados.

**5. Duas separações por conflito de interesse.**

- quem **implementa** (os cinco de track e o de persistência) **não revisa a própria saída** — a
  revisão é do `agente-revisao-e-refatoracao`;
- quem **implementa** **não declara `PASS` na própria bateria** — quem executa e reporta é o
  `agente-testes-e-depuracao`.

É o mesmo mecanismo do ADR-009 §6, que no forward de 2026-07-26 **pegou cinco falhas reais de
contraste** que nenhum validador via. Aqui ele guarda algo mais caro: a alegação de que o código
funciona.

**6. Gate de saída: bordas cobertas e evidência fresca.** A entrega só fecha com

- **piso de bordas** por unidade de mudança: **vazio + limite + erro**, os três, ou a ausência
  declarada com justificativa;
- **evidência de execução fresca** — bateria rodada contra o candidato entregue, com `PASS/FAIL/SKIP`
  e cada `SKIP` com motivo.

Herdado da canônica: *"código sem os testes rodados não é entrega"*. Faltou um dos três da borda,
ou a prova é de outra versão, a entrega é `INCOMPLETA`.

**7. Os dois marcadores viram campo estruturado.** `SUPOSIÇÃO:` (RO-01 — fonte não confirmada) e
`ponytail:` (simplificação deliberada com teto conhecido) deixam de ser só comentário no código e
passam a ser itens do retorno, com localização, teto e gatilho de revisita. Motivo: o
`departamento-inovacao-melhoria` colhe os `ponytail:` para a fila de dívida, e comentário espalhado
em arquivo não é colhível. O comentário no ponto exato **continua obrigatório**; o campo é o índice.

**8. A escada de decisão é obrigatória, e o que ela nunca corta é mecânico.** Todo trecho novo
declara em que degrau parou — existe? → stdlib? → primitiva da plataforma? → dependência já
instalada? → uma linha legível no ponto de uso? → código novo. E cinco coisas **nunca** são degrau:
validação em fronteira de confiança, tratamento de erro que evita perda de dado, segurança,
acessibilidade e requisito explícito do usuário. O schema recusa `simplificado` nesses cinco.

**9. Regra dos Três, mecânica.** Três correções falhas na mesma causa param a frente: o modelo
mental está errado, e a quarta tentativa é desperdício com risco. `fix_attempts >= 3` exige
escalação ao Diretor, não outra tentativa.

## Consequências

- as dependências que Arquitetura, Dados e Design emitem passam a ter destinatário real;
- a estrutura ganha o primeiro `test_summary` com números — e o `departamento-auditoria` passa a ter
  o que conferir em `EVIDENCIA` que não seja `0/0/0`;
- o `departamento-qa-usabilidade` recebe código com pontos de risco sinalizados, como a canônica
  prevê;
- o `departamento-inovacao-melhoria` — ainda ausente — ganha uma fonte de dívida estruturada.

## Alternativas consideradas

- **Agentes por concern em vez de por track** (implementar, revisar, testar, integrar). Descartada:
  o acervo é organizado por track, e um agente "implementador" genérico não teria como declarar qual
  gerador conduziu. A forma do time segue a forma do acervo.
- **Um agente por linguagem** (Java, JS, Dart, Rust, SQL, HTML/CSS). Descartada: linguagem não é a
  unidade de trabalho — JavaFX e Spring Boot são ambos Java e não compartilham nada operacional;
  Tauri é Rust *e* web ao mesmo tempo.
- **Manter `test_summary` em `0/0/0` por simetria com os outros Departamentos.** Descartada: seria
  simetria comprando mentira. O Departamento que escreve o código é exatamente o que precisa provar
  que ele roda.
- **Deixar a revisão com quem implementou, para economizar rodada.** Descartada pelo mesmo motivo do
  ADR-009 §6 — e agora com evidência empírica de que a separação encontra defeito real.
