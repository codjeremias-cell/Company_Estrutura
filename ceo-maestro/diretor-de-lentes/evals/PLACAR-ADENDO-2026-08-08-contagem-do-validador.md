# Adendo de contagem — `diretor-de-lentes`, 2026-08-08

> **Por que este arquivo existe.** O [`PLACAR.md`](PLACAR.md) ao lado e os adendos anteriores
> declaram números corretos **nas datas em que foram medidos**, e este adendo **não altera nenhum
> deles**. A receita devolve outro número hoje porque a tarefa 43 acrescentou dois casos.
> Redeclarar ao lado, por adendo datado e **no mesmo ato** que muda a contagem, é o que esta casa
> aprendeu depois que uma canonização somou 47 casos em 15 validadores e redeclarou em 1 — a deriva
> derrubou o `C04` de oito pacotes na rodada seguinte.

## A contagem vigente

| medição | resultado |
|---|---|
| vigente em 2026-08-07 | 101/101 |
| **vigente em 2026-08-08** | **103/103** |

**Receita, literal:**

```
cd "Estrutura Final de Skills/ceo-maestro/diretor-de-lentes"
PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1 python evals/validate_workflow.py
```

## O delta: +2, e os dois são desta frente

| caso acrescentado | o que trava |
|---|---|
| `todo DEPARTMENT_RETURN tem GATE_RECORD, dentro do teto declarado` | a dívida de gate não pode crescer sem que um número mude à vista |
| `a trava do gate sabe ficar vermelha (fixture nos dois sentidos)` | a própria detecção é exercitada com fixture, nos dois sentidos |

### A cadeia inteira

| medição | resultado |
|---|---|
| vigente em 2026-08-07, após as tarefas 40, 41, 51 e 48 | 1990/1991 |
| **vigente em 2026-08-08, após a tarefa 43** | **1992/1993** |

O único `FAIL` continua sendo o mesmo e não é desta frente: `departamento-conteudo-marketing`,
*"fontes legadas intactas e cópias exatas"* — a tarefa 36, diagnosticada em 07/ago como drift real
do Catálogo e ainda pendente de decisão de governança.

## O que a tarefa 43 mediu, e que é o motivo destes dois casos

Varredura de **2.137 envelopes** com `artifact_type` (`.json` e `.ndjson`) na árvore:

- **`DEPARTMENT_GATE_RECORD`: 0 instâncias.** O `SKILL.md:310` deste Diretor diz que retorno
  departamental **só integra** por gate completo. A única porta obrigatória nunca foi aberta.
- **`DEPARTMENT_RETURN`: 38 envelopes, 35 com `department_return_id`, 19 ids distintos.** Dezenove
  retornos integraram sem gate nenhum.
- `MATRIX_EXCHANGE_MESSAGE`: 0 instâncias — e a seção de evidência do Diretor afirma cumprida a
  condição dele.

## A unidade é o retorno distinto, não o arquivo

O primeiro teto que escrevi foi **38**, e era o denominador errado: conta envelopes, e o mesmo
retorno viaja copiado entre campanhas. Duplicação de cópia não é dívida de governança. O teto
vigente é **19**, o número de `department_return_id` distintos sem gate.

É o mesmo defeito que a própria tarefa 43 carregava — ela dizia "90 `EXECUTIVE_MISSION`" e nenhum
método reproduz 90 (medi 68 no topo de `.json`, 80 com aninhados, 69 por nome de arquivo, 49 no
commit de 06/ago). Contagem de instância não é contagem de coisa, e o erro é fácil de repetir
justamente quando se está corrigindo o de outro.

## Por que teto numérico e não lista de nomes

O precedente da casa é a `BYPASS_HISTORICO_2026_08_06` da tarefa 32 — uma lista de nomes sob o
comentário *"é EXCEÇÃO HISTÓRICA DATADA, não permissão: a lista só pode ENCOLHER"*.

Medido em 2026-08-08: **ela nasceu com 7 entradas e hoje tem 13.** Cinco das seis que entraram não
trazem justificativa escrita, e o comentário ainda diz "As 7 rodadas medidas em 2026-08-06" — o
texto normativo e o dado discordam dentro do mesmo bloco. Está aberta como tarefa 53.

Lista de nomes cresce em silêncio porque acrescentar uma linha parece inofensivo no diff. Um **teto
obriga quem cresce a mudar um número**, que é a menor unidade de mudança que um revisor não deixa
passar.

E o teto é `<=`, não `==`: exigir igualdade proibiria a melhora — o `gate-de-maximalidade-proibe-o-futuro`
desta casa. Quando a dívida cair, a trava **manda baixar o teto** em vez de reprovar quem melhorou.
Isso foi exercitado: com o teto em 38 e a dívida real em 19, ela acusou *"teto desatualizado"*.

## Prova de mutação — 4 de 4

| mutação | efeito | caso que avermelhou |
|---|---|---|
| N1 | teto sobe para 99 (dívida nova entraria calada) | 102/103 — o caso do teto |
| N2 | teto desce para 5 (dívida acima do declarado) | 102/103 — o caso do teto |
| N3 | a detecção nunca acha retorno descoberto | 101/103 — o autoteste |
| N4 | a correlação para de reconhecer o gate | 102/103 — o autoteste |

Árvore restaurada ao fim, SHA-256 do arquivo conferido idêntico.

**Duas mutações da primeira passada foram descartadas por erro meu de mira, não por defeito do
código:** uma desligava uma asserção *dentro* do autoteste — enfraquecer um autoteste nunca o
avermelha — e a outra esperava vermelho no caso do teto quando quem devia acusar era o autoteste.
Resultado de mutação é pergunta, não veredito: as duas foram refeitas mirando a função sob teste.

## O que este adendo NÃO afirma

- **Não afirma nota nem veredito.** Nota é exclusiva do `departamento-juizes`.
- **Não afirma que a cadeia passou a ser usada.** A trava impede a dívida de crescer calada; ela
  não abre a porta que nunca foi aberta. Os 19 retornos sem gate continuam lá, agora contados e
  com teto declarado.
- **Limite conhecido:** os **3** envelopes `DEPARTMENT_RETURN` sem `department_return_id` são
  invisíveis a esta trava — sem id não há o que correlacionar. Ficam nomeados aqui em vez de
  escondidos; fechá-los é exigir o campo no schema, que é outra frente.
- **Limite conhecido:** forjar um `DEPARTMENT_GATE_RECORD` com o `department_return` certo é
  trivial e derrubaria o teto sem que nada integrasse de verdade. Esta trava torna o bypass
  **visível e deliberado**, não impossível — é o mesmo teto `OI-04` já nomeado nesta casa.
