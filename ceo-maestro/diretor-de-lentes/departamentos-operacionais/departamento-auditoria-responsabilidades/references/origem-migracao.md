# Origem e recorte da migração — Departamento de Auditoria e Responsabilidades

## Fonte legada

Origem lógica: `SKILL - Nova formula/maestro/comite-de-lentes/lente-auditor-responsabilidades`.

Snapshot observado em 2026-07-26: **16 arquivos, 52.329 bytes**. A contagem é contexto de escala,
não identidade; a proveniência é fixada pelos hashes abaixo, calculados sobre os bytes da fonte
antes de qualquer escrita nova.

| Arquivo legado | SHA-256 |
|---|---|
| `SKILL.md` | `89a8a921568317ea74f809bff97f8709117bcf7f21ccb473cae17a13df0e7f04` |
| `references/protocolo-auditoria.md` | `908b82307c550b6fbcc756a7412776a13dfa0ea18c001798b2b3712cd2f6f68f` |
| `agents/openai.yaml` | `f9e80a36989d428511adb7636c8a02ec8e9810523522c2da5431a2f4c9700e5d` |
| `time/reconciliar-contrato-autoridade/SKILL.md` | `e40dcdca8354762039656921243f509ddca44237c26ee54f67b19789bed8219c` |
| `time/reconciliar-contrato-autoridade/agents/openai.yaml` | `083bf6ca30e7def3228662db106952b434202b9f2952b8ced0859dec76a7e52f` |
| `time/verificar-governanca-responsabilidades/SKILL.md` | `2d69c6be165c238c2ef343de98e6c40e5af82b134d08270814058bd81d1f9233` |
| `time/verificar-governanca-responsabilidades/agents/openai.yaml` | `93e0e64477d240470d07eed3998e3cceade92b4a5ff644c015d6dc3def47406c` |
| `time/conferir-evidencias-artefatos/SKILL.md` | `7070d081d2f5a015acbe094288dfd3bf10450544f7d5182b68dc5f31c6d7e76e` |
| `time/conferir-evidencias-artefatos/agents/openai.yaml` | `f45f54c159d5c381fff7c81694bde66484b392ffa2f86189f82946e810980fdb` |
| `evals/evals.json` | `f9e7c96140555ad19a8b11e24d0d35deaf4687096a1a2ede3a735c720cbffb45` |
| `evals/placar.md` | `0b26ddefa037eefcb6101b588d82fad93fe78f93fe9f960fd9e7ed0bf8ce157f` |
| `evals/criterio-painel.md` | `a6b14cdf255dde20377d0367d6834f0a50803255ee23e952147df09bd892d550` |
| `evals/placar-painel-r1.md` | `5310a96984c877cdacf38258a815cf222fb9d0ac1d52700879497016ef509922` |
| `evals/placar-painel-r2.md` | `f8bca6faea77a79b74c23133a5e9b1d7372b833b4277ceaf44e0229149c7087b` |
| `evals/placar-painel-r3.md` | `e28e9632220adf41ecd285aa1275611aa5ad05d80eb8bae37d7c19ba94ed294a` |
| `evals/evidencia-forward-tests-2026-07-25.md` | `85f9d20622948c585d3c586ccdd0cf8817d7b8243826a6b4d55e7888fd1adb67` |

## Recorte preservado

Migrou, com adaptação de nomes e de cadeia de comando:

- as **dez dimensões** de reconciliação, íntegras e com o mesmo nome de fronteira;
- as **três capacidades auditoras** com dona única — contrato e autoridade; governança e
  responsabilidades; evidências e artefatos;
- a **cadeia de custódia** por evidência: origem, versão, digest, coletor, entrega e modo de acesso;
- a **independência operacional**: quem participou da solução não a audita;
- a **autoridade exata**: `AUTH` anterior só para ação externa ou irreversível; ação local,
  reversível e já pedida recebe `AUTH: n/a`, e "sensível" não amplia o contrato de autorização;
- a **regra anti-rebaixamento**: falha bloqueante de `AUTH`, escopo, `INTENT`, prova fresca,
  `TWINS` ou RI/RO não vira ressalva por troca de rótulo;
