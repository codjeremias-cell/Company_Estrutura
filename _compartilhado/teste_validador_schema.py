"""Teste do motor compartilhado de schema.

O motor é usado por todos os validadores de pacote: um erro aqui passa
despercebido em cada um deles ao mesmo tempo. Rodar sempre que este módulo mudar,
**antes** dos validadores dos pacotes.

Uso: python _compartilhado/teste_validador_schema.py
"""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _compartilhado.validador_schema import (  # noqa: E402
    collect_property_names,
    digest,
    find_const,
    is_type,
    json_pointer,
    validate_schema,
)
from _compartilhado.verificacoes_pacote import digest_de_arvore  # noqa: E402
from _compartilhado.verificacoes_estrutura import validate_adr_series  # noqa: E402


def check(schema: dict, value: object, *, valid: bool, name: str) -> tuple[str, bool]:
    errors = validate_schema(value, schema, schema)
    return name, (not errors) == valid


def build_tree(root: Path, relative_paths: list[str]) -> None:
    """Materializa uma estrutura sintética só com os `adr-*.md` pedidos."""
    for relative in relative_paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# ADR sintético\n", encoding="utf-8")


def digest_de_arvore_results() -> list[tuple[str, bool]]:
    """A receita de identidade de árvore, travada contra as armadilhas conhecidas.

    Cada caso aqui existe porque a armadilha correspondente já custou uma rodada:
    o digest irreprodutível de 2026-07-26 em `departamento-registros`, e o
    `candidate_tree_sha256` ad-hoc que barrou o primeiro julgamento em 2026-07-27.
    """
    resultados: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        (raiz / "b").mkdir()
        (raiz / "a.md").write_bytes(b"alfa\n")
        (raiz / "b" / "c.md").write_bytes(b"beta\n")

        d1 = digest_de_arvore(raiz)
        resultados.append(("digest de árvore: determinístico entre chamadas",
                           d1 == digest_de_arvore(raiz)))

        # Reprodução por implementação independente: o manifesto declarado na
        # docstring, montado à mão, tem de dar o mesmo número.
        manifesto = "".join(
            f"{hashlib.sha256(conteudo).hexdigest()}  {chave}\n"
            for chave, conteudo in sorted(
                [("a.md", b"alfa\n"), ("b/c.md", b"beta\n")]
            )
        )
        esperado = hashlib.sha256(manifesto.encode("utf-8")).hexdigest()
        resultados.append(("digest de árvore: reproduz a receita da docstring",
                           d1 == esperado))

        # O conteúdo entra em bytes crus: mudar o fim de linha MUDA o digest.
        (raiz / "a.md").write_bytes(b"alfa\r\n")
        resultados.append(("digest de árvore: CRLF muda o número (deliberado)",
                           digest_de_arvore(raiz) != d1))
        (raiz / "a.md").write_bytes(b"alfa\n")

        # `__pycache__` não entra, senão o número muda ao rodar um validador.
        cache = raiz / "b" / "__pycache__"
        cache.mkdir()
        (cache / "x.pyc").write_bytes(b"lixo")
        resultados.append(("digest de árvore: __pycache__ é ignorado",
                           digest_de_arvore(raiz) == d1))

        # A chave é o caminho POSIX: a mesma árvore em qualquer SO dá o mesmo
        # número, e a ordem é a da chave, não a da linha formatada.
        resultados.append(("digest de árvore: raiz ausente falha fechado",
                           _falha_fechado(raiz / "nao-existe")))
    return resultados


def _falha_fechado(caminho: Path) -> bool:
    try:
        digest_de_arvore(caminho)
    except NotADirectoryError:
        return True
    except Exception:
        return False
    return False


