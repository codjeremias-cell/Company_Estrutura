# Estrutura Final de Skills — vitrine pública

Uma organização de agentes em **cadeia de comando**: um CEO que roteia e nunca executa, um Diretor
que dirige dez Departamentos operacionais, um Departamento de Juízes que dá nota em camada paralela,
e uma Auditoria que prova conformidade sem pontuar. Cada pacote traz `SKILL.md`,
`CONTRATO-DE-COMPROMISSO.md`, `references/` com protocolo e ADRs, `schemas/` e `evals/` com um
validador determinístico próprio.

As regras da casa, em quatro linhas: nota e veredito são exclusivos dos Juízes; conformidade é da
Auditoria, que prova e não pontua; gerente orquestra e não executa a especialidade; agente é folha e
só fala com a própria gerente. E a que vale mais que as outras — **ausência de evidência permanece
ausência**.

---

## Leia isto antes de tirar conclusão do que está aqui

**Esta é uma cópia parcial, e a palavra é literal.** A fonte é um repositório privado. O que você vê
são **729 arquivos espelhados** de um total de **18.977** — mais este `README.md` e o `.gitignore`,
que existem só aqui. A diferença não é curadoria editorial: são **46 pastas de campanha**, com
**18.248 arquivos**, removidas por um motivo único e verificável — elas carregam **caminhos
absolutos da máquina de origem** dentro dos artefatos, e publicá-las exporia o layout de pastas e a
conta de usuário local.

**A exclusão foi remedida em 2026-09-02, não repetida de memória.** Um detector de **15** padrões
(caminho absoluto Windows e POSIX, conta local, caminho do cofre, `AppData`/`%TEMP%`, e-mail,
telefone BR, CPF/CNPJ, chave PEM, tokens AWS/GitHub/Anthropic-OpenAI, `Bearer`/`Authorization`,
senha atribuída, string de conexão) rodou sobre os arquivos que entraram **e** sobre uma amostra do
conteúdo excluído, como braço de controle. Nos que entraram:
**0 ocorrências reais**. No braço de controle, medido em 2026-09-02: **973 achados em 400
arquivos** — em cheio os caminhos absolutos que a regra cita. *Zero dos dois lados seria suspeita de
detector cego, não prova de árvore limpa* — por isso o controle existe, e por isso `conferir`
**reprova** quando o controle vem zerado.

> **A lista do que é conferido cresceu de quatro para oito em 2026-09-02, e cada entrada tem
> motivo.** `15 padrões` entrou porque este parágrafo dizia **17** enquanto a lista tinha 15, e
> nenhum dos quatro números anteriores olhava para isso. `0 ocorrências reais` entrou porque ele
> *tem* de ser zero, e declarar o zero por extenso faz a prosa reprovar junto com a trava no dia em
> que não for. Os dois de link entraram como custo declarado (abaixo). **Ficam de fora, de
> propósito, os do braço de controle**: dependem da amostra, e travá-los produziria ruído, não
> segurança — de o controle vir zerado cuida a trava `DETECTOR_CEGO`, não o texto.

**Desde 2026-09-02 esta cópia tem um gerador, e a regra deixou de morar só neste texto.**
`publicar_vitrine.py` espelha a fonte pela regra declarada em `vitrine-exclusoes.json` e **reprova
a deriva** em vez de descrevê-la: arquivo da fonte que não esteja publicado **nem** excluído é
`FALHA`, e foi exatamente esse o buraco por onde 25 arquivos sumiram por dez dias. Ele também
confere, contra a árvore, **oito** dos números que este texto declara — se o texto e a medição
divergirem, `numeros` sai vermelho. As travas têm prova de mutação própria
(`prova_mutacao_vitrine.py`, **13/13 mutantes mortos** em 2026-09-02): validador verde não prova
que a trava funciona, prova que nada a acionou.

> **A prova de mutação cresceu de 10 para 13 no mesmo dia, e o motivo é um defeito que ela deixava
> passar.** Ela só exercitava `conferir` — a perna que mede a árvore. A perna que confere a
> **prosa** contra a medição não tinha caso nenhum, e foi por aí que este README publicou *"detector
> de 17 padrões"* com uma lista de 15 sem nada ficar vermelho. Os dois mutantes novos desligam
> exatamente isso: aceitar uma declaração que sumiu do texto, e aceitar um número declarado
> diferente do medido; o décimo terceiro faz o contador de links dar por existente um alvo que
> não existe. **Este `13/13`, porém, não é conferido por máquina** — ele mora na mesma categoria
> dos números do braço de controle: datado, e verdadeiro na data.

**25 arquivos que faltavam sem serem campanha voltaram nesta republicação.** São 18 adendos de
`PLACAR`, um `ROLLBACK.md` e sete peças da prova de sucessão de envelope. Eles não estavam
excluídos por regra nenhuma: nasceram **depois** de 23/08/2026, quando esta vitrine foi montada, e
ficaram para trás porque não havia quem os trouxesse. Cópia pública que envelhece calada é um
defeito, não um recorte.

**Consequência declarada, e ela é a parte que costuma ser omitida em vitrine: a cadeia não roda
aqui.** Os 16 validadores estão presentes e íntegros, mas **12 dos 16 pacotes reprovam nesta
árvore — medido em 2026-09-02** (4 passam) — porque a documentação **linka** as campanhas
removidas, o `departamento-registros` exige uma pasta legado para prova de integridade, e o CEO
valida rodadas de julgamento que viviam lá. **As campanhas não eram arquivo morto: eram carga.**
Quem clonar isto e rodar `evals/validate_workflow.py` vai ver vermelho, e o vermelho é honesto — é
o preço de não publicar os caminhos.

