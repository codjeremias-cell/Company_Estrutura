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
são **726 arquivos espelhados** de um total de **18.957** — mais este `README.md` e o `.gitignore`,
que existem só aqui. A diferença não é curadoria editorial: são **45 pastas de campanha**, com
**18.231 arquivos**, removidas por um motivo único e verificável — elas carregam **caminhos
absolutos da máquina de origem** dentro dos artefatos, e publicá-las exporia o layout de pastas e a
conta de usuário local.

**A exclusão foi remedida em 2026-09-02, não repetida de memória.** Um detector de 17 padrões
(caminho absoluto, conta local, e-mail, telefone, CPF/CNPJ, chave PEM, tokens AWS/GitHub/OpenAI,
`Authorization`, senha atribuída, string de conexão, IP privado…) rodou sobre os arquivos que
entraram **e** sobre uma campanha excluída, como braço de controle. Nos que entraram: **zero
ocorrências reais**. No braço de controle: **17**, exatamente os caminhos absolutos que a regra
cita. *Zero dos dois lados seria suspeita de detector cego, não prova de árvore limpa* — por isso o
controle existe.

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

Na árvore completa, privada, **os mesmos 16 pacotes fecham `2202/2202`, ZERO FAIL**, no mesmo dia.
A diferença entre os dois números não é qualidade: é quanto da carga cada árvore tem.

**Links internos quebrados: 16 de 1.327 (1,2%) — medido em 2026-09-02.** Quinze são consequência da
remoção e apontam para `remedicao-dos-sete-2026-08-03`, `forward-test-cadeia-rodada3`,
`rejulgamento-rodada2-2026-07-31`, `julgamento-nove-departamentos-2026-08-04`,
`compliant-porta-unica-2026-08-01` e `medicao-comportamental-2026-09-01`. O décimo sexto já estava
quebrado na árvore completa — um `](alvo)` literal, deixado por engano em
`ceo-maestro/evals/forward-test-julgamento-rodada3/04-JUDGE_OPINION-robustez-e-evidencia.md`.

Eram 12 de 1.287 em 23/08/2026. **Subiu porque a fonte cresceu, e caiu um** quando os adendos de
`PLACAR` voltaram: o alvo existia e o link não achava.

---

## O número da cadeia — e a que árvore ele pertence

> **2202/2202, ZERO FAIL, 16 de 16 pacotes limpos. Medido em 2026-09-02, na árvore COMPLETA do
> repositório privado — não nesta.** O número anterior deste README era `2096/2096 → 2113/2113`,
> de 2026-08-22, e fica registrado aqui em vez de apagado.

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