def adr_series_results() -> list[tuple[str, bool]]:
    """Casos da trava de unicidade da série global de ADR.

    Sintéticos, em pasta temporária: a função varre a estrutura inteira, então
    testá-la contra a árvore real provaria só o estado de hoje — não a detecção.
    """
    results: list[tuple[str, bool]] = []
    historicos = [
        "ceo-maestro/references/adr-001-hierarquia-executiva.md",
        "ceo-maestro/diretor-de-lentes/references/adr-001-diretoria-e-camada-de-juizes.md",
        "ceo-maestro/departamento-negocios/references/adr-001-rota-vigente-aos-juizes.md",
    ]
    colisao_a = "ceo-maestro/dep-registros/references/adr-005-quatro-agentes.md"
    colisao_b = "ceo-maestro/dep-qa/references/adr-005-qa-executa-sem-julgar.md"

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)

        # 1. série sem duplicata: nada a reprovar.
        limpa = root / "limpa"
        build_tree(
            limpa,
            [
                "ceo-maestro/dep-registros/references/adr-005-quatro-agentes.md",
                "ceo-maestro/dep-qa/references/adr-011-qa-executa-sem-julgar.md",
                "ceo-maestro/dep-seguranca/references/adr-010-seguranca-por-funcao.md",
            ],
        )
        results.append(("série de ADR sem duplicata é aprovada", not validate_adr_series(limpa)))

        # 2. colisão sintética: reprova E aponta OS DOIS caminhos.
        colidida = root / "colidida"
        build_tree(colidida, [colisao_a, colisao_b])
        errors = validate_adr_series(colidida)
        detectou = len(errors) == 1 and "005" in errors[0]
        aponta_os_dois = detectou and colisao_a in errors[0] and colisao_b in errors[0]
        print(f"       colisão sintética detectada: {errors}")
        results.append(("colisão sintética de adr-005 é detectada", detectou))
        results.append(("erro de colisão aponta os dois caminhos", aponta_os_dois))

        # 2b. cópia de laboratório dentro de `evals/` NÃO cunha número (2026-08-19).
        # As campanhas guardam `references/` inteiros do pacote julgado; sem esta
        # exclusão o original colide com a própria evidência, e a casa era reprovada
        # por ter registro do passado — 16 dos 41 FAIL da cadeia vinham daqui.
        com_copia = root / "com_copia_de_campanha"
        build_tree(
            com_copia,
            [
                "ceo-maestro/dep-arq/references/adr-006-decisao.md",
                "ceo-maestro/evals/campanha-x/custodia/cand/references/adr-006-decisao.md",
                "ceo-maestro/evals/campanha-x/isolamento/ASSIGN-1/root/candidato/references/adr-006-decisao.md",
            ],
        )
        results.append(
            ("cópia de adr dentro de evals/ não conta como duplicata",
             not validate_adr_series(com_copia))
        )

        # 2c. e a trava CONTINUA pegando colisão real — o par da regra acima. Sem
        # este caso, afrouxar a exclusão para "tudo" passaria despercebido.
        real_fora = root / "colisao_real_fora_de_evals"
        build_tree(
            real_fora,
            [
                "ceo-maestro/dep-arq/references/adr-006-decisao.md",
                "ceo-maestro/evals/campanha-x/custodia/cand/references/adr-006-decisao.md",
                "ceo-maestro/dep-outro/references/adr-006-decisao-diferente.md",
            ],
        )
        erros_reais = validate_adr_series(real_fora)
        results.append(
            ("colisão real fora de evals/ continua reprovando",
             len(erros_reais) == 1 and "006" in erros_reais[0]
             and "evals" not in erros_reais[0])
        )

        # 3. os três ADR-001 históricos do guia passam nos caminhos declarados.
        historica = root / "historica"
        build_tree(historica, historicos)
        results.append(
            ("os três ADR-001 históricos não reprovam", not validate_adr_series(historica))
        )

        # 4. a isenção é por caminho: um quarto adr-001 novo reprova o grupo.
        reuso = root / "reuso"
        novo = "ceo-maestro/dep-novo/references/adr-001-decisao-nova.md"
        build_tree(reuso, [*historicos, novo])
        errors = validate_adr_series(reuso)
        results.append(
            (
                "ADR-001 histórico não autoriza reuso do número",
                len(errors) == 1 and novo in errors[0],
            )
        )

        # 5. só o nome canônico `adr-<NNN>-<slug>.md` entra na série.
        ruido = root / "ruido"
        build_tree(
            ruido,
            [
                "ceo-maestro/dep-a/references/adr-005-decisao.md",
                "ceo-maestro/dep-b/references/adrs-e-decisoes.md",
                "ceo-maestro/dep-c/references/adr-modelo.md",
            ],
        )
        results.append(("arquivo fora do padrão adr-NNN- é ignorado", not validate_adr_series(ruido)))

    return results


