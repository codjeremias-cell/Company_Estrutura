# Adendo de contagem — `departamento-arquitetura-dados`, 2026-08-08

> **Redeclaração no mesmo ato da mudança.** A tarefa 71 acrescentou **um caso** a cada um dos
> dezesseis validadores canônicos: `validate_contagem_ligada_ao_instrumento`, que exige que a
> contagem publicada aponte para o **digest do instrumento que a produziu**. Contagem que muda sem
> redeclarar é a deriva que, em 2026-08-05, derrubou o `C04` de oito pacotes na rodada seguinte.

## Contagem vigente

| medição | resultado |
|---|---|
| Validador determinístico do Departamento | 129/129 PASS | **sim** |
| **vigente em 2026-08-08** | **129/129** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes/departamentos-operacionais/departamento-arquitetura-dados"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta desta data

`126/126` → **`129/129`**, isto é **+3 casos**, das tarefas 71 (dois) e 84 (um): *a contagem publicada
aponta para o digest do instrumento vigente*, *as travas do módulo compartilhado não estão
neutralizadas* e *toda pendência declarada nomeia quem responde por ela*.

> **Correção de 2026-08-08, no mesmo dia.** Esta linha chegou a dizer `126/126 → 128/128` com a
> tabela acima em `129/129` — número do delta contradizendo o número vigente, dentro do documento
> que existe para redeclarar contagem. Foi edição minha em duas passadas, com a segunda batendo num
> texto que a primeira já havia mudado. Fica registrado em vez de apagado: é a mesma classe que a
> tarefa 71 fechou por mecanismo, e ela reapareceu à mão, no arquivo de prosa que nenhuma trava lê.

## Por que o `PLACAR.md` não foi tocado

Este pacote já tinha, sozinho, a forma mais próxima do que a T71 generalizou: uma trava local que
lê a linha da contagem e a compara com o número de casos da corrida, tomando o **adendo mais
recente** como fonte e deixando o `PLACAR.md` como registro da rodada em que foi escrito. Na
primeira tentativa desta frente eu reescrevi aquela linha de `122/122` para `127/127` — e isso é
alterar registro histórico, exatamente o que o comentário do validador proíbe em prosa. Revertido;
o número novo entra por adendo, que é a forma da casa.

## O que mudou de mecanismo

O achado `EA-01` da remedição de 2026-08-03 é bloqueante em sete pacotes e diz que a contagem é
publicada **sem ligação com a versão do instrumento**. Medido por execução em 2026-08-08: dos 16
pacotes, 15 publicavam número próprio e **os 15 estavam defasados**. Este aqui publicava `122/122`
no placar e `126/126` no último adendo, contra `126/126` vivos — era o mais próximo de estar certo,
e ainda assim ninguém conseguia ligar o número ao instrumento.

Agora o `evals/PLACAR.md` carrega o **selo de contagem**, gerado por
`_compartilhado/selar_contagem.py`, com a contagem, o `sha256` normalizado do
`evals/validate_workflow.py` e a data. Editar o validador sem regenerar o selo derruba a bateria
deste pacote: o número não consegue mais envelhecer em silêncio.