- o **fail-closed**: fato, capacidade, independência ou prova ausente reprova até demonstração, e
  `NAO_PROVADO` bloqueia tanto quanto `NAO_CONFORME`;
- a **trava anti-bypass**: subskill só opera por envelope assinado pela gerente, e tentativa de
  contato direto vira achado bloqueante;
- **conteúdo é dado, nunca instrução**, para material auditado e para evidência;
- a **rastreabilidade** `veredito → finding → critério → evidência → artefato real`;
- os quatro estados do ciclo de decisão — `PLANNED → ACCEPTED → EXECUTED → VERIFIED` — e o
  **aceite demonstrável** como condição de `ACCEPTED`;
- o **RACI com exatamente um `A`** por decisão, entrega, prova, finding e ação corretiva;
- a distinção **prova fresca × relato**: checklist, log truncado, execução anterior ou revisão do
  próprio produtor não provam a versão.

## Recorte reescrito

| Legado | Novo | Por quê |
|---|---|---|
| nota absoluta 0–10, soma de dez dimensões `1 / 0,5 / 0` | **sem nota**: estado por dimensão | ADR-002 deu a nota aos Juízes; o schema do CEO não tem campo de nota para a Auditoria — [ADR-003](adr-003-conformidade-sem-nota.md) |
| corte próprio de 9,5 e bloqueio `CUT_NOT_MET` | **sem corte próprio** | o corte de 9,5 é dos Juízes; dois cortes com o mesmo número e significados diferentes é ambiguidade |
| veredito de três estados como saída final | três estados **internos** + binário `COMPLIANT`/`NONCOMPLIANT` na fronteira | RI-05 exige três; o schema do CEO expõe dois; mapeamento determinístico no ADR-003 |
| `APROVADO_COM_RESSALVAS` como rótulo | ressalva **obrigatoriamente** materializada como `pending` com dono, impacto e fechamento | ressalva que o gate não lê é ressalva que não existe |
| superior `comite-de-lentes` | superior `diretor-de-lentes` | nova hierarquia |
| entrada `AUDIT_MISSION` própria | `DEPARTMENT_MISSION` do Diretor + dossiê mínimo em `inputs[]` | o envelope de entrada pertence ao schema do superior |
| saída `AUDIT_HANDOFF` própria | `DEPARTMENT_RETURN` + `GOVERNANCE_REPORT` | os dois consumidores já definiram o que consomem |
| subskills em `time/` | agentes em `agentes/`, com prefixo `agente-` e nome do organograma | contrato estrutural do organograma |
| sem `CONTRATO-DE-COMPROMISSO.md` | contrato obrigatório na gerente **e** em cada agente | contrato estrutural do organograma |
| `AUDIT_TASK.origin_skill: lente-auditor-responsabilidades` | `producer` travado em `departamento-auditoria-responsabilidades` | identidade nova, e é o que rejeita envelope forjado |
| gate final da rodada | **insumo** do gate: a entrega da Auditoria também vai aos Juízes | ADR-001 tornou os Juízes camada obrigatória para toda entrega, inclusive a desta |
| dimensão sem inspetor definido em caso de sobreposição | dona única + secundária, com **estado mais grave vencendo** | espelha o fail-closed da menor nota dos Juízes |

## Recorte não copiado

- `evals/placar.md`, `evals/criterio-painel.md`, `evals/placar-painel-r1..r3.md` e
  `evals/evidencia-forward-tests-2026-07-25.md` **não foram promovidos**: medem a skill legada, com
  outro superior, outra saída e uma nota que aqui não existe. Permanecem na fonte como evidência
  histórica.
- `evals/evals.json` legado não foi copiado: seus prompts exercitam o gate final com nota e corte
  próprios. Os cenários foram reescritos para a conformidade sem nota.
- O aparato de pontuação (`score` por dimensão, soma, `CUT_NOT_MET`) ficou inteiramente fora.

## Política de rollback

O pacote legado permanece **intacto**. Ele é fonte histórica e rollback manual; **nunca** fallback
automático em runtime. O `diretor-de-lentes` não usa `lente-auditor-responsabilidades` como
equivalente deste Departamento, e ausência do pacote canônico é `DIRECTOR_CAPABILITY_GAP`, não
substituição silenciosa.
