# Rubrica `rubrica-corte-v1` e o corte de 9,5

Escala única de todo `score` de `JUDGE_OPINION` e de toda linha do `scorecard`. A gerente resolve
a rubrica **antes** de emitir a primeira `JUDGE_ASSIGNMENT` e copia esta tabela literal em cada
atribuição da rodada — agente nunca busca rubrica sozinho e nunca inventa escala.

## Bandas

A nota mede o candidato **contra o critério declarado e observado**, nunca contra um ideal
abstrato e nunca contra o que outro Departamento entregou em outra rodada.

| Banda | Nota | O que significa naquele critério | Efeito no gate |
|---|---:|---|---|
| **quebrado** | 0–3 | não atende, ou atende com defeito que impede o uso; a evidência contradiz o candidato | reprova o critério; costuma vir com `critical_findings` |
| **cru** | 4–6 | atende em parte, com lacuna observável e nomeável (caso não coberto, estado ausente, prova faltando) | reprova o critério |
| **polido** | 7–8 | atende o critério inteiro, sem defeito observado; sobra risco menor ou acabamento | **reprova o gate**: cumprir o combinado não é o corte desta casa |
| **excelente** | 9–10 | atende e supera: cobre borda, traz prova executada e resolve o critério sem deixar risco nomeável | única banda que atravessa o corte |

**9 e 10 não são a mesma coisa.** `9` é excelente com um risco menor nomeado; `10` é excelente sem
risco nomeável naquele critério. Quem dá `10` declara, na razão, que procurou o risco e não achou —
`10` por ausência de análise é parecer fora do contrato.

## O corte

- **`minimum_score >= 9.5`** — a **menor** nota do `scorecard` aplicável, nunca a média.
- Como toda nota é **inteira**, o corte na prática exige **10 em todos os critérios aplicáveis**:
  `9` em um único critério fixa `minimum_score: 9` e reprova. Isso é deliberado — o `9,5` do
  organograma é um piso entre notas inteiras, e a fração só aparece quando o Diretor recebe
  scorecards de rodadas distintas. Rebaixar a exigência arredondando `9` para "quase 9,5" é
  violação de contrato, não flexibilidade.
- **Proibido:** média, mediana, ponderação por `confidence`, arredondamento, compensação entre
  critérios e "nota de conjunto". `9,49` permanece abaixo de `9,5`.
- Critério com `score: "n/a:<motivo>"` verificável **não entra** no mínimo e fica registrado no
  `scorecard`; `n/a` sem motivo verificável é parecer fora do contrato.
- Critério **sem nota** (ótica ausente, critério sem dona, razão única descartada) não vira nota
  estimada: proíbe `VALIDATED` e abre lacuna — protocolo, §3, regra 5, e §4, regra 2.

## Fração e escala

Todo `score` é **inteiro** de 0 a 10. `9,5` ou `8,5` em um parecer é veredito fora do contrato e
volta pelo reenvio único (protocolo, §3, regra 6) — assim toda nota cai numa banda nomeada e o
`scorecard` permanece legível. O `minimum_score` do relatório é o mínimo dessas notas inteiras; ele
só assume valor fracionário quando o Diretor consolida scorecards de rodadas ou frentes distintas,
o que é operação dele, não do Departamento.

## Uso e registro

- Uma só rubrica por rodada. Duas em uso é pedido inválido.
- O relatório declara a rubrica efetivamente usada; sem esse registro a nota não é recalculável e
  o relatório está incompleto.
- Banda diferente entre dois critérios não se compensa: a menor manda.

**Concluído quando:** toda nota da rodada é inteira, cai numa banda nomeada, tem razão e
`evidence_ref` que resolvem, e o `minimum_score` declarado é o mínimo verificável do `scorecard`.