Na árvore completa, privada, **os mesmos 16 pacotes fecham `2203/2203`, ZERO FAIL**, no mesmo dia.
A diferença entre os dois números não é qualidade: é quanto da carga cada árvore tem.

Links quebrados: **18 de 1.329** (1,4%), medido em 2026-09-02. Dezessete são consequência da
remoção e apontam para `remedicao-dos-sete-2026-08-03`, `forward-test-cadeia-rodada3`,
`rejulgamento-rodada2-2026-07-31`, `julgamento-nove-departamentos-2026-08-04`,
`compliant-porta-unica-2026-08-01`, `medicao-comportamental-2026-09-01` e
`medicao-acionamento-2026-09-02`. O décimo oitavo já estava quebrado na árvore completa — um
`](alvo)` literal, deixado por engano em
`ceo-maestro/evals/forward-test-julgamento-rodada3/04-JUDGE_OPINION-robustez-e-evidencia.md`.

Eram 12 de 1.287 em 23/08/2026 e 16 de 1.327 mais cedo em 02/09. **Sobe quando a fonte cresce e
quando entra campanha nova:** os dois últimos são a medição de acionamento, publicada como texto no
`PLACAR` do `planejador-estrutura` e excluída como pasta, pelos caminhos absolutos que os brutos
carregam.

> **Este par de números passou a ser conferido, e por um motivo específico.** Ele descreve o **custo
> da parcialidade**, e custo que ninguém mede vira custo que ninguém vê. Mas ele **não reprova**:
> quebrar link é consequência conhecida da regra de exclusão, e reprovar aqui obrigaria a editar a
> fonte para agradar a vitrine — o inverso de tudo o que esta cópia é. `numeros` apenas impede que
> o texto acima o declare errado. Só links **relativos** entram: conferir URL externa exigiria rede,
> e auditoria que depende de estar on-line não é auditoria.

---

## O número da cadeia — e a que árvore ele pertence

> **2203/2203, ZERO FAIL, 16 de 16 pacotes limpos. Medido em 2026-09-02, na árvore COMPLETA do
> repositório privado — não nesta.** Os números anteriores deste README ficam registrados em vez de
> apagados: `2096/2096 → 2113/2113` em 2026-08-22, e `2202/2202` mais cedo em 02/09.
>
> **O `+1` sobre o 2202 não é ruído: é um caso novo.** O `planejador-estrutura` passou de 18 para
> 19 casos ao ganhar uma trava que compara, byte a byte e a cada execução, a região de doutrina
> desta variante com a da gêmea que vive no Catálogo. Antes, a identidade era conferida por uma
> receita publicada, executada por quem editasse — e **receita não recusa nada**. Nenhum outro
> pacote mexeu um caso.

A data não é enfeite. Este projeto já carregou por semanas um `1531/1531 PASS` **sem data**, e o
commit anterior desta mesma vitrine ainda o repete no título — em 2026-08-06 mediu-se que **onze dos
quinze** `PLACAR.md` repetiam aquele número **no presente** enquanto a rodada daquele dia tinha
falhas. Dentro da Estrutura isso hoje é impedido por trava (`validate_placar_nao_declara_cadeia`);
aqui fora, a regra é a data. **Número de cadeia sem data não entra.**

Um detalhe que vale mais que o número: o denominador **também** adoece quando a casa adoece. Um
validador que reprova cedo executa menos casos — o `departamento-negocios` media 106 casos enquanto
estava vermelho e mede 238 limpo. Placar de cadeia suja não é comparável com o de cadeia limpa.

---

## Uma skill mudou de nome em 2026-09-02, e o motivo é publicável

O pacote `especialista-planejador` passou a se chamar **`planejador-estrutura`**. O nome antigo
**colidia** com uma lente homônima de outro acervo do mesmo autor, e os três runtimes instalados
carregavam a outra — quem digitava o nome recebia a variante errada, **sem aviso**. As duas
compartilham a doutrina byte a byte; o que as separa é o envelope, e na única prova em que se
separaram a outra **aceitou uma rota que não existe**.

A saída foi renomear, não substituir: substituir elegeria um vencedor e seria desfeita em silêncio
pelo deploy de rotina do outro acervo. Renomear **elimina** a colisão — as duas coexistem.

A evidência anterior **não foi reescrita**: a rodada de julgamento e a medição comportamental
julgaram o pacote sob o nome antigo, e os arquivos ficam como estão. Evidência não se atualiza,
ganha sucessora.

---

## Por onde começar

| Arquivo | O que responde |
|---|---|
| [`ORGANOGRAMA.md`](ORGANOGRAMA.md) | quem manda em quem, e quem não pode falar com quem |
| [`AGENTS.md`](AGENTS.md) | a hierarquia inteira em uma página |
| [`GUIA-DE-EXPANSAO-E-MIGRACAO.md`](GUIA-DE-EXPANSAO-E-MIGRACAO.md) | como um pacote novo nasce e é validado |
| [`regras-de-ouro/`](regras-de-ouro/) | a fonte normativa que os 81 contratos citam |
| [`ceo-maestro/SKILL.md`](ceo-maestro/SKILL.md) | a porta única: como uma missão entra |
| [`_compartilhado/`](_compartilhado/) | o motor de verificação que todos os validadores usam |

---

## O que este repositório não é

Não é um produto instalável, não é biblioteca e não recebe issues ou PRs — é o **espelho** de uma
fonte privada, publicado para leitura. Editar aqui não altera nada: a regra da casa é editar a fonte
e replicar, nunca o contrário.

Se algo aqui for útil, a licença de uso é sua; a garantia é a que a ausência de evidência sempre dá.
