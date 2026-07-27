# Fronteiras — onde Dados começa e onde termina

Este Departamento tem quatro vizinhos com sobreposição real. A fronteira não é preferência de
estilo: é o que impede duas frentes de decidirem a mesma coisa em direções opostas.

## A navalha

> **Como o dado é modelado, evoluído e contratado é daqui.**
> **Quem é dono do dado e como as partes o trocam é do `departamento-arquitetura-software`.**
> **Como qualquer coisa é implementada é do `departamento-desenvolvimento`.**
> **Como o dado é protegido contra um adversário é do `departamento-seguranca`.**

A primeira metade é o recíproco exato do que o
[ADR-006](../../departamento-arquitetura-software/references/adr-006-arquitetura-sem-julgamento-e-com-seis-agentes.md)
fixou do outro lado. As duas fronteiras foram escritas para encaixar; se divergirem, o Diretor
decide e o ADR mais novo registra.

## Tabela de desempate

| A pergunta é… | Dono | Por quê |
|---|---|---|
| "que perguntas esse dado responde e em que volume?" | **Dados** | é o piso da modelagem |
| "qual banco, e por qual evidência?" | **Dados** | escolha de motor é decisão de dado |
| "o que uma linha dessa tabela representa?" (o grão) | **Dados** | é a definição do modelo |
| "como esse schema evolui sem downtime?" | **Dados** | expand/contract é desenho de dado |
| "esse índice se justifica por qual padrão de acesso?" | **Dados** | leitura dimensionada é do modelo |
| "que campos são PII e quanto tempo retemos?" | **Dados** | classificação e retenção são do dado |
| "qual serviço é dono dessa tabela?" | **Arquitetura** | ownership é limite de módulo |
| "esse módulo lê do outro por API ou por evento?" | **Arquitetura** | é contrato de integração |
| "síncrono ou assíncrono, e qual o modo de falha?" | **Arquitetura** | é topologia |
| "como escrevo esse repositório/DAO?" | **Desenvolvimento** | é implementação |
| "por que *esta* query está lenta em produção?" | **Desenvolvimento** | é tuning pontual |
| "como escrevo a migração no Flyway?" | **Desenvolvimento** | executar a migração é implementar |
| "esse campo pode vazar por enumeração?" | **Segurança** | é modelagem de ameaça |
| "como cifro em repouso e quem tem a chave?" | **Segurança** | é controle, não modelo |

A distinção mais fina da tabela é a linha do índice contra a linha da query. **Ler um plano de
execução para provar que o padrão de acesso justifica um índice é daqui.** Pegar uma query lenta e
reescrevê-la é do Desenvolvimento. O sinal é o objeto: se a saída é *estrutura persistente*, é
Dados; se a saída é *um trecho de código*, não é.

## Regra A — restrição arquitetural é vinculante

Quando a Arquitetura delega para cá, a dependência chega com `architectural_constraint`
preenchida — tipicamente ownership de dado ou modo de integração já fixado. Este Departamento
**modela dentro dela**.

- Se o ownership diz que só o serviço dono lê a base, nenhum modelo daqui propõe leitura direta de
  outro serviço — propõe réplica, projeção ou contrato de leitura.
- Se a restrição **inviabiliza** um modelo defensável, isso não se contorna e não se ignora:
  **escala ao Diretor** como conflito entre dois Departamentos. O Diretor roteia; a Arquitetura
  revisa a restrição ou o modelo cede.

Contornar em silêncio é o modo de falha que os dois ADRs foram escritos para impedir — dos dois
lados.

## Regra B — dependência sai, nunca vira execução

Precisou de código, teste, endurecimento de segurança ou decisão de topologia? Sai como
`delegated_dependency` endereçada ao Departamento dono, **com o que já está decidido aqui**
anexado: grão, chaves, plano de migração, índice justificado. Dependência sem esse anexo devolve
para o vizinho um problema em branco.

## O que este Departamento nunca entrega

- código de DAO, repositório, ORM, query ou arquivo de migração pronto;
- diagrama C4, decisão de módulo, escolha entre síncrono e assíncrono;
- nota, veredito ou ranking — pontuar é do `departamento-juizes`;
- resultado de teste executado: `pass` e `fail` do `test_summary` daqui são `0` por `const`.

## Zona cinzenta declarada

**Contrato de dados** aparece nos dois lados e a divisão é esta: o **significado, schema, qualidade
e linhagem** do dado trafegado são daqui; o **canal, protocolo, garantia de entrega e modo de
falha** são da Arquitetura. Um contrato completo tem as duas metades e nasce das duas frentes.

**CDC e outbox** são daqui quando a pergunta é *"como o dado chega íntegro do lado de lá sem
dual-write"*; são da Arquitetura quando a pergunta é *"quem publica e quem consome"*.
