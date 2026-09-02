# Adendo de contagem — `departamento-arquitetura-dados`, 2026-08-23

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) declara números corretos **na data em
> que foram medidos**, e este adendo **não altera nenhum deles**. A receita devolve outro número
> hoje porque a tarefa 97 mexeu neste pacote. Redeclarar ao lado, por adendo datado e **no mesmo
> ato** que muda a contagem, é o que esta casa aprendeu depois que uma canonização somou 47 casos
> em 15 validadores e redeclarou em 1.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-23, após a tarefa 105 | 129/129 |
| **vigente em 2026-08-23, após a tarefa 97** | **131/131** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-dados"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: 129 → 131 é +2

| caso | o que planta |
|---|---|
| contratos de gerente na anatomia canônica | o caso **positivo**: este pacote passa a exercer a trava global, que antes rodava em 5 dos 16 |
| anatomia de contrato acusa raiz inexistente | o par **negativo**, exigido pela regra do passo 9 (negativos ≥ positivos). Ele passa uma raiz que não existe e cobra que a trava **acuse** — sem ele, o positivo sozinho corrói a margem, e em `conteudo-marketing` e `registros` ela quebrou na hora |

**Um caso positivo nunca entra sozinho.** A regra do passo 9 é publicada por 3 dos 16 pacotes; nos
outros treze ela não aparece. Acrescentar o par em todos os onze — e não só nos dois que doeram —
é o que impede a próxima adição de quebrar os próximos dois.


## A linha que a trava deste pacote lê

Este é o **único** dos dezesseis com a trava `placar declara a contagem vigente do
validador`. Ela procura a linha abaixo no `PLACAR.md` **e em todos os adendos**, e
toma a **última** — por ordem lexicográfica do nome, que abre pela data. Sem ela
aqui, a redeclaração não chega à trava e o pacote não fecha: foi exatamente o que
impediu o reselo de convergir em cinco rodadas. O `PLACAR.md` **não** se reescreve —
ele é o registro da rodada em que foi escrito.

| artefato | resultado | executado |
|---|---|---|
| Validador determinístico do Departamento | 131/131 PASS | **sim** |


## O que a tarefa 97 decidiu, e por quê

`validate_contratos_de_gerente` era chamada por **5 dos 16** validadores, e os cinco não tinham
padrão: dois nós de topo, dois departamentos comuns e o pacote mais novo. Não havia motivo escrito
em lugar nenhum para só cinco a rodarem. Ela foi promovida a **obrigatória** — decisão (a) de
Jeremias, em 2026-08-23 — e a chamada entrou nos onze restantes, **derivada do estilo que cada
arquivo já usava**, com o par negativo ao lado.

`validate_adr_series` **não** foi promovida junto, e a razão é de desenho: promover as duas deixaria
`FUNCOES_DE_ESTRUTURA` e `FUNCOES_OBRIGATORIAS` idênticas, o conjunto **complementar** ficaria vazio,
e a trava de cobertura — que exige "chame alguma função complementar" — reprovaria os dezesseis de
uma vez. Ela fica como a única complementar.
