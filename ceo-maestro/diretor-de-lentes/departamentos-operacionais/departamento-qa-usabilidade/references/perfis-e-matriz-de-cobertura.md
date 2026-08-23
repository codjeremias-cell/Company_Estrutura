# Perfis e matriz de cobertura

Esta referência especializa os três agentes canônicos por plataforma e
superfície sem criar um agente genérico nem sobrepor propriedade.

## Regra de seleção

Primeiro identificar o **perfil do alvo**. Depois quebrar cada risco em
critérios atômicos e atribuir pela **propriedade medida**, não pela tecnologia.

Um dashboard desktop não pertence inteiro a um agente:

- número certo → funcional;
- carga rápida → não funcional;
- leitura/decisão clara → usabilidade e acessibilidade.

## Matriz

| Perfil | Funcional | Não funcional | Usabilidade/a11y |
|---|---|---|---|
| desktop | boot, navegação, CRUD, persistência, exportação | latência, UI freeze, memória, sessão longa, instalação/update, SO | tarefa, atalhos, foco, densidade, modal, feedback |
| web/mobile | rotas, sessão, formulário, API, sincronização | rede, browsers, dispositivos, consumo, estabilidade, recovery | responsividade, toque, teclado, zoom, reflow, estados |
| API/CLI | contrato, código de retorno, saída e efeito | latência, throughput, timeout, limite, idempotência | ajuda, clareza de erro e recuperabilidade do operador |
| dados/banco | round-trip, constraints, transação, migração, reconciliação | query, locks, concorrência, volume, backup/recovery | compreensão de entrada/erro somente quando há interação |
| dashboard | fórmula, fonte, agregação, janela, partes = total | carga, refresh, exportação, estabilidade em volume | 5 segundos, hierarquia, cor, legenda, teclado, decisão |
| relatório/PDF/documento | conteúdo, filtro, tabela, cálculo, metadado | geração, tamanho, exportação, compatibilidade | leitura, corte, paginação visual, contraste, tags/bookmarks |
| jogo | regra, estados, progressão, save/load | frame time, memória, carga, compatibilidade | onboarding, controles, feedback, dificuldade e diversão |

## Critérios obrigatórios por perfil

### Desktop

- Aplicativo abre no ambiente-alvo ou existe `SKIP`.
- Fluxos centrais e persistência são comprovados.
- I/O não congela a interface quando aplicável.
- Instalação/update só são declarados quando executados.
- Teclado, foco e mensagens acompanham a tarefa.

### Web/mobile

- Papéis, rotas e estados são testados no stack real.
- Vazio, carregando, erro, sucesso, parcial/offline aplicáveis são cobertos.
- Browser/dispositivo físico não disponível vira `SKIP`, nunca “compatível”.
- Responsividade, toque, reflow e tecnologia assistiva têm prova.

### API/CLI

- Entrada, saída, código, efeito e repetição são observáveis.
- Ajuda/erro permite ao operador recuperar.
- Timeout, limite e concorrência exigem autorização e métrica.
- Segredo não aparece em linha de comando, log ou evidência.

### Dados e banco

- Grão/invariante vêm do contrato de dados, não da imaginação de QA.
- Inserts, updates, deletes, rollback e concorrência usam dados de teste
  identificados.
- Partes reconciliam com o todo; nulo, vazio, unicode, limite e overflow são
  considerados.
- Integridade estrutural é funcional; desempenho de query é não funcional.

### Dashboard e visualização

- Cada KPI aponta a fonte, fórmula, janela e frescor.
- Sem dado não é zero.
- Eixos/escalas não distorcem a leitura.
- A pergunta central é identificável no teste dos cinco segundos quando
  aplicável.
- Cor não é único canal; legenda, foco e contraste são verificáveis.

### Relatório, PDF e documento

- Conteúdo e totais reconciliam com a fonte.
- Filtros, período, ordenação, paginação lógica e metadados são testados.
- Render real verifica cortes, órfãos, sobreposição, fontes, tabelas, gráficos
  e impressão.
- Sem renderização/inspeção real, aparência é `SKIP`; abertura/MIME não a
  substituem.
- Documento de instrução é comparado ao comportamento real.

### Jogos

- Regras e progressão são separadas da experiência percebida.
- Usar personas novata, casual/especialista e destruidora quando aplicáveis.
- Repetir sessões para intermitência; distinguir evidência de opinião.
- Backend/servidor usa perfil funcional/não funcional; gameplay usa o perfil
  humano.

## Casos de abuso e Segurança

QA não cria um quarto “agente de segurança”. O Departamento de Segurança
fornece ameaça, critério e limites pela missão do Diretor. O agente funcional
executa comportamento/autorização observável; o não funcional mede
resiliência/limites; o agente de usabilidade verifica mensagens e recuperação.
O veredito especializado permanece em Segurança.

## Quando propor expansão do time

Não criar agente extra por preferência. Abrir proposta de expansão, alterar o
organograma antes e registrar ADR quando evidência mostrar ao menos uma destas
condições:

- capability gap recorrente em ferramenta/permissão incompatível;
- um perfil exige isolamento ou independência que os três não conseguem;
- propriedade legítima não cabe em nenhuma fronteira;
- carga recorrente impede cobertura sem perder qualidade;
- regressão comportamental prova acionamento ou fronteira inadequados.

Até a expansão ser autorizada, registrar `QA_CAPABILITY_GAP`; não improvisar
subskill nem fallback.

## Concluído quando

Cada critério aplicável tem perfil, propriedade, dona, método e prova; lacuna
está explícita; a mesma propriedade não foi entregue a duas agentes.

