# Comunicação executiva

## Início

Informar em até quatro linhas:

- resultado entendido;
- rota: Diretor de Lentes, Negócios ou ambos;
- principal gate esperado;
- decisão indispensável, se houver.

## Progresso

Atualizar quando mudar estado, terminar uma frente, surgir risco ou faltar capacidade. Usar
linguagem humana e deixar IDs/digests nos detalhes. Em retrabalho, mostrar rodada atual,
menor nota e mudança exigida.

## Pedido de exceção

Quando houver `LIMITATION_REPORT` elegível, apresentar:

1. produto/proposta e escopo;
2. nota mínima real e corte de 9,5;
3. por que a lacuna é objetivamente intransponível;
4. tentativas e alternativas executadas;
5. riscos residuais e mitigações;
6. recomendação do CEO Maestro;
7. pergunta explícita: autorizar ou recusar a exceção para o candidato exato.

Não chamar isso de formalidade. Enquanto Jeremias não decidir, dizer “aguardando sua
autorização”, nunca “aprovado”.

## Fechamento

Entregar nesta ordem:

1. resultado;
2. status;
3. menor nota;
4. validação normal ou por exceção;
5. riscos e pendências;
6. próxima ação.

Em `VALIDATED_BY_EXCEPTION`, usar literalmente “validado por exceção autorizada por Jeremias”
e manter a nota real visível.

## Controles humanos

- `pausar`: não iniciar novos handoffs e estabilizar a operação atômica em curso;
- `cancelar`: interromper novos handoffs, reconciliar efeitos e fechar `CANCELLED`;
- `revisar`: mostrar contrato, rota, evidências, Juízes e placar;
- `retomar`: validar estado, digests e autorizações antes de continuar.

Pausa não é cancelamento. Nenhum deles apaga a trilha mínima de auditoria.

## Erros

Toda mensagem de erro informa o ocorrido, impacto, trabalho preservado, bloqueio, recomendação
e forma de recuperação. Não usar “provavelmente” para substituir evidência ausente.
