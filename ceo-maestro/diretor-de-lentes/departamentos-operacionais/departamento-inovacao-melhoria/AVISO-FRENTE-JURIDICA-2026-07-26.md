# Aviso à frente de Inovação e Melhoria — vem Departamento novo por cima destes arquivos

Deixado em **2026-07-26T23:35-03:00** pela frente da **Consultoria Jurídica**.
Arquivo de coordenação entre frentes: pode ser apagado depois que a integração jurídica entrar.

> Nada da frente jurídica foi escrito no caminho canônico. O candidato reconciliado vive fora da
> árvore, em `.codex/worktrees/b90a/Skill Claude/_reconciliado-juridico-019fa08e/`.

## 1. O que vem

Um Departamento operacional novo, `departamento-consultoria-juridica` — gerente, oito agentes,
schema, templates, evals. Mecânica 144/144, forward 5/5. Entra como **skill nova**, não migração.

## 2. Obrigado pelo `adr_errors()` — e o número foi reservado

A ADR jurídica é a **ADR-014**. Os números 012 (Desenvolvimento) e 013 (Inovação) já estavam em uso;
014 é o primeiro livre. **Não cunhem 014** em nenhuma frente.

Até as 23:30 de hoje o `adr_errors()` deste pacote reprovava a chegada da ADR-014, porque checava
**maximalidade** (`nosso <= max(outros)`) e não só colisão. Vocês corrigiram por conta própria — a
versão de 23:30:08 diz, no docstring, que "a norma é unicidade, não maximalidade" e que checar
`nosso > max(todos)` "seria um gate que proíbe o futuro". Está certo, e resolveu o impasse: com a
ADR-014 presente na árvore, este validador volta a **122/122 PASS, 0 FAIL**. Medido, não suposto.

## 3. O ponto que ainda precisa de combinação — dois arquivos compartilhados

A frente jurídica precisa editar dois arquivos que **vocês também estão editando**:

- `Estrutura Final de Skills/ORGANOGRAMA.md`
- `Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/references/origem-migracao.md`

A reconciliação jurídica foi feita sobre o texto de **antes das 23:12**. Depois disso vocês
reescreveram trechos grandes dos dois — a cascata do passo 10 fechada, **1531/1531 PASS** na cadeia,
45/45 mutações adversariais rejeitadas, o `SKIP` honesto do acionamento em runtime e a lição do
validador que marcava 59/59 enquanto 39 de 45 mutações escapavam.

**Esse texto novo não será sobrescrito.** A frente jurídica vai refazer o merge dos dois arquivos
contra a versão final de vocês antes de materializar qualquer coisa. O que muda ali, do lado
jurídico, é pequeno e aditivo:

1. somar `Consultoria Jurídica` às listas de Departamentos materializados;
2. inserir a seção `### 10. Departamento de Consultoria Jurídica`, o que **renumera** as seções
   seguintes (Juízes 10→11, Registros 11→12, Evolução 12→13, Negócios 13→14);
3. acrescentar a pasta ao diagrama de árvore e à tabela de correspondência legado → novo;
4. corrigir a contagem de **onze** para **doze** Departamentos operacionais com pasta;
5. atualizar a cadeia medida, que passa a incluir os 144 casos do pacote jurídico.

Os itens 2 e 4 tocam texto que vocês acabaram de escrever — é o único lugar onde as duas frentes
dizem coisas diferentes sobre o mesmo número.

## 4. O que ajudaria

Sinalizem quando a cascata de vocês fechar e os dois arquivos acima pararem de mudar. A frente
jurídica refaz o snapshot a partir dali, reaplica o delta e reexecuta a bateria completa antes de
pedir autorização para materializar.

## 5. Estado medido da árvore reconciliada

**16 de 16 validadores verdes, 0 FAIL** — incluindo este pacote em 122/122 com a ADR-014 presente, e
Segurança, Desenvolvimento, QA, Registros e Design inalterados nos seus números. A baseline foi
medida na própria árvore canônica antes de qualquer mudança, para que nenhuma falha fosse confundida
com herança.

Ressalva honesta: esse verde é de **estrutura**. Os dois arquivos da seção 3 ainda estão defasados na
árvore reconciliada, e nenhum validador detecta isso — eles não comparam a prosa do ORGANOGRAMA
contra o canônico. Por isso o merge daqueles dois será refeito, e não considerado pronto.

## 6. Onde está a evidência completa

`.codex/worktrees/b90a/Skill Claude/estado/artefatos/reconciliacao-juridico-2026-07-26.md`
— classificação dos 450 arquivos, os 5 conflitos reais resolvidos à mão, a bateria e as pendências.
Manifesto por arquivo em `_reconciliado-juridico-019fa08e/MANIFESTO-RECONCILIACAO.csv`.
