# Adendo de contagem — `departamento-auditoria-responsabilidades`, 2026-08-08 (dono por pendência)

> **Redeclaração no mesmo ato da mudança.** Terceira e última forma da tarefa 71 a virar mecanismo:
> `validate_pendencia_tem_dono` acrescentou **um caso** aos dezesseis validadores canônicos. Este
> pacote é a testemunha da prova de mutação, e por isso o adendo mora aqui.

## Contagem vigente

| medição | resultado |
|---|---|
| Validador determinístico da Auditoria | 178/178 PASS |
| **vigente em 2026-08-08** | **178/178** |

O número corrente e o digest do instrumento vivem no **selo** no topo do `evals/PLACAR.md`. Este
adendo registra o delta.

## O delta desta data

`177/177` → **`178/178`**. Nos dois pacotes que cobram negativos ≥ positivos o delta é `+2`, porque
cada caso novo entrou com o par negativo.

## O achado, e o raio real

`CA-01` e `GR-01`/`GR-02` da remedição de 2026-08-03: os itens de "O que ainda não foi provado"
descrevem a pendência e **não dizem quem responde por fechá-la**. Medido em 2026-08-08, antes de
escrever: **52 itens abertos na casa, UM com dono**. Como nas outras duas formas desta campanha, o
defeito nunca foi dos sete reprovados — era de forma, e estava na casa inteira.

Hoje os **onze** pacotes que têm a seção carregam a tabela `item → dono → fecha quando`, e os três
de topo que não a têm seguem sem exigência: cobrar formulário não é cobrar conteúdo.

## Três falsos negativos do meu próprio instrumento, e o que eles ensinaram

A varredura que produziu o número foi refeita três vezes, e as três correções estão no docstring da
trava:

1. **sensível a caixa** — não achou a seção do `especialista-planejador`, escrita `O que ainda NÃO
   foi provado`. Declarar "não tem seção" teria isentado um pacote com quatro pendências;
2. **só itens numerados** — aquele pacote usa traço, e a conta saiu "4 pacotes" onde eram 5;
3. **ainda só numerados** — `departamento-qa-usabilidade` aparecia com **zero** itens e tinha três,
   também em traço. Foi a própria trava, já escrita, que o acusou.

Detector cego ao formato do vizinho não produz conformidade: produz **isenção**. Por isso o
`_ITEM_DE_PENDENCIA` aceita `1.`, `-` e `*`, e por isso o teto abaixo é declarado.

## Prova de mutação — 5 de 6, e o sexto é o teto

| mutante | veredito | quem pegou |
|---|---|---|
| M1 linha da tabela de donos apagada | PEGOU | a própria trava |
| M2 célula do dono esvaziada | PEGOU | a própria trava |
| M3 trava do dono inerte | PEGOU | **`validate_travas_compartilhadas_com_efeito`** (T84) |
| M4 trava fora de `FUNCOES_OBRIGATORIAS` | PEGOU | **o piso da T84** |
| M5 autoteste do dono desligado | PEGOU | **a T84** |
| M6 pendência em formato desconhecido | **ESCAPA — teto declarado** | ninguém |

**M3, M4 e M5 são o retorno do investimento da tarefa 84.** A trava nova nasceu protegida: quem
tentar desligá-la cai no mecanismo que foi escrito ontem para as travas compartilhadas. Antes da
T84 os três escapariam.

## O TETO, publicado

**M6 escapa por construção.** O detector conhece três formas de item — numerada, traço e asterisco —
porque são as que a casa usa. Pendência escrita em formato novo (tabela, parágrafo solto, outro
marcador) não é contada e não é cobrada. Isso não se fecha alargando a expressão regular: cada
alargamento cria a próxima forma não coberta.

O fechamento honesto é de outra natureza — quem escreve pendência declara o formato, ou a seção
inteira vira estrutura tipada em vez de prosa. Enquanto não for, o limite fica aqui, medido e
nomeado, e a prova de mutação carrega o M6 como caso **esperado**: se um dia ele parar de escapar
sem que esta declaração mude, a prova reclama.

Instrumento: `_compartilhado/prova_mutacao_dono.py`.
