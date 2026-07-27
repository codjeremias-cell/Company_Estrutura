# Gate dos Juízes, retrabalho e limitação

## Separação de responsabilidades

- **Departamento produtor:** entrega e evidencia.
- **Auditoria:** prova conformidade com contrato e Regras de Ouro.
- **Juízes:** avalia, pontua e emite o veredito.
- **Diretor:** verifica integridade, encaminha e coordena retrabalho.
- **CEO:** decide validação executiva ou pede exceção.
- **Jeremias:** única autoridade para autorizar exceção abaixo do corte.

## Toda entrega passa pelos Juízes

O legado usava Juízes apenas em disputa entre candidatos. Essa regra foi substituída: todo
`DEPARTMENT_RETURN` materializado e todo candidato integrado seguem ao
`departamento-juizes`.

Para retorno departamental, usar o `DEPARTMENT_JUDGE_REPORT` do contrato dos Juízes
(`departamento-juizes/CONTRATO-DE-COMPROMISSO.md`). Para o candidato integrado que chegará ao
CEO, exigir o `JUDGE_REPORT` definido pelo CEO. O Diretor só integra o retorno depois de
materializar `DEPARTMENT_GATE_RECORD` com missão, retorno, pedido e parecer correlacionados.

O Departamento de Juízes também opera em modo **DISPUTA**, quando o Diretor submete 2 ou mais
candidatos ao mesmo contrato: a saída ali é um `PANEL_HANDOFF` consultivo, e o candidato
recomendado **ainda passa pelo gate de validação** antes de integrar. Recomendação de painel não
é aprovação de gate.

## Conferência de integridade

O Diretor confere:

- identidade, versão e digest dos Juízes;
- contrato, versão e `candidate_digest`;
- avaliações aplicáveis e evidências;
- `minimum_score` igual à menor nota aplicável;
- validade temporal;
- falhas críticas e pendências;
- críticas e mudanças exigidas.

O Diretor recalcula a menor nota para detectar adulteração; não produz nota alternativa.

## Tabela de encaminhamento

| Situação | Encaminhamento do Diretor |
|---|---|
| `minimum_score >= 9.5`, veredito aprovado e gates íntegros | `D_READY_FOR_CEO` |
| nota abaixo de `9.5` com correção viável | `REWORK_ORDER` |
| nota abaixo de `9.5` com alegação vaga | `REWORK_ORDER` ou `D_BLOCKED` |
| limite objetivo completo e endossado por Juízes | enviar pacote de limitação ao CEO |
| falha crítica, RI/RO violada, evidência ou autoria ausente | `D_BLOCKED` |
| Juízes ausentes ou parecer vencido/divergente | `D_BLOCKED` |
| décima rodada sem corte | `D_LIMIT_REACHED_RETURNED` ao CEO |

Não usar média. `9.49` permanece abaixo de `9.5`. Não arredondar.

## `REWORK_ORDER`

Transportar do parecer:

- critério abaixo do corte;
- nota e evidência;
- mudança exigida;
- Departamento responsável;
- critério de reteste;
- rodada global do contrato e rodadas restantes.

Reabrir somente missões afetadas. Integração que muda candidato exige novo julgamento.

## Relatório de limitação

O Diretor pode montar ou endossar `LIMITATION_REPORT` somente quando houver:

1. candidato, contrato, rodada e snapshot exatos;
2. todas as avaliações abaixo do corte;
3. fatores objetivos e provas;
4. tentativas executadas e resultados;
5. alternativas e descarte verificável;
6. melhor nota atingível;
7. razão por mudança exigida ainda não resolvida;
8. riscos, impacto e mitigações;
9. dissensos;
10. escopo e prazo pedidos;
11. endosso do Diretor e dos Juízes.

Prazo ou orçamento só contam se o CEO os recebeu de Jeremias como restrição vinculante.

## Limites não dispensáveis

Não encaminhar exceção como elegível quando houver:

- falha crítica;
- violação de sistema, política, lei, privacidade ou segurança crítica;
- violação de Regra Inquebrável;
- ausência de autoria, independência, evidência ou `DONE`;
- pendência bloqueante fora do piso numérico;
- scorecard, digest ou escopo divergente;
- efeito externo sem autorização própria.

O Diretor envia o pacote ao CEO e para. Nunca produz `EXCEPTION_REQUEST`, conversa
diretamente com Jeremias para obter aceite, consome autorização ou emite
`VALIDATED_BY_EXCEPTION`.

## Rodadas

O contador é global ao contrato, de 1 a 10; não reinicia por Departamento. Não executar
rodada inútil quando limitação objetiva já estiver provada. Na décima rodada sem corte, o
Diretor informa o estado real; somente o CEO registra `LIMIT_REACHED`.

## Critério de conclusão

Cada entrega possui parecer vigente e encaminhamento, sem o Diretor assumir julgamento ou
autoridade executiva.