def run() -> int:
    results: list[tuple[str, bool]] = []

    # --- tipos --------------------------------------------------------------
    results.append(check({"type": "integer"}, 9, valid=True, name="integer aceita inteiro"))
    results.append(check({"type": "integer"}, 9.5, valid=False, name="integer rejeita fração"))
    results.append(check({"type": "integer"}, True, valid=False, name="integer rejeita booleano"))
    results.append(check({"type": "number"}, 9.5, valid=True, name="number aceita fração"))
    results.append(check({"type": "number"}, True, valid=False, name="number rejeita booleano"))
    results.append(check({"type": "null"}, None, valid=True, name="null aceita None"))
    results.append(check({"type": "string"}, 3, valid=False, name="string rejeita número"))

    # --- const, enum --------------------------------------------------------
    results.append(check({"const": "a"}, "a", valid=True, name="const aceita igual"))
    results.append(check({"const": "a"}, "b", valid=False, name="const rejeita diferente"))
    results.append(check({"enum": ["a", "b"]}, "b", valid=True, name="enum aceita membro"))
    results.append(check({"enum": ["a", "b"]}, "c", valid=False, name="enum rejeita externo"))

    # --- strings ------------------------------------------------------------
    results.append(check({"minLength": 3}, "ab", valid=False, name="minLength rejeita curta"))
    results.append(check({"maxLength": 2}, "abc", valid=False, name="maxLength rejeita longa"))
    results.append(
        check({"pattern": "^sha256:[a-f0-9]{64}$"}, digest("a"), valid=True,
              name="pattern aceita digest válido")
    )
    results.append(
        check({"pattern": "^sha256:[a-f0-9]{64}$"}, "sha256:XYZ", valid=False,
              name="pattern rejeita digest inválido")
    )
    results.append(
        check({"format": "date-time"}, "2026-07-26T18:00:00-03:00", valid=True,
              name="date-time aceita ISO-8601")
    )
    results.append(
        check({"format": "date-time"}, "26/07/2026", valid=False,
              name="date-time rejeita formato local")
    )

    # --- números ------------------------------------------------------------
    results.append(check({"minimum": 9.5}, 9.49, valid=False, name="minimum rejeita 9,49"))
    results.append(check({"minimum": 9.5}, 9.5, valid=True, name="minimum aceita o corte exato"))
    results.append(check({"maximum": 10}, 11, valid=False, name="maximum rejeita acima"))
    results.append(
        check({"exclusiveMaximum": 9.5}, 9.5, valid=False,
              name="exclusiveMaximum rejeita o próprio limite")
    )
    results.append(
        check({"exclusiveMaximum": 9.5}, 9.49, valid=True,
              name="exclusiveMaximum aceita abaixo")
    )

    # --- listas -------------------------------------------------------------
    results.append(check({"minItems": 2}, [1], valid=False, name="minItems rejeita curta"))
    results.append(check({"maxItems": 1}, [1, 2], valid=False, name="maxItems rejeita longa"))
    results.append(
        check({"uniqueItems": True}, [{"a": 1}, {"a": 1}], valid=False,
              name="uniqueItems rejeita duplicata estrutural")
    )
    results.append(
        check({"uniqueItems": True}, [{"a": 1}, {"a": 2}], valid=True,
              name="uniqueItems aceita itens distintos")
    )
    results.append(
        check({"items": {"type": "integer"}}, [1, "x"], valid=False,
              name="items valida cada elemento")
    )
    results.append(
        check({"contains": {"pattern": "R6"}, "minContains": 1}, ["R6 nomeado"], valid=True,
              name="contains encontra o item exigido")
    )
    results.append(
        check({"contains": {"pattern": "R6"}, "minContains": 1}, ["outro"], valid=False,
              name="contains rejeita lista sem o item")
    )
    results.append(
        check({"contains": {"const": "a"}, "minContains": 1, "maxContains": 1},
              ["a", "a"], valid=False, name="maxContains rejeita repetição")
    )

    # --- objetos ------------------------------------------------------------
    results.append(
        check({"required": ["a"]}, {"b": 1}, valid=False, name="required exige a chave")
    )
    results.append(
        check({"properties": {"a": {"type": "integer"}}, "additionalProperties": False},
              {"a": 1, "b": 2}, valid=False, name="additionalProperties false rejeita extra")
    )
    results.append(
        check({"properties": {"a": {"type": "integer"}}, "additionalProperties": False},
              {"a": 1}, valid=True, name="additionalProperties false aceita declarada")
    )

    # --- combinadores -------------------------------------------------------
    one_of = {"oneOf": [{"type": "integer"}, {"type": "string"}]}
    results.append(check(one_of, 1, valid=True, name="oneOf aceita exatamente uma"))
    results.append(check(one_of, None, valid=False, name="oneOf rejeita nenhuma"))
    ambiguous = {"oneOf": [{"minimum": 0}, {"maximum": 10}]}
    results.append(check(ambiguous, 5, valid=False, name="oneOf rejeita duas alternativas"))

    all_of = {"allOf": [{"minimum": 0}, {"maximum": 10}]}
    results.append(check(all_of, 5, valid=True, name="allOf aceita quando todas passam"))
    results.append(check(all_of, 11, valid=False, name="allOf rejeita quando uma falha"))

    conditional = {
        "if": {"properties": {"v": {"const": "X"}}, "required": ["v"]},
        "then": {"required": ["motivo"]},
        "else": {"required": ["nota"]},
    }
    results.append(
        check(conditional, {"v": "X", "motivo": "ok"}, valid=True, name="then aplica no ramo certo")
    )
    results.append(
        check(conditional, {"v": "X"}, valid=False, name="then cobra o campo do ramo")
    )
    results.append(
        check(conditional, {"v": "Y", "nota": 10}, valid=True, name="else aplica no outro ramo")
    )
    results.append(
        check(conditional, {"v": "Y"}, valid=False, name="else cobra o campo do outro ramo")
    )

    results.append(check({"not": {"const": "n/a"}}, "real", valid=True, name="not aceita diferente"))
    results.append(check({"not": {"const": "n/a"}}, "n/a", valid=False, name="not rejeita proibido"))

    # --- $ref ---------------------------------------------------------------
    with_ref = {"$defs": {"id": {"type": "string", "minLength": 3}}, "$ref": "#/$defs/id"}
    results.append(check(with_ref, "abc", valid=True, name="$ref local resolve"))
    results.append(check(with_ref, "ab", valid=False, name="$ref local aplica a restrição"))
    results.append(
        check({"$ref": "https://exemplo/x.json"}, "abc", valid=False,
              name="$ref externo é recusado, não ignorado")
    )

    # --- utilitários --------------------------------------------------------
    pointer_root = {"$defs": {"a/b": {"ok": True}}}
    try:
        pointed = json_pointer(pointer_root, "#/$defs/a~1b")
        results.append(("json_pointer decodifica ~1", pointed == {"ok": True}))
    except Exception:
        results.append(("json_pointer decodifica ~1", False))

    nested = {"x": {"y": {"properties": {"producer": {"const": "departamento-juizes"}}}}}
    results.append(
        ("find_const acha em profundidade",
         find_const(nested, "producer", "departamento-juizes"))
    )
    results.append(
        ("find_const não inventa achado",
         not find_const(nested, "producer", "ceo-maestro"))
    )

    names: set[str] = set()
    collect_property_names(
        {"properties": {"a": {}}, "z": [{"properties": {"b": {}}}]}, names
    )
    results.append(("collect_property_names percorre listas", names == {"a", "b"}))

    results.append(("is_type trata booleano fora de integer", not is_type(True, "integer")))

    # --- limites declarados do motor ---------------------------------------
    # Palavra-chave não suportada é IGNORADA. O teste existe para que a lacuna
    # seja visível e intencional, nunca uma surpresa em produção.
    results.append(
        check({"anyOf": [{"type": "integer"}]}, "texto", valid=True,
              name="LIMITE: anyOf é ignorado (não suportado)")
    )
    results.append(
        check({"multipleOf": 2}, 3, valid=True,
              name="LIMITE: multipleOf é ignorado (não suportado)")
    )
    results.append(
        check({"exclusiveMinimum": 5}, 5, valid=True,
              name="LIMITE: exclusiveMinimum é ignorado (não suportado)")
    )

    # --- verificações de pacote: unicidade da série global de ADR -----------
    results.extend(adr_series_results())

    # --- identidade de árvore: a receita tem de ser reproduzível ------------
    results.extend(digest_de_arvore_results())

    # --- ADR-025: a allowlist do frontmatter prova que é allowlist ----------
    results.extend(frontmatter_allowlist_results())
    results.extend(base_do_candidato_results())
    results.extend(sondas_e_evidencias_results())

    failures = 0
    for name, passed in results:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        if not passed:
            failures += 1

    print(f"\nResultado: {len(results) - failures}/{len(results)} casos passaram.")
    return 1 if failures else 0


