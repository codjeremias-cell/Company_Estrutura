# ADR-001 — CEO Maestro na hierarquia executiva

**Status:** aceito para migração — **emendado pelo
[ADR-004](../departamento-evolucao-skills/references/adr-004-evolucao-no-nivel-do-ceo.md) e pelo
[ADR-014](../diretor-de-lentes/departamento-juizes/references/adr-014-dois-niveis-de-veredito.md)**
**Data:** 2026-07-26  
**Decisor:** Jeremias

> **Emenda (ADR-004).** A decisão original permitia **duas** relações diretas.
> O ADR-004 criou o `departamento-evolucao-skills` no nível do CEO, porque ele
> evolui as skills do próprio Diretor e não pode responder a quem ele modifica.
> São **três** pares executivos: `diretor-de-lentes`, `departamento-negocios` e
> `departamento-evolucao-skills`. Onde o texto abaixo diz "duas relações diretas", leia
> **três**.
>
> **Emenda (ADR-014, 2026-07-28).** O corte binário 9,5 abaixo é histórico e foi substituído
> pelas faixas `10 → VALIDATED`, `7–9 → ACEITO_USO_INTERNO`, `0–6 → REPROVED`, com
> `required_level` declarado no envelope. O parecer obrigatório dos Juízes e o CEO sem comando
> direto sobre agentes permanecem vigentes.

## Contexto

O pacote `maestro` antigo continha o Comitê abaixo da própria skill e falava diretamente com
lentes. A nova arquitetura separa direção, departamentos e agentes, inclui Negócios ao lado
do CTO e torna Juízes uma camada transversal de validação.

## Decisão

Migrar `maestro` para `ceo-maestro` como plano de controle executivo. Permitir somente duas
relações diretas: `diretor-de-lentes` e `departamento-negocios`. Exigir parecer do
`departamento-juizes` anexado a toda submissão final.

Reservar `VALIDATED` para menor nota aplicável `>= 9,5`. Abaixo do corte, permitir somente
retrabalho ou `VALIDATED_BY_EXCEPTION` após relatório verificável de limitação e autorização
explícita de Jeremias.

## Consequências

- CEO Maestro não conhece nem comanda agentes diretamente.
- CTO e Negócios ganham contratos próprios e serão migrados separadamente.
- Juízes avalia; Auditoria fornece evidência; CEO decide o fechamento.
- `regras-de-ouro/REGRAS-DE-OURO.md` passa a ser a fonte normativa única da nova estrutura,
  inicialmente materializada como cópia byte a byte da fonte legada.
- O pacote antigo permanece intacto como rollback até a nova estrutura ser validada.
- Capacidade ainda não migrada aparece como lacuna, não como integração presumida.

## Alternativas descartadas

- Renomear apenas o arquivo antigo: manteria fronteiras e referências incompatíveis.
- Copiar o Comitê inteiro para o CEO: duplicaria as futuras skills do CTO.
- Permitir exceção autônoma pelo CEO: retiraria de Jeremias a autoridade sobre risco residual.
