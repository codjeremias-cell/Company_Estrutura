# `_compartilhado/` — ferramentas dos validadores

Fonte única do que era copiado dentro de cada `evals/validate_workflow.py`. Só biblioteca padrão
do Python: nenhuma dependência nova, nenhum acesso à rede.

| Arquivo | O que é |
|---|---|
| [validador_schema.py](validador_schema.py) | Motor de validação de JSON Schema (subconjunto draft 2020-12) + `find_const` e `collect_property_names` |
| [verificacoes_pacote.py](verificacoes_pacote.py) | Verificações estruturais: frontmatter, `openai.yaml`, arquivos obrigatórios, pasta de agentes, links internos e **unicidade da série global de ADR** |
| [teste_validador_schema.py](teste_validador_schema.py) | Teste do motor — **rodar antes dos validadores sempre que o motor mudar** |

## Como usar num validador de pacote

O import vem **depois** da definição de `STRUCTURE_ROOT`, porque depende dela:

```python
sys.path.insert(0, str(STRUCTURE_ROOT))
try:
    from _compartilhado.validador_schema import (  # noqa: E402
        digest,
        find_const,
        json_pointer,
        sha256_file,
        validate_schema,
    )
    from _compartilhado.verificacoes_pacote import (  # noqa: E402
        validate_agents_folder,
        validate_frontmatter,
        validate_links,
        validate_openai_yaml,
        validate_required_files,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[FAIL] motor compartilhado ausente em "
        f"{STRUCTURE_ROOT}/_compartilhado: {exc}"
    )
    raise SystemExit(1)
```

A guarda existe para que motor ausente falhe **legível**, com `exit 1`, em vez de despejar um
traceback. Todo validador lista `_compartilhado/validador_schema.py` entre os vínculos externos
obrigatórios, então a ausência aparece também como caso reprovado.

Um Departamento que valida links deve **excluir subárvores que são pacotes próprios**, para que um
filho quebrado não reprove o superior:

```python
validate_links(PACKAGE_ROOT, exclude=[PACKAGE_ROOT / "departamento-juizes"])
```

## A trava da série global de ADR

`validate_adr_series(STRUCTURE_ROOT)` é a única verificação daqui que **não** recebe o pacote e sim a
estrutura inteira, de propósito. A série `adr-<NNN>` é global (passo 4 da
[`GUIA-DE-EXPANSAO-E-MIGRACAO.md`](../GUIA-DE-EXPANSAO-E-MIGRACAO.md)): o arquivo mora na pasta do
dono da decisão, mas o número pertence à estrutura. O aviso em prosa do guia já falhou uma vez — duas
frentes paralelas cunharam `adr-005` (Registros e QA) — então **todo** validador chama esta função,
mesmo o de um pacote que não tem ADR nenhum. É isso que faz a trava valer entre frentes: quem rodar
qualquer validador pega a colisão do vizinho, inclusive de um pacote que ainda não tem validador
próprio.

```python
cases.append(("série global de ADR é única em toda a estrutura", True,
              validate_adr_series(STRUCTURE_ROOT)))
```

A isenção dos três `ADR-001` históricos é por **caminho exato** (`ADR_HISTORICAL_EXCEPTIONS`), não por
número: um quarto `adr-001` em qualquer outro lugar reprova o grupo inteiro, como o guia manda
("não autorizam reuso").

## Regra de manutenção

Um erro aqui afeta **todos** os pacotes ao mesmo tempo, e cada validador continuaria dizendo
"passou". Por isso, ao mexer em `validador_schema.py` ou em `verificacoes_pacote.py`:

```bash
python _compartilhado/teste_validador_schema.py
```

e depois **todos** os validadores de pacote, conferindo que as contagens não mudaram. Contagem que
muda sem mudança de contrato é regressão, não melhoria.

## Limites declarados do motor

O motor implementa um **subconjunto** do draft 2020-12. Palavra-chave não suportada é **ignorada em
silêncio** — o schema não é rejeitado, a restrição simplesmente não vale. Hoje ficam de fora:
`anyOf`, `exclusiveMinimum`, `multipleOf`, `patternProperties`, `propertyNames`,
`dependentSchemas`, `prefixItems`, `$ref` remoto e `format` diferente de `date-time`.

Três dessas lacunas têm caso no teste, marcado com `LIMITE:`, justamente para que a ausência seja
visível e intencional. **Antes de usar qualquer uma delas num schema novo, implemente-a aqui** —
senão a regra entra no schema e não vale nada.

## Por que o validador do CEO é diferente

`ceo-maestro/evals/validate_workflow.py` **não** usa o motor genérico: ele é um validador
artesanal, com asserções específicas por artefato (`add_if`, `required_list`, `valid_digest`,
`resolve_local_ref`). Isso não é duplicação do motor — é outro desenho, anterior, que cobre
invariantes executivos que um validador genérico não expressaria bem.

Dele foram compartilhados apenas `digest` e `sha256_file`. Reescrevê-lo para usar o motor genérico
não está descartado, mas exigiria refazer 32 casos que hoje passam, e o ganho seria estético.