def frontmatter_allowlist_results() -> list[tuple[str, bool]]:
    """A allowlist do ADR-025 e uma ALLOWLIST -- casos, nao prosa (tarefa 86).

    A assimetria que estes casos fecham foi medida em 2026-08-11 pelo proprio
    executor da canonizacao: REVERTER o ADR-025 e auto-detectavel, porque os
    `SKILL.md` que declaram `allowed-tools` ficariam vermelhos na hora. Mas
    AFROUXA-LO -- passar a ignorar chave desconhecida -- nao era pego por NADA:
    este motor devolvia o mesmo numero com o modulo canonizado e com o mutante,
    porque nao havia UM caso sobre frontmatter aqui.

    O comentario de `CHAVES_FRONTMATTER_OPCIONAIS` promete, em prosa, que "campo
    desconhecido no frontmatter segue sendo erro". Prosa nao reprova; estes casos
    reprovam.

    Chamam `chaves_do_frontmatter_conferem`, a funcao de PRODUCAO extraida na
    tarefa 86 -- nao uma copia da comparacao. Testar a copia mediria a
    reimplementacao, e mutar a de producao deixaria tudo verde.
    """
    from _compartilhado.verificacoes_pacote import (
        chaves_do_frontmatter_conferem as confere,
        _AMOSTRAS_DO_FRONTMATTER,
    )
    resultados: list[tuple[str, bool]] = []
    for rotulo, chaves, deve_reprovar in _AMOSTRAS_DO_FRONTMATTER:
        passou = confere(chaves)
        resultados.append((
            "FRONTMATTER (ADR-025): %s -> %s" % (
                rotulo, "reprova" if deve_reprovar else "passa"),
            passou is not deve_reprovar,
        ))
    return resultados



