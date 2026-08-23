# Tracks, geradores e a regra de quem conduz

O acervo tem **31 geradores de desenvolvimento** em cinco tracks. O time deste Departamento tem a
forma do acervo, não uma forma inventada.

## A regra

> **Existe gerador de track para a tarefa? Ele conduz; o agente revisa.**
> **Não existe? O agente implementa direto, e diz que não existia.**

Herdada da canônica `dev-senior`: *"os geradores do track são o braço determinístico desta lente;
quando existir gerador para a tarefa, ele conduz e esta lente revisa"*.

O motivo é operacional, não hierárquico: o gerador é determinístico e já carrega as convenções do
track — pacote, nomenclatura, RO específica. Reimplementar à mão o que ele gera introduz variação
sem ganho. Mas gerador não pensa: **a revisão é obrigatória** e é o que o agente acrescenta.

Todo `DEV_RETURN` declara `generator_used` — o nome do gerador, ou `n/a` **com motivo**. `n/a`
genérico é tratado como gerador não procurado.

## Os cinco tracks

### 1. Java e Spring Boot — `agente-java-e-spring`

| Gerador | Produz |
|---|---|
| `java-project-bootstrap` | esqueleto do projeto, build, estrutura de pacotes |
| `java-db-foundation` | fundação de acesso a banco |
| `java-jdbc-dao` | DAO em JDBC, com `try-with-resources` (RO-10) |
| `java-service-usecase` | serviço e caso de uso |
| `java-logging-log4j2` | logging estruturado |
| `springboot-entity` | entidade JPA |
| `springboot-repository-service` | repositório e serviço Spring |
| `springboot-controller-thymeleaf` | controller e view Thymeleaf |

RO do track: **RO-04** (acesso parametrizado), **RO-10** (JDBC seguro, `try-with-resources`),
**RO-SB2** (Flyway dono do schema, `ddl-auto=validate`, engine único dev = prod), **RO-SB3**
(transação em operação multi-passo), **RO-SB6** (Thymeleaf com CSRF e a11y).

### 2. JavaFX desktop — `agente-javafx-desktop`

| Gerador | Produz |
|---|---|
| `javafx-app-shell` | casca da aplicação, navegação |
| `javafx-screen-fxml` | tela FXML |
| `javafx-dashboard` | painel e KPIs |
| `javafx-theme-tokens` | tokens de tema |
| `java-javafx-entity` | entidade do track |
| `java-package-desktop` | empacotamento desktop |

Fronteira dura: **nunca forçar padrão web em JavaFX**. O `-fx-effect` do CSS do JavaFX aceita só
`dropshadow` e `innershadow`; não há `backdrop-filter`; `TranslateTransition` não dispara layout,
animar `prefHeight` dispara. Primitiva nomeada, sempre.

### 3. Web frontend — `agente-web-frontend`

| Gerador | Produz |
|---|---|
| `frontend-stack-decisor` | decisão de stack front |
| `web-component` | componente |
| `web-vanilla-supabase-pwa` | PWA vanilla com Supabase |
| `web-data-layer` | camada de dados do front |
| `design-tokens-gen` | JSON DTCG + CSS a partir dos tokens que Design decidiu |

RO do track: **RO-W1** (anon key do Supabase é pública por design), **RO-W2** (RLS é a fronteira de
segurança — checklist em todas as tabelas e bucket privado antes de expor), **RO-W8** (`catch` nunca
só `console.error`; estados carregando/erro/vazio; data local, não UTC cru).

Linguagens: HTML, CSS, JavaScript, TypeScript, JSX/TSX quando o stack decidido os usar.

### 4. Tauri desktop — `agente-tauri-desktop`

| Gerador | Produz |
|---|---|
| `desktop-tauri-scaffold` | esqueleto Tauri |
| `desktop-feature-crud` | feature CRUD |
| `desktop-packaging` | empacotamento e distribuição |

RO do track: **RO-DT3** — banco local SQLite com migração **versionada**; o plugin aplica o *up* no
boot, o *down* é artefato manual de dev. Gravação segura (temp + rename); teste nunca contra dados
reais.

### 5. Mobile Flutter — `agente-mobile-flutter`

| Gerador | Produz |
|---|---|
| `mobile-flutter-scaffold` | esqueleto do app |
| `mobile-flutter-feature` | feature |
| `mobile-flutter-firebase` | integração Firebase |

Linguagem: Dart. Fronteira: padrão mobile não se transporta para desktop sem motivo observado, e
vice-versa.

## Os três transversais

**`agente-persistencia-e-sql`** — implementa o modelo que o `departamento-arquitetura-dados`
desenhou: DDL, migração versionada, acesso parametrizado, índice, leitura de plano de execução,
fronteira transacional. Atravessa os cinco tracks. **Não decide o modelo** — recebe grão, chaves e
plano de expand/contract prontos.

**`agente-revisao-e-refatoracao`** — revisa a saída dos outros, nunca a própria. Clean Code, Big-O
quando incide, GoF só quando resolve problema real, Cerca de Chesterton antes de remover, e colheita
dos marcadores `ponytail:` para a fila de dívida.

**`agente-testes-e-depuracao`** — escreve os testes, **executa a bateria** e reporta
`PASS/FAIL/SKIP` com evidência fresca. Conduz o protocolo de depuração: laço vermelho-verde, causa
raiz antes do fix, Regra dos Três.

## Track ausente

Pedido em stack sem gerador e sem agente — Go, Python, .NET, React Native, Kotlin nativo — **não se
improvisa**. Sai `DEV_CAPABILITY_GAP` ao Diretor, com a stack nomeada e o que seria preciso. Track
novo entra por ADR, com os geradores correspondentes declarados; agente sem gerador que o sustente é
agente sem braço.
