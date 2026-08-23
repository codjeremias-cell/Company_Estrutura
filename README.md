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
são **701 arquivos** de um total de **17.710**. A diferença não é curadoria editorial: são **31
pastas de campanha datadas**, com **17.009 arquivos**, removidas por um motivo único e verificável —
elas carregam **caminhos absolutos da máquina de origem** dentro dos artefatos, e publicá-las
exporia o layout de pastas e a conta de usuário local.

**Consequência declarada, e ela é a parte que costuma ser omitida em vitrine: a cadeia não roda
aqui.** Os 16 validadores estão presentes e íntegros, mas 12 dos 16 pacotes reprovam nesta árvore —
porque a documentação **linka** as campanhas removidas, o `departamento-registros` exige uma pasta
legado para prova de integridade, e o CEO valida rodadas de julgamento que viviam lá. **As campanhas
não eram arquivo morto: eram carga.** Quem clonar isto e rodar `evals/validate_workflow.py` vai ver
vermelho, e o vermelho é honesto — é o preço de não publicar os caminhos.

**Links internos quebrados: 12 de 1.287 (0,9%).** Onze são consequência da remoção e apontam para
`remedicao-dos-sete-2026-08-03`, `forward-test-cadeia-rodada3`, `rejulgamento-rodada2-2026-07-31` e
`julgamento-nove-departamentos-2026-08-04`. O décimo segundo já estava quebrado na árvore completa —
um `](alvo)` literal, deixado por engano em
`ceo-maestro/evals/forward-test-julgamento-rodada3/04-JUDGE_OPINION-robustez-e-evidencia.md`.

---

## O número da cadeia — e a que árvore ele pertence

> **2096/2096 → 2113/2113, ZERO FAIL, 16 de 16 pacotes limpos, motor compartilhado 96/96.
> Medido em 2026-08-22, na árvore COMPLETA do repositório privado — não nesta.**

A data não é enfeite. Este projeto já carregou por semanas um `1531/1531 PASS` **sem data**, e o
commit anterior desta mesma vitrine ainda o repete no título — em 2026-08-06 mediu-se que **onze dos
quinze** `PLACAR.md` repetiam aquele número **no presente** enquanto a rodada daquele dia tinha
falhas. Dentro da Estrutura isso hoje é impedido por trava (`validate_placar_nao_declara_cadeia`);
aqui fora, a regra é a data. **Número de cadeia sem data não entra.**

Um detalhe que vale mais que o número: o denominador **também** adoece quando a casa adoece. Um
validador que reprova cedo executa menos casos — o `departamento-negocios` media 106 casos enquanto
estava vermelho e mede 238 limpo. Placar de cadeia suja não é comparável com o de cadeia limpa.

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