def base_do_candidato_results() -> list[tuple[str, bool]]:
    """T103: a conferência de base do candidato sabe distinguir viva de morta.

    Sem isto, `conferir_base_do_candidato` é código que ninguém executa até o
    dia em que alguém promove um overlay de dezenove dias por cima de oito
    travas novas — que foi exatamente o que a tarefa 46 quase fez.
    """
    from verificacoes_pacote import (
        _AMOSTRAS_DA_BASE,
        _autoteste_da_base_do_candidato,
        promocao_e_segura,
        travas_que_o_overlay_apagaria,
    )

    resultados: list[tuple[str, bool]] = []
    resultados.append((
        "base do candidato: o autoteste da produção não acusa nada",
        not _autoteste_da_base_do_candidato(),
    ))
    for nome, arquivos, mapa, espera_erro in _AMOSTRAS_DA_BASE:
        obtido = bool(promocao_e_segura(arquivos, lambda a, m=mapa: m.get(a)))
        resultados.append(("base do candidato: %s" % nome, obtido == espera_erro))
    resultados.append((
        "overlay que apaga trava é nomeado, e o que acrescenta não é",
        travas_que_o_overlay_apagaria("X Y", "X", ("X", "Y")) == ["Y"]
        and not travas_que_o_overlay_apagaria("X", "X Y", ("X", "Y")),
    ))
    return resultados

def sondas_e_evidencias_results() -> list[tuple[str, bool]]:
    """T104: o detector de sonda duplicada e de evidência que não discrimina.

    As amostras são SINTÉTICAS por necessidade: com os três refinos, os 16
    pacotes vivos têm ZERO ocorrências, e árvore sem o caso não mata mutante.
    O espécime REAL — o par antes/depois da sanação da tarefa 14 — está medido
    no adendo, com a receita para reexecutar.
    """
    from verificacoes_pacote import (
        _AMOSTRAS_DA_SONDA,
        _autoteste_das_sondas,
        evidencias_que_nao_discriminam,
        sondas_duplicadas_em_casos,
    )

    resultados: list[tuple[str, bool]] = [(
        "sondas: o autoteste da produção não acusa nada",
        not _autoteste_das_sondas(),
    )]
    for nome, fonte, espera in _AMOSTRAS_DA_SONDA:
        resultados.append(
            ("sonda duplicada: %s" % nome,
             bool(sondas_duplicadas_em_casos(fonte)) == espera)
        )
    resultados.append((
        "evidência repetida entre casos é contada, distinta não é",
        evidencias_que_nao_discriminam(["a", "a", "b"]) == {"a": 2}
        and not evidencias_que_nao_discriminam(["a", "b", "c"]),
    ))
    resultados.append((
        "evidência vazia não é repetição, e lista vazia não é conformidade",
        not evidencias_que_nao_discriminam(["", "  ", ""])
        and not evidencias_que_nao_discriminam([]),
    ))
    return resultados

if __name__ == "__main__":
    sys.exit(run())

