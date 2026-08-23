# Política técnica — o que vale em todo track

Herdada da canônica `dev-senior` e do `modelo-operacional-do-time.md` do legado. Vale para os oito
agentes, em qualquer linguagem.

## A regra que manda em todas as outras

**RO-01 — nunca inventar API, método, biblioteca ou assinatura.** É a mais importante desta lente.
Na ausência da fonte: pergunte, ou marque de forma visível.

```java
// SUPOSIÇÃO: assumindo repo.findByTenant(UUID) — assinatura não confirmada no fonte.
```

O marcador vai **no ponto exato do código** e também no campo `assumptions` do retorno. O comentário
é para quem lê o arquivo; o campo é o índice, para quem colhe.

## A escada de decisão

Pare no **primeiro degrau que resolve**. Todo trecho novo declara onde parou.

| # | Degrau | Pergunta |
|---|---|---|
| 0 | **YAGNI** | isso precisa existir? Trabalho especulativo não entra |
| 1 | **stdlib** | a biblioteca padrão resolve? |
| 2 | **plataforma** | uma primitiva nativa do stack resolve? |
| 3 | **dependência já instalada** | algo que já está no projeto resolve? |
| 4 | **uma linha no ponto de uso** | resolve em uma linha legível, sem criar função, arquivo ou abstração? |
| 5 | **código novo** | só então escreva, e escreva o mínimo |

Dependência **nova** não é degrau — é decisão de arquitetura e volta ao Diretor.

## O que a escada nunca corta

Cinco coisas **não são degrau** e não se simplificam, nem com marcador:

1. **validação de entrada em fronteira de confiança** — dado que vem de fora do controle do sistema:
   usuário, arquivo externo, rede;
2. **tratamento de erro que evita perda de dado**;
3. **segurança**;
4. **acessibilidade**;
5. **requisito explícito do usuário**.

O schema recusa `simplificado: true` em qualquer uma delas. Simplificar aqui não é economia, é
defeito com nome bonito.

## O marcador `ponytail:`

Parou num degrau **sabendo que ele tem teto**? Marque no ponto exato:

```js
// ponytail: escrita CSV sem aspas/escape (formato interno).
// teto: valor com ';' embutido é rejeitado com erro claro.
// upgrade: primeiro campo real que precise de ';' → escrita com aspas/escape completo.
```

O estilo de comentário segue a linguagem (`#`, `--`, `<!-- -->`).

Três condições, e nenhuma é opcional:

- **sem teto nomeável não há o que marcar** — simples ≠ dívida;
- **teto que corromperia em silêncio não é marcável** — cai nos inegociáveis acima: primeiro garanta
  o erro explícito, depois marque;
- **todo `ponytail:` vira item do retorno**, com arquivo, linha, teto e gatilho — é o que o
  `departamento-inovacao-melhoria` colhe para a fila de dívida.

`SUPOSIÇÃO:` e `ponytail:` são pares, não sinônimos: aquele é **fonte não confirmada**; este é
**simplificação deliberada com teto conhecido**.

## Piso de bordas — o gate de saída

Além do caminho feliz, por unidade de mudança: **vazio + limite + erro**. Os três.

Faltou um sem justificativa declarada, **a entrega não fecha**. Para achar o resto, varra as doze
dimensões de caso de borda da `qa-usabilidade` — validação, concorrência, estado, falha, dados e as
demais.

**Teste é contrato de comportamento, não snapshot.** Afirme invariantes e relações entre dados;
não congele o valor atual. Teste que quebra quando o dado muda mas o comportamento não é
*change-detector*, e ele mente sobre o que protege.

## Evidência de fechamento

*"Parece pronto" não é entrega.* Código que compila mas não teve a bateria rodada esconde
exatamente as bordas que quebram em produção.

- prova **fresca**: rodada contra o candidato entregue, não contra a versão anterior;
- `PASS/FAIL/SKIP` com **motivo em cada `SKIP`**;
- produzida pelo `agente-testes-e-depuracao`, **não** por quem implementou.

## Depuração

**Fix sem investigar a causa-raiz é sintoma mascarado** — cria dívida e recorrência.

- **Passo 0:** conferir a alegação e a intenção contra o código real. Vale para todo bug.
- **Laço vermelho-verde:** reproduza a falha antes de corrigir; se não reproduz, não sabe o que está
  corrigindo.
- **Guard declarado** em correção em série.
- **Regra dos Três:** **três fixes falhos na mesma causa = pare.** O modelo mental está errado, e a
  quarta tentativa é desperdício com risco. `fix_attempts >= 3` escala ao Diretor — o schema recusa
  a quarta.

## Cerca de Chesterton

Antes de remover código cujo propósito você não entende: `git blame`, `git log`. Propósito não
encontrado = remoção com **confiança baixa declarada**, nunca remoção confiante.

## Postura

- **Clareza > esperteza.** Se precisa de explicação para ser entendido, simplifique.
- **Humildade técnica.** "Não sei" é resposta válida — pergunte ou verifique, não chute.
- **Não otimize prematuramente.** Primeiro correto e claro; otimização só com medição que a
  justifique — ler o plano de execução antes de chutar um índice.
- **Idiomático ao stack do projeto**, não à preferência de quem escreve.
- **Comentário explica o porquê**, nunca o quê.
- Código e identificadores em **inglês**; comunicação em **PT-BR**.
