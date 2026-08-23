# Fontes canônicas e fronteiras

Síntese congelada em 2026-07-26. As fontes abaixo foram usadas para escrever o
novo pacote; **não são dependências nem fallback runtime**. O Departamento
opera apenas com seus arquivos locais e agentes verificados.

| Fonte canônica | SHA-256 do `SKILL.md` | Absorvido | Não absorvido |
|---|---|---|---|
| `qa-usabilidade` | `a310bef76b8c633c7611aedfe3547cf7e80c9c75eeb93b4fb601657f3015eb3e` | risco, técnicas, 12 dimensões, estados, UX/a11y | autoridade de veredito, agora dos Juízes |
| `testador-real` | `523117ffc88fb9b6ad45c5e059b4617ce00495f3f7b84144b5b08fbd1e082c22` | execução real, perfil de projeto, prova, regressão, limpeza | identidade universal como substituta de agente |
| `gradup-testador` | `bb1289c00b7a3b5cd4da89675e0d3dff57d3b857ab0f7421c84ee99df5b71991` | exemplo de instância por projeto e PASS observável | rotas, papéis e paths do Gradup |
| `testador-jogos` | `800fa6cf5bae02d40d1859a79d9baffdc5cf1b1b367397fb9bce48a636f4e68c` | personas, repetição, breaker, evidência × opinião | rubrica específica de game fora de jogos |
| `requisitos-descoberta` | `3ff5b7d68fbe18e8287d7fc929d34d8cbdaafb3e7e49830febf1ee4606150dea` | objetivo e aceite observáveis | descoberta de escopo como responsabilidade de QA |
| `arquiteto-software` | `0ae60d638ca221b2a3842b74f10cd61b1ee791357c6544b179b2c503829d0e37` | ISO 25010 e atributos mensuráveis | decisão arquitetural |
| `arquiteto-dados` | `df101721b5488c9791ab345bbf17d8bc87d65272269e7f2f32c1058cf3b7b211` | invariantes, reconciliação, migração e contratos | modelagem/evolução dos dados |
| `designer-ux-ui` | `b2df6cf23286b8af191251319f261d92b2ece2e1a1f29a401e715c5824b8fd3f` | Nielsen, WCAG, tarefa, data-viz | criação/redesign da experiência |
| `javafx-dashboard` | `51364fd8e87cd8b8f0d1656aa4640ad4a89cb3912ceb3a923833b4208ca2a9c3` | fonte/fórmula, sem-dado, frescor, reconciliação, 5 s | APIs JavaFX fora de JavaFX |
| `docs-projeto` | `86edfa6c74f3459293edd977f3ed4906e8f2e452522bbdea046bde60fcb3c74d` | fidelidade da documentação ao real | autoria de documentação |
| `especialista-seguranca` | `82b641615f1fca060f2e6e61b4b53550e0069511aca0e31f3962ad45c3655c0e` | casos de abuso recebidos e execução delimitada | threat model e veredito de segurança |
| `estado-projeto` | `167793fe6bb03a6c3c2f9a896863ad0b6c833e8e62d7ac7cdb830ad25bc08693` | IDs, transições e artefatos retomáveis | escrita de estado por cada agente |
| `assistente-deterministico` | `808ac4b5d17b7cbc80d93f5214c3c1ca4302df4e4afc36c13ae23f864781befe` | schema fechado, regras deriváveis e auditabilidade | execução de QA ou orquestração |
| `auditor-responsabilidades` | `cfeb64724fe767a3ff2da4370fe002d67fd90c9a7306f14a5c679a78a56baf75` | prova fresca, intenção, escopo e rastreabilidade | auditoria/global gate |

## Decisões de uso

- `assistente-deterministico` é **apoio de contrato**, não membro do time.
- `estado-projeto` é **infraestrutura de rastreio**, não executor. Agentes
  devolvem artefatos; a gerente é a única escritora do estado compartilhado
  quando o fluxo externo autorizar.
- `gradup-testador` é exemplo de instanciação, não base genérica.
- `testador-jogos` só amplia o perfil jogo e o método de personas.
- Skills de stack fornecem critérios quando o alvo usa aquela stack; não são
  incorporadas integralmente ao Departamento.
- Pesquisa externa não foi necessária: o cânone cobre o método; a lacuna era a
  materialização dos agentes.

## Fronteiras organizacionais

| Capacidade | Entrega a QA | Continua dona de |
|---|---|---|
| Requisitos | critérios e objetivo | intenção e escopo |
| Arquitetura | drivers/limites | decisão arquitetural |
| Dados | invariantes/contratos | modelo e evolução |
| Design | tarefas/UX/a11y | solução de experiência |
| Segurança | casos de abuso/limites | risco e veredito de segurança |
| Desenvolvimento | candidato e fix | implementação |
| QA | prova executada e recomendação técnica | estratégia e evidência de qualidade |
| Auditoria | prova de conformidade | governança |
| Juízes | críticas/nota/veredito | validação independente |

## Concluído quando

O método local funciona sem carregar qualquer fonte canônica; cada influência
tem proveniência e uma fronteira que impede duplicação de autoridade.

